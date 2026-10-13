"""
manual_selection.py
Person 5 - Manual Selection & Object Management
Project: Interactive Wall Visualization and Redesigning System

Purpose
-------
Manage the shared `objects` list: add manually drawn objects, correct
bounding boxes, select, delete and re-type objects.

This module does NOT: detect objects (Person 3), transform objects
(Person 4), manage designs (Person 1), edit the wall image (Person 2) or
draw the UI (Person 6).

Shared object format (keys must never be renamed)
-------------------------------------------------
{
    "id": 1, "type": "window",
    "x": 100, "y": 80, "width": 200, "height": 150,   # top-left origin
    "rotation": 0, "scale": 1.0, "design": None,
    "confidence": 0.91,          # None for manual objects
    "source": "automatic",       # "manual" for manual objects
}

Conventions
-----------
* Image origin (0, 0) is the TOP-LEFT corner. x = column, y = row.
* Every function that changes the list returns a NEW list (the input list
  and its dicts are never modified). Always use:  objects = f(objects, ...)
  This makes undo/redo (history stack of lists) easy for Person 6.
* Invalid input raises ValueError with a readable message. Person 6 can
  wrap calls in try/except ValueError and show the message with st.error().

Dependencies: Python standard library only.
"""

import math
import numbers

# Common categories shown by default in the UI. This list is a convenience,
# NOT a restriction: custom and newly detected categories are accepted too.
# Add new defaults here only if you want them to appear even before detection.
OBJECT_TYPES = [
    "door", "window", "table", "bookshelf", "light", "switchboard",
    "decoration", "wardrobe", "curtain", "bed", "whiteboard","ground",
]

SOURCE_MANUAL = "manual"
SOURCE_AUTOMATIC = "automatic"

# Highest ID ever issued in this session. Stops an ID from being reused
# after the object that had it was deleted (important for undo/redo and
# for anything that refers to an object by id).
_last_issued_id = 0


# --------------------------------------------------------------------------
# Internal helpers / validation
# --------------------------------------------------------------------------
def _copy_objects(objects):
    """Copy the list and each object dict so the caller's data is untouched."""
    return [dict(obj) for obj in objects]


def _validate_number(value, name):
    """Return value as a finite number; reject bool, strings, NaN, inf."""
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"{name} must be a number, got {value!r}")
    if not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")
    return value


def normalize_object_type(object_type):
    """Normalize a category name into a stable key suitable for data lookup."""
    if not isinstance(object_type, str):
        raise ValueError(f"object type must be a string, got {object_type!r}")
    cleaned = "_".join(object_type.strip().lower().replace("-", " ").split())
    if not cleaned:
        raise ValueError("object type cannot be empty")
    return cleaned


def validate_object_type(object_type):
    """Return a normalized object type. Unknown categories are allowed for expansion."""
    return normalize_object_type(object_type)


def get_object_types(objects=None, extra_types=None):
    """Return sorted UI categories, including defaults and types already in use.

    Pass detector results as ``extra_types`` or pass the shared ``objects`` list.
    This function does not claim that every category has a replacement design.
    """
    types = set(OBJECT_TYPES)
    for obj in objects or []:
        value = obj.get("type") if isinstance(obj, dict) else None
        if isinstance(value, str) and value.strip():
            types.add(normalize_object_type(value))
    for value in extra_types or []:
        if isinstance(value, str) and value.strip():
            types.add(normalize_object_type(value))
    return sorted(types)


def validate_box(x, y, width, height, image_size=None):
    """
    Validate a box in (x, y, width, height) form and return it as ints.

    x, y must be >= 0; width, height must be > 0.
    image_size: optional (image_width, image_height). If given, the box
    must lie fully inside the image.
    """
    x = _validate_number(x, "x")
    y = _validate_number(y, "y")
    width = _validate_number(width, "width")
    height = _validate_number(height, "height")

    if x < 0 or y < 0:
        raise ValueError(f"x and y must be >= 0, got x={x}, y={y}")
    if width <= 0 or height <= 0:
        raise ValueError(
            f"width and height must be positive, got {width} x {height}"
        )

    x, y, width, height = (int(round(v)) for v in (x, y, width, height))
    # Rounding a tiny positive value (e.g. 0.3) could give 0 - re-check.
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be at least 1 pixel")

    if image_size is not None:
        img_w, img_h = image_size
        if x + width > img_w or y + height > img_h:
            raise ValueError(
                f"Box (x={x}, y={y}, w={width}, h={height}) goes outside the "
                f"image ({img_w} x {img_h})"
            )
    return x, y, width, height


def generate_object_id(objects):
    """
    Return a new unique integer id.

    It is larger than every id currently in `objects` AND larger than any id
    this module has issued before, so deleted ids are never recycled.
    """
    global _last_issued_id
    existing = [o["id"] for o in objects if isinstance(o.get("id"), int)]
    new_id = max([_last_issued_id] + existing) + 1
    _last_issued_id = new_id
    return new_id


