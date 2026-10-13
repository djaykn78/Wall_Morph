"""Streamlit integration app for Interactive Wall Visualization and Redesigning System.

Run from this folder with: streamlit run app.py
All image processing uses OpenCV BGR arrays internally; Streamlit displays RGB.
"""
from __future__ import annotations

import copy
import hashlib
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from design_database import (
    get_designs, get_design, get_object_types, get_wall_colours,
    get_wallpapers, get_textures, resolve_asset_path,
)
from detection import detect_objects
from image_processing import (
    apply_wall_color, apply_wall_wallpaper, apply_wall_texture,
    create_polygon_mask, exclude_objects_from_mask, apply_wall_wallpaper_perspective,
)
from manual_selection import (
    OBJECT_TYPES, add_manual_object, get_object_types as get_manual_object_types,
    remove_object, change_object_type, update_bounding_box,
)
from project_storage import list_projects, load_project, save_project, save_named_version, read_named_version
from transformations import (
    translate_object, scale_object, rotate_object, duplicate_object,
    bring_forward, send_backward, bring_to_front, send_to_back, get_corners,
)

st.set_page_config(page_title="Wall Visualization Studio", page_icon="🏡", layout="wide")
st.title("🏡 Interactive Wall Visualization & Redesigning System")
st.caption("Upload a room/wall image, detect or select objects, try replacement designs, and redesign the wall.")

# Local project dashboard. Projects and images remain on this computer.
with st.expander("📁 Projects · New, recent, and open", expanded=True):
    st.caption("Projects auto-save locally in the Wall_Project/projects folder. Each project contains one wall photo.")
    saved_projects = list_projects()
    if saved_projects:
        project_options = {f"{p['name']} · updated {p.get('updated','')}": p['id'] for p in saved_projects}
        chosen_project_label = st.selectbox("Recent projects", list(project_options), key="open_project_choice")
        pc1, pc2 = st.columns(2)
        if pc1.button("Open selected project", use_container_width=True):
            try:
                loaded = load_project(project_options[chosen_project_label])
                st.session_state.original = loaded["original"]
                st.session_state.canvas = loaded["canvas"]
                st.session_state.objects = loaded["objects"]
                st.session_state.history = loaded["history"]
                st.session_state.history_cursor = min(loaded["history_cursor"], len(loaded["history"])-1)
                st.session_state.project_name = loaded["name"]
                st.session_state.project_name_input = loaded["name"]
                st.session_state.named_versions = loaded.get("named_versions", [])
                st.session_state.selected_id = st.session_state.objects[0]["id"] if st.session_state.objects else None
                st.session_state.upload_signature = None
                st.session_state.upload_wall_image = None
                st.session_state.geometry_revision = int(st.session_state.get("geometry_revision", 0)) + 1
                st.success(f"Opened {loaded['name']}")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not open project: {exc}")
    else:
        st.info("No saved projects yet. Upload a photo to start; your work will auto-save after edits.")
    st.session_state.project_name = st.text_input("Project name", value=st.session_state.get("project_name", "My Wall Project"), key="project_name_input")


