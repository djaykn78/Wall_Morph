import cv2
import numpy as np
import os


def load_image(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    image = cv2.imread(path)

    if image is None:
        raise ValueError(f"Unable to load image: {path}")

    return image


def resize_image(image, width, height):
    if image is None:
        raise ValueError("Image is empty")

    if width <= 0 or height <= 0:
        raise ValueError("Width and height must be positive")

    return cv2.resize(
        image,
        (width, height),
        interpolation=cv2.INTER_AREA
    )


def blend_with_mask(original, modified, mask):
    if original is None or modified is None:
        raise ValueError("Images cannot be empty")

    if original.shape != modified.shape:
        raise ValueError(
            "Original and modified images must have the same size"
        )

    if mask.shape[:2] != original.shape[:2]:
        raise ValueError(
            "Mask and image must have the same dimensions"
        )

    if len(mask.shape) == 3:
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    mask = mask.astype(np.float32) / 255.0
    mask = np.expand_dims(mask, axis=2)

    result = (
        original.astype(np.float32) * (1 - mask)
        + modified.astype(np.float32) * mask
    )

    result = np.clip(result, 0, 255).astype(np.uint8)

    return np.ascontiguousarray(result)


def apply_wall_color(image, wall_mask, color):
    if image is None:
        raise ValueError("Image is empty")

    if wall_mask.shape[:2] != image.shape[:2]:
        raise ValueError(
            "Mask and image must have the same dimensions"
        )

    color_layer = np.zeros_like(image)
    color_layer[:, :] = color

    color_hsv = cv2.cvtColor(
        color_layer,
        cv2.COLOR_BGR2HSV
    )

    image_hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    image_hsv[:, :, 0] = color_hsv[:, :, 0]
    image_hsv[:, :, 1] = color_hsv[:, :, 1]

    modified = cv2.cvtColor(
        image_hsv,
        cv2.COLOR_HSV2BGR
    )

    return blend_with_mask(
        image,
        modified,
        wall_mask
    )


def apply_wall_wallpaper(image, wall_mask, wallpaper, opacity=0.90):
    if image is None:
        raise ValueError("Image is empty")

    if wallpaper is None:
        raise ValueError("Wallpaper is empty")

    x, y, width, height = cv2.boundingRect(wall_mask)

    if width == 0 or height == 0:
        raise ValueError("Wall mask is empty")

    wallpaper = resize_image(
        wallpaper,
        width,
        height
    )

    original_region = image[y:y + height, x:x + width]

    original_hsv = cv2.cvtColor(
        original_region,
        cv2.COLOR_BGR2HSV
    )

    wallpaper_hsv = cv2.cvtColor(
        wallpaper,
        cv2.COLOR_BGR2HSV
    )

    wallpaper_hsv[:, :, 2] = original_hsv[:, :, 2]

    modified = image.copy()

    wallpaper_bgr = cv2.cvtColor(
        wallpaper_hsv,
        cv2.COLOR_HSV2BGR
    )

    modified[y:y + height, x:x + width] = wallpaper_bgr

    # Opacity controls how strongly the wallpaper pattern appears over the
    # source wall while preserving lighting and wall details.
    opacity = float(max(0.0, min(1.0, opacity)))
    blended = cv2.addWeighted(image, 1.0 - opacity, modified, opacity, 0)
    return blend_with_mask(image, blended, wall_mask)

def apply_wall_texture(image, wall_mask, texture):
    if image is None:
        raise ValueError("Image is empty")

    if texture is None:
        raise ValueError("Texture is empty")

    x, y, width, height = cv2.boundingRect(wall_mask)

    if width == 0 or height == 0:
        raise ValueError("Wall mask is empty")

    texture = resize_image(
        texture,
        width,
        height
    )

    original_region = image[y:y + height, x:x + width]

    texture_gray = cv2.cvtColor(
        texture,
        cv2.COLOR_BGR2GRAY
    )

    texture_gray = cv2.GaussianBlur(
        texture_gray,
        (3, 3),
        0
    )

    texture_gray = texture_gray.astype(np.float32)

    texture_gray = cv2.normalize(
        texture_gray,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    texture_gray = texture_gray.astype(np.uint8)

    texture_gray = cv2.cvtColor(
        texture_gray,
        cv2.COLOR_GRAY2BGR
    )

    original_region = original_region.astype(np.float32)
    texture_gray = texture_gray.astype(np.float32)

    modified_region = (
        original_region * 0.75
        + texture_gray * 0.25
    )

    modified_region = np.clip(
        modified_region,
        0,
        255
    ).astype(np.uint8)

    modified = image.copy()

    modified[
        y:y + height,
        x:x + width
    ] = modified_region

    return blend_with_mask(
        image,
        modified,
        wall_mask
    )

    
def save_image(image, path):
    if image is None:
        raise ValueError("Image is empty")

    image = np.ascontiguousarray(image)

    folder = os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    success = cv2.imwrite(path, image)

    if not success:
        if os.path.exists(path):
            return path
        raise IOError(
            f"Unable to save image: {path}"
        )

    return path


def create_polygon_mask(image, points):
    if image is None:
        raise ValueError("Image is empty")

    mask = np.zeros(
        image.shape[:2],
        dtype=np.uint8
    )

    points = np.array(
        points,
        dtype=np.int32
    )

    cv2.fillPoly(
        mask,
        [points],
        255
    )

    return mask


def exclude_objects_from_mask(wall_mask, objects):
    if wall_mask is None:
        raise ValueError("Wall mask is empty")

    mask = wall_mask.copy()

    for obj in objects:
        x = int(obj["x"])
        y = int(obj["y"])
        width = int(obj["width"])
        height = int(obj["height"])

        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(mask.shape[1], x + width)
        y2 = min(mask.shape[0], y + height)

        mask[y1:y2, x1:x2] = 0

    return mask

def apply_wall_wallpaper_perspective(image, quad_points, wallpaper, opacity=0.90):
    """Project a wallpaper tile onto a four-corner wall quadrilateral."""
    if image is None or wallpaper is None:
        raise ValueError("Image and wallpaper are required")
    pts = np.asarray(quad_points, dtype=np.float32)
    if pts.shape != (4, 2):
        raise ValueError("Exactly four wall corner points are required")
    # Stable clockwise ordering around the centroid, then start at top-left.
    center = pts.mean(axis=0)
    pts = np.array(sorted(pts.tolist(), key=lambda p: np.arctan2(p[1]-center[1], p[0]-center[0])), dtype=np.float32)
    first = min(range(4), key=lambda i: float(pts[i,0]+pts[i,1]))
    pts = np.concatenate([pts[first:], pts[:first]])
    top_w = max(1, int(max(np.linalg.norm(pts[1]-pts[0]), np.linalg.norm(pts[2]-pts[3]))))
    side_h = max(1, int(max(np.linalg.norm(pts[3]-pts[0]), np.linalg.norm(pts[2]-pts[1]))))
    tile = cv2.resize(wallpaper, (top_w, side_h), interpolation=cv2.INTER_AREA if top_w < wallpaper.shape[1] else cv2.INTER_LINEAR)
    src = np.float32([[0,0],[top_w-1,0],[top_w-1,side_h-1],[0,side_h-1]])
    H = cv2.getPerspectiveTransform(src, pts)
    h, w = image.shape[:2]
    projected = cv2.warpPerspective(tile, H, (w,h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    mask = np.zeros((h,w), dtype=np.uint8)
    cv2.fillPoly(mask, [np.round(pts).astype(np.int32)], 255)
    original_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    pattern_hsv = cv2.cvtColor(projected, cv2.COLOR_BGR2HSV)
    pattern_hsv[:,:,2] = original_hsv[:,:,2]
    projected = cv2.cvtColor(pattern_hsv, cv2.COLOR_HSV2BGR)
    opacity = float(np.clip(opacity, 0.0, 1.0))
    blended = cv2.addWeighted(image, 1-opacity, projected, opacity, 0)
    return blend_with_mask(image, blended, mask)