def reset_id_counter(value=0):
    """Reset the id counter (used by tests / when a new image is loaded)."""
    global _last_issued_id
    _last_issued_id = value


# --------------------------------------------------------------------------
# Coordinate helpers (the ONLY place where x1,y1,x2,y2 <-> x,y,w,h happens)
# --------------------------------------------------------------------------
def box_from_corners(x1, y1, x2, y2):
    """
    Convert two corner points (e.g. mouse-down and mouse-up of a drag) into
    (x, y, width, height). The corners can be in any order, so dragging
    right-to-left or bottom-to-top also works.
    """
    x1 = _validate_number(x1, "x1")
    y1 = _validate_number(y1, "y1")
    x2 = _validate_number(x2, "x2")
    y2 = _validate_number(y2, "y2")
    x, y = min(x1, x2), min(y1, y2)
    return int(round(x)), int(round(y)), int(round(abs(x2 - x1))), int(round(abs(y2 - y1)))


def box_to_corners(obj):
    """Return (x1, y1, x2, y2) for an object dict (handy for cv2.rectangle)."""
    return obj["x"], obj["y"], obj["x"] + obj["width"], obj["y"] + obj["height"]


# --------------------------------------------------------------------------
# Main API
# --------------------------------------------------------------------------
def get_object_by_id(objects, object_id):
    """Return the object dict with this id, or None if it does not exist."""
    for obj in objects:
        if obj.get("id") == object_id:
            return obj
    return None


def _require_object(objects, object_id):
    obj = get_object_by_id(objects, object_id)
    if obj is None:
        raise ValueError(f"No object with id {object_id!r}")
    return obj


def add_manual_object(objects, object_type, x, y, width, height, image_size=None):
    """
    Create a manual object and return a NEW list with it appended.

    The new object is always the last element: objects[-1]["id"] gives its id.
    image_size=(w, h) is optional and enables an "inside the image" check.
    """
    object_type = validate_object_type(object_type)
    x, y, width, height = validate_box(x, y, width, height, image_size)

    new_obj = {
        "id": generate_object_id(objects),
        "type": object_type,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "rotation": 0,
        "scale": 1.0,
        "design": None,
        "confidence": None,
        "source": SOURCE_MANUAL,
    }
    updated = _copy_objects(objects)
    updated.append(new_obj)
    return updated


def select_object(objects, object_id):
    """
    Return the object with this id so the app can use it (e.g. keep it as
    `selected_object`). Raises ValueError if the id does not exist.
    """
    return _require_object(objects, object_id)


def remove_object(objects, object_id):
    """Return a NEW list without the object. Other objects are untouched."""
    _require_object(objects, object_id)
    return [dict(o) for o in objects if o.get("id") != object_id]


def change_object_type(objects, object_id, new_type):
    """Return a NEW list where only the 'type' of one object has changed."""
    new_type = validate_object_type(new_type)
    _require_object(objects, object_id)
    updated = _copy_objects(objects)
    for obj in updated:
        if obj["id"] == object_id:
            obj["type"] = new_type
    return updated


def update_bounding_box(objects, object_id, x=None, y=None, width=None,
                        height=None, image_size=None):
    """
    Correct an object's box and return a NEW list.

    Pass all four values, or pass None for any value you want to keep.
    Only x, y, width, height change - rotation, scale, design, confidence
    and source are left as they were (an automatic object stays "automatic").
    """
    current = _require_object(objects, object_id)
    new_x = current["x"] if x is None else x
    new_y = current["y"] if y is None else y
    new_w = current["width"] if width is None else width
    new_h = current["height"] if height is None else height
    new_x, new_y, new_w, new_h = validate_box(new_x, new_y, new_w, new_h, image_size)

    updated = _copy_objects(objects)
    for obj in updated:
        if obj["id"] == object_id:
            obj["x"], obj["y"] = new_x, new_y
            obj["width"], obj["height"] = new_w, new_h
    return updated


# --------------------------------------------------------------------------
# Quick demo:  python manual_selection.py
# --------------------------------------------------------------------------
if __name__ == "__main__":
    objs = [{
        "id": 1, "type": "window", "x": 100, "y": 80, "width": 200,
        "height": 150, "rotation": 0, "scale": 1.0, "design": None,
        "confidence": 0.91, "source": "automatic",
    }]
    objs = add_manual_object(objs, "table", 300, 200, 180, 120)
    objs = update_bounding_box(objs, 1, x=110, y=85, width=210, height=155)
    objs = change_object_type(objs, 2, "bookshelf")
    objs = remove_object(objs, 1)
    print(objs)
