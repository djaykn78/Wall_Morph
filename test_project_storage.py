"""Tests for persistent project round-tripping without changing user data."""
import tempfile
import unittest
from pathlib import Path
import cv2
import numpy as np
import project_storage

class ProjectStorageTests(unittest.TestCase):
    def test_save_and_load_preserves_original_canvas_and_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = project_storage.PROJECT_ROOT
            project_storage.PROJECT_ROOT = Path(tmp)
            try:
                original=np.full((12,14,3), 90, dtype=np.uint8)
                canvas=original.copy(); canvas[2:5,3:7]=200
                objects=[{"id":1,"type":"window","x":3,"y":2,"width":4,"height":3,"rotation":15,"scale":1.2,"design":None}]
                history=[{"image":original,"objects":[]},{"image":canvas,"objects":objects}]
                project_storage.save_project("Demo Room",original,canvas,objects,history,1)
                loaded=project_storage.load_project("Demo_Room")
                self.assertTrue(np.array_equal(loaded["original"],original))
                self.assertTrue(np.array_equal(loaded["canvas"],canvas))
                self.assertEqual(loaded["objects"][0]["rotation"],15)
                self.assertEqual(len(loaded["history"]),2)
                label=project_storage.save_named_version("Demo Room",canvas,objects,original,"Evening palette")
                self.assertEqual(label,"Evening palette")
                # Normal auto-save must not discard named snapshots.
                project_storage.save_project("Demo Room",original,canvas,objects,history,1)
                restored=project_storage.read_named_version("Demo Room","Evening palette")
                self.assertTrue(np.array_equal(restored["image"],canvas))
            finally:
                project_storage.PROJECT_ROOT=old

if __name__ == '__main__': unittest.main()