def decode_upload(uploaded_file):
    data = np.frombuffer(uploaded_file.getvalue(), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("This image could not be decoded. Try a PNG or JPG image.")
    return image


def read_asset(path):
    full = resolve_asset_path(path)
    if not Path(full).is_file():
        raise FileNotFoundError(f"Asset file is missing: {path}")
    asset = cv2.imread(full, cv2.IMREAD_UNCHANGED)
    if asset is None:
        raise ValueError(f"Could not read asset: {path}")
    return asset


def composite_design(canvas_bgr, asset_path, obj):
    """Render an asset using the current geometry, rotation, and optional perspective quad."""
    asset = read_asset(asset_path)
    if asset.ndim == 2:
        asset = cv2.cvtColor(asset, cv2.COLOR_GRAY2BGRA)
    elif asset.shape[2] == 3:
        asset = cv2.cvtColor(asset, cv2.COLOR_BGR2BGRA)
    ah, aw = asset.shape[:2]
    H, W = canvas_bgr.shape[:2]
    quad = obj.get("quad")
    if quad and len(quad) == 4:
        src = np.float32([[0, 0], [aw - 1, 0], [aw - 1, ah - 1], [0, ah - 1]])
        dst = np.float32(quad)
        transform = cv2.getPerspectiveTransform(src, dst)
        warped = cv2.warpPerspective(asset, transform, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        alpha = warped[:, :, 3:4].astype(np.float32) / 255.0
        base = canvas_bgr.astype(np.float32)
        rgb = warped[:, :, :3].astype(np.float32)
        out = rgb * alpha + base * (1.0 - alpha)
        return np.clip(out, 0, 255).astype(np.uint8)
    rgba = cv2.cvtColor(asset, cv2.COLOR_BGRA2RGBA)
    overlay = Image.fromarray(rgba).resize((max(1, int(obj["width"])), max(1, int(obj["height"]))), Image.Resampling.LANCZOS)
    angle = float(obj.get("rotation", 0))
    if angle:
        overlay = overlay.rotate(-angle, expand=True, resample=Image.Resampling.BICUBIC)
    base = Image.fromarray(cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGBA))
    x, y = int(obj["x"]), int(obj["y"])
    x -= (overlay.width - int(obj["width"])) // 2
    y -= (overlay.height - int(obj["height"])) // 2
    base.alpha_composite(overlay, (x, y))
    return cv2.cvtColor(np.array(base.convert("RGB")), cv2.COLOR_RGB2BGR)


def render_scene(base_image, objects):
    """Render registered object designs from current object geometry over the wall canvas."""
    out = base_image.copy()
    for obj in objects:
        design_id = obj.get("design")
        if not design_id:
            continue
        design = get_design(design_id)
        if design:
            try:
                out = composite_design(out, design["path"], obj)
            except (FileNotFoundError, ValueError) as exc:
                # Keep the rest of the scene visible if one optional asset is broken.
                log_message = f"Could not render {design_id}: {exc}"
                st.warning(log_message)
    return out


def render_object_boxes(image, objects):
    """Draw visible, rotation-aware object outlines and labels."""
    out = image.copy()
    for obj in objects:
        color = (45, 190, 90) if obj.get("source") == "automatic" else (30, 150, 240)
        corners = np.round(obj.get("quad") if obj.get("quad") and len(obj["quad"]) == 4 else get_corners(obj)).astype(np.int32)
        cv2.polylines(out, [corners], True, color, 2, cv2.LINE_AA)
        if obj.get("quad") and len(obj["quad"]) == 4:
            for px, py in corners:
                cv2.circle(out, (int(px), int(py)), 5, color, -1, cv2.LINE_AA)
        label = f'{obj.get("type", "object")} #{obj.get("id", "?")} · {int(obj.get("rotation", 0))}°'
        anchor_x = int(max(0, min(corners[:, 0].min(), out.shape[1] - 1)))
        anchor_y = int(max(18, min(corners[:, 1].min() - 6, out.shape[0] - 2)))
        cv2.putText(out, label, (anchor_x, anchor_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2, cv2.LINE_AA)
    return out


def push_snapshot():
    """Save the current edit state to undo history, trimming redo states."""
    # Refresh geometry widget keys on the next rerun so controls never show stale values.
    st.session_state.geometry_revision = int(st.session_state.get("geometry_revision", 0)) + 1
    state = {"image": st.session_state.canvas.copy(), "objects": copy.deepcopy(st.session_state.objects)}
    history = st.session_state.history
    cursor = st.session_state.history_cursor
    history = history[: cursor + 1]
    history.append(state)
    if len(history) > 30:
        history = history[-30:]
    st.session_state.history = history
    st.session_state.history_cursor = len(history) - 1


def restore_snapshot(index):
    snap = st.session_state.history[index]
    st.session_state.canvas = snap["image"].copy()
    st.session_state.objects = copy.deepcopy(snap["objects"])
    st.session_state.history_cursor = index


def reset_state(image):
    st.session_state.original = image.copy()
    st.session_state.canvas = image.copy()
    st.session_state.objects = []
    st.session_state.history = [{"image": image.copy(), "objects": []}]
    st.session_state.history_cursor = 0
    st.session_state.wall_points = ""
    st.session_state.selected_id = None
    st.session_state.geometry_revision = int(st.session_state.get("geometry_revision", 0)) + 1


def clamp_object_to_image(obj, image_width, image_height):
    """Keep object geometry valid even when a detector returns off-image boxes."""
    item = copy.deepcopy(obj)
    width = max(1, min(int(round(float(item.get("width", 1)))), image_width))
    height = max(1, min(int(round(float(item.get("height", 1)))), image_height))
    x = int(round(float(item.get("x", 0))))
    y = int(round(float(item.get("y", 0))))
    item["width"], item["height"] = width, height
    item["x"] = max(0, min(x, image_width - width))
    item["y"] = max(0, min(y, image_height - height))
    item.setdefault("rotation", 0)
    item.setdefault("scale", 1.0)
    item.setdefault("design", None)
    return item


def set_object_geometry(objects, object_id, *, x=None, y=None, width=None, height=None, image_width, image_height):
    """Update one object's geometry while guaranteeing it remains inside the image."""
    updated = copy.deepcopy(objects)
    for index, obj in enumerate(updated):
        if obj.get("id") == object_id:
            candidate = copy.deepcopy(obj)
            if x is not None: candidate["x"] = int(x)
            if y is not None: candidate["y"] = int(y)
            if width is not None: candidate["width"] = int(width)
            if height is not None: candidate["height"] = int(height)
            candidate["width"] = max(1, min(int(candidate["width"]), image_width))
            candidate["height"] = max(1, min(int(candidate["height"]), image_height))
            candidate["x"] = max(0, min(int(candidate["x"]), image_width - candidate["width"]))
            candidate["y"] = max(0, min(int(candidate["y"]), image_height - candidate["height"]))
            if candidate.get("quad"):
                sx = candidate["width"] / max(1, int(obj["width"]))
                sy = candidate["height"] / max(1, int(obj["height"]))
                dx = candidate["x"] - float(obj["x"]); dy = candidate["y"] - float(obj["y"])
                candidate["quad"] = [[candidate["x"] + (float(px)-float(obj["x"])) * sx, candidate["y"] + (float(py)-float(obj["y"])) * sy] for px, py in obj["quad"]]
            updated[index] = candidate
            break
    return updated


def set_object_rotation(objects, object_id, angle):
    updated = copy.deepcopy(objects)
    for obj in updated:
        if obj.get("id") != object_id: continue
        old = float(obj.get("rotation", 0)); new = float(angle) % 360
        if obj.get("quad"):
            cx = float(obj["x"]) + float(obj["width"]) / 2
            cy = float(obj["y"]) + float(obj["height"]) / 2
            delta = np.radians(new - old); c, sn = np.cos(delta), np.sin(delta)
            points=[]
            for px, py in obj["quad"]:
                dx, dy = float(px)-cx, float(py)-cy
                points.append([cx + dx*c - dy*sn, cy + dx*sn + dy*c])
            obj["quad"] = points
        obj["rotation"] = new
    return updated


uploaded = st.file_uploader("Upload a wall or room image", type=["png", "jpg", "jpeg", "webp"], key="upload_wall_image")
if uploaded is not None:
    upload_bytes = uploaded.getvalue()
    upload_signature = (uploaded.name, len(upload_bytes), hashlib.sha256(upload_bytes).hexdigest())
    if st.session_state.get("upload_signature") != upload_signature:
        try:
            reset_state(decode_upload(uploaded))
            st.session_state.upload_signature = upload_signature
        except Exception as exc:
            st.error(str(exc))
            st.stop()

if "geometry_revision" not in st.session_state:
    st.session_state.geometry_revision = 0
if "named_versions" not in st.session_state:
    st.session_state.named_versions = []

if "canvas" not in st.session_state:
    st.info("Upload an image to begin. Your image stays in this Streamlit session; it is not uploaded to an external design service by this app.")
    st.stop()

original = st.session_state.original
h, w = original.shape[:2]
st.caption(f"Image size: {w} × {h} pixels · Green boxes are automatically detected; orange boxes are manually added.")

left, right = st.columns([1.05, 1])
with left:
    st.subheader("Original image")
    st.image(cv2.cvtColor(original, cv2.COLOR_BGR2RGB), use_container_width=True)
with right:
    st.subheader("Current design")
    st.image(cv2.cvtColor(render_object_boxes(render_scene(st.session_state.canvas, st.session_state.objects), st.session_state.objects), cv2.COLOR_BGR2RGB), use_container_width=True)

st.divider()
# Object detection and management
st.header("1. Detect and manage objects")
c1, c2, c3 = st.columns([1.2, 1, 1])
with c1:
    backend = st.selectbox("Detection model", ["dino", "dino_tiny", "yoloworld", "coco", "ensemble"], index=0,
                           help="Models may download weights on first use. If dependencies or model access are unavailable, add objects manually.")
with c2:
    confidence = st.slider("Confidence threshold", 0.10, 0.80, 0.25, 0.05)
with c3:
    if st.button("🔎 Detect objects", type="primary", use_container_width=True):
        try:
            with st.spinner("Detecting objects. First run may take a while while model weights load..."):
                found = detect_objects(original, confidence_threshold=confidence, backend=backend, fallback=True)
        except Exception as exc:
            found = []
            st.error(f"Object detection could not complete: {exc}. You can still add or edit objects manually.")
        if found:
            # Assign fresh IDs in a predictable manner; preserve the common object schema.
            for i, obj in enumerate(found, start=1):
                obj["id"] = i
                obj.setdefault("rotation", 0); obj.setdefault("scale", 1.0); obj.setdefault("design", None)
                found[i - 1] = clamp_object_to_image(obj, w, h)
            st.session_state.objects = found
            st.session_state.selected_id = found[0]["id"] if found else None
            st.session_state.geometry_revision = int(st.session_state.get("geometry_revision", 0)) + 1
            st.session_state.canvas = original.copy()
            st.session_state.history = [{"image": original.copy(), "objects": copy.deepcopy(found)}]
            st.session_state.history_cursor = 0
            st.success(f"Detected {len(found)} object(s). You can edit boxes and replace supported categories below.")
        else:
            st.warning("No objects were returned. The model may have failed to load, or no objects passed the threshold. Try another backend or add an object manually.")

objects = st.session_state.objects
if objects:
    st.dataframe([{"ID": o["id"], "Type": o["type"], "Source": o.get("source", "unknown"),
                   "Confidence": o.get("confidence"), "X": o["x"], "Y": o["y"],
                   "Width": o["width"], "Height": o["height"]} for o in objects], use_container_width=True, hide_index=True)
else:
    st.write("No objects yet. Run detection or add one manually.")

with st.expander("Add an object manually", expanded=not bool(objects)):
    type_options = get_manual_object_types(objects=objects, extra_types=get_object_types(include_empty=True))
    st.markdown("**Mark the object using four corner points**")
    st.caption("Choose the object type, then click the four corners of the object on the image below. The app creates a bounding box around those points.")
    point_type = st.selectbox("Object type for four-point selection", type_options, key="manual_point_type")
    try:
        from streamlit_drawable_canvas import st_canvas
        point_width = min(850, w)
        point_height = max(240, int(h * point_width / w))
        point_preview = cv2.resize(original, (point_width, point_height), interpolation=cv2.INTER_AREA if point_width < w else cv2.INTER_LINEAR)
        point_result = st_canvas(
            background_image=Image.fromarray(cv2.cvtColor(point_preview, cv2.COLOR_BGR2RGB)),
            drawing_mode="point", point_display_radius=7, stroke_width=3,
            stroke_color="#FF8C00", height=point_height, width=point_width,
            update_streamlit=True, key="manual_object_four_points",
        )
        point_objects = (point_result.json_data or {}).get("objects", []) if point_result else []
        points = []
        for pobj in point_objects:
            if pobj.get("type") in ("circle", "point"):
                # Try to get center coordinates robustly
                cx, cy = None, None
                if "x" in pobj and "y" in pobj:
                    # Assume x,y are center coordinates
                    cx = float(pobj["x"])
                    cy = float(pobj["y"])
                elif "left" in pobj and "top" in pobj:
                    left = float(pobj["left"])
                    top = float(pobj["top"])
                    if "radius" in pobj:
                        # Assume left,top is top-left of bounding box, radius is circle radius
                        cx = left + float(pobj["radius"])
                        cy = top + float(pobj["radius"])
                    elif "width" in pobj and "height" in pobj:
                        # Assume left,top is top-left, width/height are dimensions
                        cx = left + float(pobj["width"]) / 2.0
                        cy = top + float(pobj["height"]) / 2.0
                    else:
                        # Fallback: assume left,top are already center coordinates
                        cx = left
                        cy = top
                if cx is not None and cy is not None:
                    points.append((cx, cy))
        st.caption(f"Corner points marked: {len(points)} / 4")
        if len(points) == 4:
            xs = [p[0] for p in points]; ys = [p[1] for p in points]
            px1 = max(0, min(w - 1, int(round(min(xs) * w / point_width))))
            py1 = max(0, min(h - 1, int(round(min(ys) * h / point_height))))
            px2 = min(w, max(px1 + 1, int(round(max(xs) * w / point_width))))
            py2 = min(h, max(py1 + 1, int(round(max(ys) * h / point_height))))
            st.image(cv2.cvtColor(render_object_boxes(original, [{"id": "preview", "type": point_type, "x": px1, "y": py1, "width": px2-px1, "height": py2-py1, "rotation": 0, "source": "manual"}]), cv2.COLOR_BGR2RGB), caption="Preview of the selected object box", use_container_width=True)
            if st.button("Add object from four points", key="add_four_point_object", type="primary"):
                try:
                    updated = add_manual_object(st.session_state.objects, point_type, px1, py1, px2-px1, py2-py1, image_size=(w, h))
                    # Preserve the actual four-corner perspective, not only its axis-aligned bounds.
                    quad_points = [[float(px) * w / point_width, float(py) * h / point_height] for px, py in points]
                    center = np.mean(np.asarray(quad_points), axis=0)
                    quad_points = sorted(quad_points, key=lambda p: np.arctan2(p[1]-center[1], p[0]-center[0]))
                    # Rotate order to start at the top-left-most corner for stable mapping.
                    first = min(range(4), key=lambda i: quad_points[i][0] + quad_points[i][1])
                    quad_points = quad_points[first:] + quad_points[:first]
                    updated[-1]["quad"] = quad_points
                    st.session_state.objects = updated
                    st.session_state.selected_id = updated[-1]["id"]
                    push_snapshot(); st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    except ImportError:
        st.warning("Four-point selection requires streamlit-drawable-canvas. Install it with: python -m pip install streamlit-drawable-canvas")
    st.divider()
    st.markdown("**Alternative: enter the box coordinates manually**")
    with st.form("manual_add_form"):
        new_type = st.selectbox("Object category", type_options + (["new category…"] if "new category…" not in type_options else []))
        custom_type = st.text_input("New category name (if selected)", placeholder="e.g. sofa, mirror, wardrobe") if new_type == "new category…" else ""
        a, b, c, d = st.columns(4)
        x = a.number_input("X", min_value=0, max_value=max(0, w - 1), value=0)
        y = b.number_input("Y", min_value=0, max_value=max(0, h - 1), value=0)
        bw = c.number_input("Width", min_value=1, max_value=w, value=max(1, min(w // 4, 250)))
        bh = d.number_input("Height", min_value=1, max_value=h, value=max(1, min(h // 4, 180)))
        add_clicked = st.form_submit_button("Add object")
    if add_clicked:
        category = custom_type.strip().lower() if new_type == "new category…" else new_type
        try:
            updated = add_manual_object(objects, category, x, y, bw, bh, image_size=(w, h))
            st.session_state.objects = updated
            st.session_state.selected_id = updated[-1]["id"]
            push_snapshot()
            st.success(f"Added {category}.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

# Object edit panel
if st.session_state.objects:
    st.subheader("Select and edit an object")
    id_options = [o["id"] for o in st.session_state.objects]
    default_index = id_options.index(st.session_state.selected_id) if st.session_state.selected_id in id_options else 0
    selected_id = st.selectbox("Object to edit", id_options, index=default_index,
        format_func=lambda oid: f"#{oid} — {next((o['type'] for o in st.session_state.objects if o['id'] == oid), 'object')}")
    st.session_state.selected_id = selected_id
    selected = next(o for o in st.session_state.objects if o["id"] == selected_id)

    st.markdown("**Position and size**")
    with st.form(f"geometry_form_{selected_id}"):
        p1, p2, p3, p4 = st.columns(4)
        edit_x = p1.number_input("X position", min_value=0, max_value=max(0, w - int(selected["width"])), value=max(0, min(w - int(selected["width"]), int(selected["x"]))), key=f"x_{selected_id}_{st.session_state.geometry_revision}", help="Pixels from the left edge.")
        edit_y = p2.number_input("Y position", min_value=0, max_value=max(0, h - int(selected["height"])), value=max(0, min(h - int(selected["height"]), int(selected["y"]))), key=f"y_{selected_id}_{st.session_state.geometry_revision}", help="Pixels from the top edge.")
        edit_w = p3.number_input("Width", min_value=1, max_value=w, value=max(1, min(w, int(selected["width"]))), key=f"w_{selected_id}_{st.session_state.geometry_revision}")
        edit_h = p4.number_input("Height", min_value=1, max_value=h, value=max(1, min(h, int(selected["height"]))), key=f"h_{selected_id}_{st.session_state.geometry_revision}")
        geometry_submit = st.form_submit_button("Apply position and size", type="primary", use_container_width=True)
    if geometry_submit:
        st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, x=edit_x, y=edit_y, width=edit_w, height=edit_h, image_width=w, image_height=h)
        push_snapshot()
        st.rerun()

    # One-click controls make the common edits discoverable and immediately visible.
    st.markdown("**Quick resize**")
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("＋ Height", key=f"height_plus_{selected_id}", use_container_width=True):
        st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, height=min(h, int(selected["height"]) + max(5, int(h * 0.03))), image_width=w, image_height=h)
        push_snapshot(); st.rerun()
    if q2.button("− Height", key=f"height_minus_{selected_id}", use_container_width=True):
        st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, height=max(1, int(selected["height"]) - max(5, int(h * 0.03))), image_width=w, image_height=h)
        push_snapshot(); st.rerun()
    if q3.button("＋ Width", key=f"width_plus_{selected_id}", use_container_width=True):
        st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, width=min(w, int(selected["width"]) + max(5, int(w * 0.03))), image_width=w, image_height=h)
        push_snapshot(); st.rerun()
    if q4.button("− Width", key=f"width_minus_{selected_id}", use_container_width=True):
        st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, width=max(1, int(selected["width"]) - max(5, int(w * 0.03))), image_width=w, image_height=h)
        push_snapshot(); st.rerun()

    b1, b2, b3, b4, b5 = st.columns(5)
    if b1.button("Duplicate", use_container_width=True):
        duplicate = duplicate_object(selected, st.session_state.objects)
        duplicate = clamp_object_to_image(duplicate, w, h)
        st.session_state.objects = [*st.session_state.objects, duplicate]
        st.session_state.selected_id = duplicate["id"]
        push_snapshot(); st.rerun()
    if b2.button("Delete", use_container_width=True):
        st.session_state.objects = remove_object(st.session_state.objects, selected_id)
        st.session_state.selected_id = st.session_state.objects[0]["id"] if st.session_state.objects else None
        push_snapshot(); st.rerun()
    if b3.button("Bring forward", use_container_width=True):
        st.session_state.objects = bring_forward(st.session_state.objects, selected_id); push_snapshot(); st.rerun()
    if b4.button("Send backward", use_container_width=True):
        st.session_state.objects = send_backward(st.session_state.objects, selected_id); push_snapshot(); st.rerun()
    if b5.button("Center object", use_container_width=True):
        st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, x=(w-int(selected["width"]))//2, y=(h-int(selected["height"]))//2, image_width=w, image_height=h)
        push_snapshot(); st.rerun()

    move_col, scale_col = st.columns(2)
    with move_col:
        st.markdown("**Move object**")
        mdx, mdy = st.columns(2)
        dx = mdx.number_input("Horizontal move (px)", min_value=-w, max_value=w, value=20, key=f"dx_{selected_id}_{st.session_state.geometry_revision}")
        dy = mdy.number_input("Vertical move (px)", min_value=-h, max_value=h, value=0, key=f"dy_{selected_id}_{st.session_state.geometry_revision}")
        if st.button("Move object", key=f"move_{selected_id}", use_container_width=True):
            st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, x=int(selected["x"])+int(dx), y=int(selected["y"])+int(dy), image_width=w, image_height=h)
            push_snapshot(); st.rerun()
    with scale_col:
        st.markdown("**Scale object**")
        factor = st.slider("Scale factor", 0.2, 3.0, 1.5, 0.1, key=f"scale_{selected_id}_{st.session_state.geometry_revision}")
        if st.button("Apply scale", key=f"scale_btn_{selected_id}", use_container_width=True):
            new_w = max(1, min(w, int(round(selected["width"] * factor))))
            new_h = max(1, min(h, int(round(selected["height"] * factor))))
            cx = float(selected["x"]) + float(selected["width"]) / 2
            cy = float(selected["y"]) + float(selected["height"]) / 2
            st.session_state.objects = set_object_geometry(st.session_state.objects, selected_id, x=round(cx-new_w/2), y=round(cy-new_h/2), width=new_w, height=new_h, image_width=w, image_height=h)
            push_snapshot(); st.rerun()

    st.markdown("**Replacement design**")
    available = get_designs(selected.get("type", ""))
    if available:
        labels = {d["id"]: d["name"] for d in available}
        design_id = st.selectbox("Design for selected object", list(labels), format_func=lambda key: labels[key])
        preview_col, apply_col = st.columns([1, 2])
        with preview_col:
            try:
                st.image(resolve_asset_path(get_design(design_id)["path"]), caption=labels[design_id], use_container_width=True)
            except Exception as exc: st.warning(f"Preview unavailable: {exc}")
        with apply_col:
            if st.button("Apply replacement design", type="primary"):
                try:
                    # Store the selected design on the object. Rendering is derived from
                    # the current geometry, so later moves/resizes/rotation stay in sync.
                    updated = copy.deepcopy(st.session_state.objects)
                    for item in updated:
                        if item["id"] == selected_id: item["design"] = design_id
                    st.session_state.objects = updated
                    push_snapshot(); st.success("Replacement design applied."); st.rerun()
                except Exception as exc: st.error(f"Could not apply design: {exc}")
    else:
        st.info(f"No replacement designs are registered for **{selected.get('type')}** yet. This category is supported in object management; add assets and register designs to enable replacement.")

    # Rotation is visible on the overlay even when no replacement asset is applied.
    st.markdown("**Rotate object**")
    rot_col, apply_rot_col, reset_rot_col = st.columns([2, 1, 1])
    current_angle = int(round(float(selected.get("rotation", 0))))
    angle = rot_col.slider("Angle (degrees)", -180, 180, max(-180, min(180, ((current_angle + 180) % 360) - 180)), 5, key=f"rot_{selected_id}_{st.session_state.geometry_revision}")
    if apply_rot_col.button("Apply angle", key=f"apply_rot_{selected_id}", use_container_width=True):
        st.session_state.objects = set_object_rotation(st.session_state.objects, selected_id, float(angle))
        push_snapshot(); st.rerun()
    if reset_rot_col.button("Reset angle", key=f"reset_rot_{selected_id}", use_container_width=True):
        st.session_state.objects = set_object_rotation(st.session_state.objects, selected_id, 0)
        push_snapshot(); st.rerun()

# Wall editing panel
st.divider()
st.header("2. Redesign the wall")
st.caption("By default, the finish is applied to the full image. For a wall-only result, turn off full-image mode and draw around the wall. Object boxes can be protected automatically; automatic semantic wall segmentation is not available in this build.")
use_full_image = st.checkbox("Apply to the full image (default)", value=st.session_state.get("use_full_image", True), key="use_full_image")
mask = None
if use_full_image:
    mask = np.full((h, w), 255, dtype=np.uint8)
    st.info("Full image selected. If the photo includes areas beyond the wall, turn this off and draw a rectangle around the wall area.")
else:
    try:
        from streamlit_drawable_canvas import st_canvas
        preview_width = min(850, w)
        preview_height = max(240, int(h * preview_width / w))
        preview = cv2.resize(original, (preview_width, preview_height), interpolation=cv2.INTER_AREA if preview_width < w else cv2.INTER_LINEAR)
        selection_method = st.radio("Wall selection method", ["Rectangle", "Four-corner perspective"], horizontal=True, key="wall_selection_method")
        if selection_method == "Rectangle":
            st.markdown("**Select wall area** — drag from one corner to the opposite corner.")
            canvas_result = st_canvas(fill_color="rgba(30, 144, 255, 0.12)", stroke_width=3, stroke_color="#1E90FF",
                background_image=Image.fromarray(cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)), update_streamlit=True,
                height=preview_height, width=preview_width, drawing_mode="rect", key="wall_area_canvas")
            canvas_objects = (canvas_result.json_data or {}).get("objects", []) if canvas_result else []
            rects = [item for item in canvas_objects if item.get("type") == "rect"]
            st.session_state.wall_quad = None
            if rects:
                rect = rects[-1]
                left_px = max(0, min(w - 1, int(round(float(rect.get("left", 0)) * w / preview_width))))
                top_px = max(0, min(h - 1, int(round(float(rect.get("top", 0)) * h / preview_height))))
                rect_w_canvas = float(rect.get("width", 0)) * float(rect.get("scaleX", 1))
                rect_h_canvas = float(rect.get("height", 0)) * float(rect.get("scaleY", 1))
                rect_w = max(1, min(w - left_px, int(round(rect_w_canvas * w / preview_width))))
                rect_h = max(1, min(h - top_px, int(round(rect_h_canvas * h / preview_height))))
                mask = np.zeros((h, w), dtype=np.uint8); mask[top_px:top_px + rect_h, left_px:left_px + rect_w] = 255
                st.caption(f"Selected area: {rect_w} × {rect_h} pixels.")
            else: st.warning("Draw a rectangle over the wall to enable applying the finish.")
        else:
            st.markdown("**Click the wall corners clockwise** (four points). The wallpaper will be perspective-mapped to this quadrilateral.")
            canvas_result = st_canvas(background_image=Image.fromarray(cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)), drawing_mode="point",
                point_display_radius=7, stroke_width=3, stroke_color="#1E90FF", update_streamlit=True,
                height=preview_height, width=preview_width, key="wall_four_corner_canvas")
            canvas_objects = (canvas_result.json_data or {}).get("objects", []) if canvas_result else []
            pts=[]
            for pobj in canvas_objects:
                if pobj.get("type") in ("circle", "point"):
                    # Try to get center coordinates robustly
                    cx, cy = None, None
                    if "x" in pobj and "y" in pobj:
                        # Assume x,y are center coordinates
                        cx = float(pobj["x"])
                        cy = float(pobj["y"])
                    elif "left" in pobj and "top" in pobj:
                        left = float(pobj["left"])
                        top = float(pobj["top"])
                        if "radius" in pobj:
                            # Assume left,top is top-left of bounding box, radius is circle radius
                            cx = left + float(pobj["radius"])
                            cy = top + float(pobj["radius"])
                        elif "width" in pobj and "height" in pobj:
                            # Assume left,top is top-left, width/height are dimensions
                            cx = left + float(pobj["width"]) / 2.0
                            cy = top + float(pobj["height"]) / 2.0
                        else:
                            # Fallback: assume left,top are already center coordinates
                            cx = left
                            cy = top
                    if cx is not None and cy is not None:
                        pts.append([cx * w / preview_width, cy * h / preview_height])
            st.caption(f"Wall corners marked: {len(pts)} / 4")
            if len(pts)==4:
                center=np.mean(np.asarray(pts),axis=0); pts=sorted(pts,key=lambda p:np.arctan2(p[1]-center[1],p[0]-center[0]))
                first=min(range(4),key=lambda i:pts[i][0]+pts[i][1]); pts=pts[first:]+pts[:first]
                st.session_state.wall_quad=pts
                mask=np.zeros((h,w),dtype=np.uint8); cv2.fillPoly(mask,[np.round(pts).astype(np.int32)],255)
            else:
                st.session_state.wall_quad=None
                st.warning("Mark four corners to enable the wall finish.")
    except ImportError:
        st.error("Visual wall selection needs streamlit-drawable-canvas. Install it with: python -m pip install streamlit-drawable-canvas")

exclude = st.checkbox("Protect detected/manual object areas", value=True, help="Subtract object boxes from the wall finish so doors, windows, and furniture are less likely to be recolored.")
if mask is not None and exclude and st.session_state.objects:
    mask = exclude_objects_from_mask(mask, st.session_state.objects)
if mask is not None and not np.any(mask):
    st.warning("The selected wall area is empty after protecting object areas. Adjust the selection or turn off object protection.")
    mask = None

wall_mode = st.radio("Wall finish", ["Solid color", "Wallpaper", "Texture"], horizontal=True)

if wall_mode == "Solid color":
    color_map = get_wall_colours()
    color_name = st.selectbox("Wall color", list(color_map))
    # Database RGB values are converted to BGR for OpenCV functions.
    rgb = color_map[color_name]
    wall_color_bgr = (int(rgb[2]), int(rgb[1]), int(rgb[0]))
elif wall_mode == "Wallpaper":
    wall_items = get_wallpapers()
    st.markdown("**Wallpaper gallery**")
    uploaded_wallpaper = st.file_uploader("Add your own wallpaper pattern (saved locally)", type=["png", "jpg", "jpeg", "webp"], key="custom_wallpaper_upload")
    if uploaded_wallpaper is not None:
        import re as _re
        user_wall_dir = Path(__file__).resolve().parent / "assets" / "user_wallpapers"
        user_wall_dir.mkdir(parents=True, exist_ok=True)
        safe_name = _re.sub(r"[^a-zA-Z0-9_-]+", "_", Path(uploaded_wallpaper.name).stem).strip("_-")[:60] or "custom_wallpaper"
        user_path = user_wall_dir / f"{safe_name}.png"
        if not user_path.exists():
            user_bytes = np.frombuffer(uploaded_wallpaper.getvalue(), dtype=np.uint8)
            user_img = cv2.imdecode(user_bytes, cv2.IMREAD_COLOR)
            if user_img is not None: cv2.imwrite(str(user_path), user_img)
        if user_path.exists():
            wall_items.append({"id": f"user_{safe_name}", "name": f"My design: {safe_name.replace('_',' ')}", "path": str(user_path)})
    # Previously uploaded wallpaper files persist in the project asset folder.
    user_wall_dir = Path(__file__).resolve().parent / "assets" / "user_wallpapers"
    if user_wall_dir.exists():
        for user_path in sorted(user_wall_dir.glob("*.png")):
            if not any(item["path"] == str(user_path) for item in wall_items):
                wall_items.append({"id": f"user_{user_path.stem}", "name": f"My design: {user_path.stem.replace('_',' ')}", "path": str(user_path)})
    wall_id = st.selectbox("Wallpaper", range(len(wall_items)), format_func=lambda i: wall_items[i]["name"])
    try:
        st.image(resolve_asset_path(wall_items[wall_id]["path"]), caption=f"Selected wallpaper: {wall_items[wall_id]['name']}", width=220)
    except Exception as exc:
        st.warning(f"Wallpaper preview unavailable: {exc}")
    wallpaper_opacity = st.slider("Wallpaper opacity", min_value=0.50, max_value=1.00, value=0.90, step=0.05,
                                  help="Higher opacity makes the wallpaper pattern and colors more visible.")
    wall_color_bgr = None
else:
    texture_items = get_textures()
    texture_id = st.selectbox("Texture", range(len(texture_items)), format_func=lambda i: texture_items[i]["name"])
    wall_color_bgr = None

if st.button("Apply wall finish", type="primary", disabled=mask is None or not np.any(mask)):
    try:
        if wall_mode == "Solid color":
            result = apply_wall_color(st.session_state.canvas, mask, wall_color_bgr)
        elif wall_mode == "Wallpaper":
            wallpaper = read_asset(wall_items[wall_id]["path"])
            if st.session_state.get("wall_quad") and not use_full_image:
                result = apply_wall_wallpaper_perspective(st.session_state.canvas, st.session_state.wall_quad, wallpaper, opacity=wallpaper_opacity)
            else:
                result = apply_wall_wallpaper(st.session_state.canvas, mask, wallpaper, opacity=wallpaper_opacity)
        else:
            texture = read_asset(texture_items[texture_id]["path"])
            result = apply_wall_texture(st.session_state.canvas, mask, texture)
        st.session_state.canvas = result
        push_snapshot(); st.success("Wall finish applied."); st.rerun()
    except Exception as exc:
        st.error(f"Could not apply wall finish: {exc}")

# History and export
st.divider()
st.header("3. History and export")
h1, h2, h3, h4 = st.columns(4)
with h1:
    if st.button("↶ Undo", disabled=st.session_state.history_cursor <= 0, use_container_width=True):
        restore_snapshot(st.session_state.history_cursor - 1); st.rerun()
with h2:
    if st.button("↷ Redo", disabled=st.session_state.history_cursor >= len(st.session_state.history) - 1, use_container_width=True):
        restore_snapshot(st.session_state.history_cursor + 1); st.rerun()
with h3:
    if st.button("Reset to original", use_container_width=True):
        st.session_state.confirm_reset = True
    if st.session_state.get("confirm_reset", False):
        st.warning("Reset all edits and objects for this session? The original photo will remain unchanged.")
        yes, no = st.columns(2)
        if yes.button("Confirm reset", key="confirm_reset_yes"):
            reset_state(st.session_state.original); st.session_state.confirm_reset = False; st.rerun()
        if no.button("Cancel reset", key="confirm_reset_no"):
            st.session_state.confirm_reset = False; st.rerun()
with h4:
    # Export the clean design without editor outlines or labels.
    rendered = render_scene(st.session_state.canvas, st.session_state.objects)
    ok, encoded = cv2.imencode(".png", rendered)
    if ok:
        st.download_button("Download PNG", data=encoded.tobytes(), file_name="wall_redesign.png", mime="image/png", use_container_width=True)

with st.expander("💾 Named versions and project recovery"):
    st.caption("The current edit state auto-saves. Named versions let you keep milestones before trying another design.")
    version_label = st.text_input("Version name", value="Before trying another design", key="version_label_input")
    if st.button("Save named version", key="save_named_version_button"):
        try:
            save_project(st.session_state.get("project_name", "My Wall Project"), st.session_state.original, st.session_state.canvas, st.session_state.objects, st.session_state.history, st.session_state.history_cursor)
            folder_id = save_named_version(st.session_state.get("project_name", "My Wall Project"), st.session_state.canvas, st.session_state.objects, st.session_state.original, version_label.strip() or None)
            if folder_id:
                st.session_state.named_versions.append({"name": version_label.strip() or folder_id, "saved": folder_id})
                st.success(f"Saved snapshot: {version_label or folder_id}")
            else:
                st.error("Save the project once before creating a named version.")
        except Exception as exc:
            st.error(f"Could not save named version: {exc}")
    try:
        project_folder = __import__("project_storage").PROJECT_ROOT / __import__("project_storage")._slug(st.session_state.get("project_name", "My Wall Project"))
        if (project_folder / "project.json").exists():
            import json as _json
            _meta = _json.loads((project_folder / "project.json").read_text(encoding="utf-8"))
            _versions = _meta.get("named_versions", [])
            if _versions:
                _labels = [v["name"] for v in _versions]
                _pick = st.selectbox("Saved versions", _labels, key="restore_version_choice")
                _v1, _v2 = st.columns(2)
                if _v1.button("Restore selected version", key="restore_named_version"):
                    _snapshot = read_named_version(st.session_state.get("project_name", "My Wall Project"), _pick)
                    st.session_state.canvas = _snapshot["image"]
                    st.session_state.objects = _snapshot["objects"]
                    push_snapshot(); st.rerun()
                if _v2.button("Compare with current", key="compare_named_version"):
                    _snapshot = read_named_version(st.session_state.get("project_name", "My Wall Project"), _pick)
                    _a, _b = st.columns(2)
                    _a.image(cv2.cvtColor(_snapshot["image"], cv2.COLOR_BGR2RGB), caption=f"Saved: {_pick}", use_container_width=True)
                    _b.image(cv2.cvtColor(render_scene(st.session_state.canvas, st.session_state.objects), cv2.COLOR_BGR2RGB), caption="Current", use_container_width=True)
    except Exception as exc:
        st.caption(f"Saved-version list is unavailable: {exc}")

# Auto-save after each successful rerun/edit. The untouched source photo is saved separately.
try:
    save_project(st.session_state.get("project_name", "My Wall Project"), st.session_state.original,
                 st.session_state.canvas, st.session_state.objects,
                 st.session_state.history, st.session_state.history_cursor,
                 st.session_state.get("named_versions", []))
except Exception as exc:
    st.warning(f"Project auto-save could not complete: {exc}")

with st.expander("Show current object boxes"):
    st.image(cv2.cvtColor(render_object_boxes(render_scene(st.session_state.canvas, st.session_state.objects), st.session_state.objects), cv2.COLOR_BGR2RGB), use_container_width=True)
