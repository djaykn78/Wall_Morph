"""
transformations.py  --  PERSON 4: Matrix Transformations & Object Manipulation
=============================================================================

Linear-algebra core of the Wall Visualization / Redesign application.

Common object format (shared by the whole team, DO NOT rename keys):

    {
        "id": 1, "type": "window",
        "x": 100, "y": 80,            # top-left corner of the object
        "width": 200, "height": 150,
        "rotation": 0,                # degrees, cumulative, about the centre
        "scale": 1.0,                 # cumulative scale factor (bookkeeping)
        "design": None, "confidence": 0.91, "source": "automatic"
    }

Conventions
-----------
* All public functions are PURE: they return a new object/list and never
  mutate their input.
* Scaling and rotation happen about the object's CENTRE
  (center_x = x + width/2, center_y = y + height/2).
* Scaling updates `width`/`height` (and moves x/y so the centre stays put).
  `scale` records the cumulative factor applied (informational for the UI).
* Rotation only updates `rotation`; the centre (x, y, width, height) is
  unchanged. Use `get_corners()` to get the rotated polygon for rendering.
* Image coordinates have y pointing DOWN, so a positive angle looks
  clockwise on screen.
* Layer order = list order: index 0 is the back, the last item is the front.

Dependencies: numpy only.
"""

import copy
import numpy as np

# ---------------------------------------------------------------------------
# 1. Homogeneous 3x3 matrix builders  (the "math" layer)
# ---------------------------------------------------------------------------

def translation_matrix(tx, ty):
    """[1 0 tx; 0 1 ty; 0 0 1]  ->  x' = x + tx, y' = y + ty"""
    return np.array([[1.0, 0.0, tx],
                     [0.0, 1.0, ty],
                     [0.0, 0.0, 1.0]])


def scaling_matrix(sx, sy=None):
    """[sx 0 0; 0 sy 0; 0 0 1]  ->  x' = sx*x, y' = sy*y  (about the origin)"""
    if sy is None:
        sy = sx
    return np.array([[sx, 0.0, 0.0],
                     [0.0, sy, 0.0],
                     [0.0, 0.0, 1.0]])


def rotation_matrix(angle_deg):
    """[cos -sin 0; sin cos 0; 0 0 1]  (about the origin, angle in degrees)"""
    t = np.radians(angle_deg)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0.0],
                     [s,  c, 0.0],
                     [0.0, 0.0, 1.0]])


def about_point(matrix, cx, cy):
    """
    Make `matrix` act about the point (cx, cy) instead of the origin:

        M_c = T(cx, cy) @ M @ T(-cx, -cy)

    Read right-to-left: move the centre to the origin, transform, move back.
    """
    return translation_matrix(cx, cy) @ matrix @ translation_matrix(-cx, -cy)


def compose(*matrices):
    """
    Combine transforms so that compose(A, B, C) @ p == A @ (B @ (C @ p)),
    i.e. the RIGHT-most matrix is applied FIRST.
    Matrix multiplication is order-dependent: T @ R != R @ T in general.
    """
    result = np.eye(3)
    for m in matrices:
        result = result @ m
    return result


def apply_matrix(matrix, points):
    """Apply a 3x3 matrix to an (N, 2) array of points -> (N, 2) array."""
    pts = np.asarray(points, dtype=float).reshape(-1, 2)
    homogeneous = np.hstack([pts, np.ones((len(pts), 1))])     # (N, 3)
    out = homogeneous @ matrix.T                               # (N, 3)
    return out[:, :2] / out[:, 2:3]                            # divide by w


# ---------------------------------------------------------------------------
# 2. Small helpers
# ---------------------------------------------------------------------------

def get_center(obj):
    """Centre of the object's (unrotated) bounding box."""
    return obj["x"] + obj["width"] / 2.0, obj["y"] + obj["height"] / 2.0


def get_corners(obj):
    """
    Four corners (TL, TR, BR, BL) of the object AFTER rotation, as an (4, 2)
    array. Handy for Person 6 when drawing / hit-testing.
    """
    x, y, w, h = obj["x"], obj["y"], obj["width"], obj["height"]
    cx, cy = get_center(obj)
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    m = about_point(rotation_matrix(obj.get("rotation", 0)), cx, cy)
    return apply_matrix(m, corners)


def get_bounding_box(obj):
    """Axis-aligned box (x_min, y_min, x_max, y_max) of the rotated object."""
    c = get_corners(obj)
    return (float(c[:, 0].min()), float(c[:, 1].min()),
            float(c[:, 0].max()), float(c[:, 1].max()))


def get_transform_matrix(obj):
    """
    Full local-to-image matrix for the object's current state:
    rotate about its centre. Useful for demos / viva.
    """
    cx, cy = get_center(obj)
    return about_point(rotation_matrix(obj.get("rotation", 0)), cx, cy)


def _clean(value):
    """Remove floating-point noise (e.g. 149.99999999 -> 150.0)."""
    return round(float(value), 6)


# ---------------------------------------------------------------------------
# 3. Core transformations on objects
# ---------------------------------------------------------------------------

def translate_object(object_data, dx, dy):
    """
    Move the object by (dx, dy) pixels using the translation matrix.
    The object's top-left corner is the point that gets transformed.
    """
    obj = copy.deepcopy(object_data)
    new_pos = apply_matrix(translation_matrix(dx, dy), [(obj["x"], obj["y"])])[0]
    obj["x"], obj["y"] = _clean(new_pos[0]), _clean(new_pos[1])
    return obj


