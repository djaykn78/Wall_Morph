"""Fast local smoke tests for the integrated modules; does not run AI model downloads."""
import os
import unittest
import numpy as np

from design_database import (
    get_designs, get_object_types, get_wallpapers, get_textures, resolve_asset_path,
)
from image_processing import create_polygon_mask, apply_wall_color, apply_wall_wallpaper_perspective
from manual_selection import add_manual_object, get_object_types as manual_object_types
from transformations import translate_object, scale_object, rotate_object, duplicate_object


class IntegrationSmokeTests(unittest.TestCase):
    def test_registered_assets_exist(self):
        assets = []
        for category in get_object_types(include_empty=True):
            assets.extend(get_designs(category))
        assets.extend(get_wallpapers())
        assets.extend(get_textures())
        missing = [item["path"] for item in assets if not os.path.isfile(resolve_asset_path(item["path"]))]
        self.assertEqual(missing, [])
        self.assertGreater(len(assets), 50)

    def test_new_category_can_be_manually_added_without_designs(self):
        objects = add_manual_object([], "mirror", 5, 6, 20, 25, image_size=(100, 100))
        self.assertEqual(objects[0]["type"], "mirror")
        self.assertIn("mirror", manual_object_types(objects))
        self.assertEqual(get_designs("mirror"), [])

    def test_transformations_work_on_shared_object_schema(self):
        obj = {"id": 1, "type": "door", "x": 10, "y": 12, "width": 20,
               "height": 30, "rotation": 0, "scale": 1.0, "design": None,
               "confidence": None, "source": "manual"}
        moved = translate_object(obj, 5, 3)
        scaled = scale_object(moved, 1.5)
        rotated = rotate_object(scaled, 30)
        duplicate = duplicate_object(rotated, [rotated])
        self.assertEqual((moved["x"], moved["y"]), (15, 15))
        self.assertEqual(rotated["rotation"], 30)
        self.assertNotEqual(duplicate["id"], rotated["id"])

    def test_perspective_wallpaper_returns_same_shape_and_changes_selected_area(self):
        image = np.full((100, 120, 3), 160, dtype=np.uint8)
        pattern = np.zeros((32, 32, 3), dtype=np.uint8)
        pattern[:, :16] = (20, 90, 180); pattern[:, 16:] = (180, 190, 210)
        result = apply_wall_wallpaper_perspective(image, [(15, 15), (100, 8), (108, 82), (20, 90)], pattern, opacity=1.0)
        self.assertEqual(result.shape, image.shape)
        self.assertFalse(np.array_equal(result, image))
        self.assertTrue(np.array_equal(result[0, 0], image[0, 0]))

    def test_wall_color_processing_returns_same_shape(self):
        image = np.full((80, 100, 3), 180, dtype=np.uint8)
        mask = create_polygon_mask(image, [(5, 5), (95, 5), (95, 75), (5, 75)])
        result = apply_wall_color(image, mask, (40, 80, 120))
        self.assertEqual(result.shape, image.shape)
        self.assertFalse(np.array_equal(result, image))


if __name__ == "__main__":
    unittest.main(verbosity=2)