def scale_object(object_data, scale_x, scale_y=None):
    """
    Resize the object about its CENTRE.

    scale_object(obj, 2)       -> uniform, 2x bigger
    scale_object(obj, 2, 0.5)  -> twice as wide, half as tall

    Math:  M = T(c) @ S(sx, sy) @ T(-c)   applied to the top-left and
    bottom-right corners (axis-aligned scaling keeps the box a box).
    """
    if scale_y is None:
        scale_y = scale_x
    if scale_x <= 0 or scale_y <= 0:
        raise ValueError("Scale factors must be positive.")

    obj = copy.deepcopy(object_data)
    cx, cy = get_center(obj)
    m = about_point(scaling_matrix(scale_x, scale_y), cx, cy)

    (x1, y1), (x2, y2) = apply_matrix(
        m, [(obj["x"], obj["y"]),
            (obj["x"] + obj["width"], obj["y"] + obj["height"])])

    obj["x"], obj["y"] = _clean(x1), _clean(y1)
    obj["width"], obj["height"] = _clean(x2 - x1), _clean(y2 - y1)
    # Cumulative bookkeeping (uniform factor; for non-uniform use the mean).
    obj["scale"] = _clean(obj.get("scale", 1.0) * (scale_x + scale_y) / 2.0)
    return obj


def rotate_object(object_data, angle):
    """
    Rotate the object by `angle` degrees about its CENTRE (cumulative).

    The centre does not move, so x/y/width/height stay the same; the stored
    `rotation` (degrees, normalised to [0, 360)) is what changes. Use
    get_corners() to obtain the rotated shape.
    """
    obj = copy.deepcopy(object_data)
    obj["rotation"] = _clean((obj.get("rotation", 0) + angle) % 360)
    return obj


# ---------------------------------------------------------------------------
# 4. Duplicate / remove
# ---------------------------------------------------------------------------

_last_assigned_id = 0


def _next_id(existing_objects=None, minimum=0):
    """Return an id larger than every id we know about."""
    global _last_assigned_id
    ids = [o["id"] for o in (existing_objects or [])]
    new_id = max(ids + [minimum, _last_assigned_id]) + 1
    _last_assigned_id = new_id
    return new_id


def duplicate_object(object_data, existing_objects=None, offset=(20, 20)):
    """
    Return a copy with a NEW unique id, shifted by `offset` so it is visible.

    Pass `existing_objects` (the full list) to guarantee the id is unique
    across the scene; without it, the id is still greater than the original's
    and greater than any id this module handed out before.
    """
    new_obj = copy.deepcopy(object_data)
    new_obj["id"] = _next_id(existing_objects, minimum=object_data["id"])
    return translate_object(new_obj, offset[0], offset[1])


def remove_object(objects, object_id):
    """Return a new list without the object whose id == object_id."""
    return [o for o in objects if o["id"] != object_id]


# ---------------------------------------------------------------------------
# 5. Layering  (list order = z-order, last item drawn on top)
# ---------------------------------------------------------------------------

def _index_of(objects, object_id):
    for i, o in enumerate(objects):
        if o["id"] == object_id:
            return i
    raise KeyError(f"No object with id {object_id}")


def bring_forward(objects, object_id):
    result = list(objects)
    i = _index_of(result, object_id)
    if i < len(result) - 1:
        result[i], result[i + 1] = result[i + 1], result[i]
    return result


def send_backward(objects, object_id):
    result = list(objects)
    i = _index_of(result, object_id)
    if i > 0:
        result[i], result[i - 1] = result[i - 1], result[i]
    return result


def bring_to_front(objects, object_id):
    result = list(objects)
    result.append(result.pop(_index_of(result, object_id)))
    return result


def send_to_back(objects, object_id):
    result = list(objects)
    result.insert(0, result.pop(_index_of(result, object_id)))
    return result


# ---------------------------------------------------------------------------
# 6. Perspective / homography  (OPTIONAL)
# ---------------------------------------------------------------------------

def get_perspective_matrix(src_points, dst_points):
    """
    3x3 homography H mapping 4 source points to 4 destination points
    (Direct Linear Transform, solved with NumPy; same result as
    cv2.getPerspectiveTransform).

    Example: map a rectangle onto a quadrilateral on an angled wall.
    """
    src = np.asarray(src_points, dtype=float)
    dst = np.asarray(dst_points, dtype=float)
    if src.shape != (4, 2) or dst.shape != (4, 2):
        raise ValueError("Need exactly 4 source and 4 destination points.")

    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    h = np.linalg.solve(np.array(A), np.array(b))
    return np.append(h, 1.0).reshape(3, 3)


def apply_perspective(object_data, dst_quad):
    """
    Return the object's four (rotated) corners mapped onto `dst_quad`.
    Output is an (4, 2) array; rendering (warping pixels) is left to
    cv2.warpPerspective in the UI layer.
    """
    x, y, w, h = (object_data[k] for k in ("x", "y", "width", "height"))
    rect = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    H = get_perspective_matrix(rect, dst_quad)
    return apply_matrix(H, rect)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo = {"id": 1, "type": "window", "x": 100, "y": 80, "width": 200,
            "height": 150, "rotation": 0, "scale": 1.0, "design": None,
            "confidence": 0.91, "source": "automatic"}
    print("Moved   :", translate_object(demo, 50, 20))
    print("Scaled  :", scale_object(demo, 2))
    print("Rotated :", rotate_object(demo, 45))
    print("Corners :\n", get_corners(rotate_object(demo, 90)))
