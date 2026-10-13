# Interactive Wall Visualization & Redesigning System — Integrated Project

## Run it

Use Python 3.10 or newer. From a terminal, change directory to the folder containing `app.py` and run:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. Upload a room/wall image to start.

## AI object detection (optional)

The detection module supports Grounding DINO, YOLO-World, and COCO/YOLO backends. AI detection may require model downloads and extra dependencies. Install a compatible PyTorch build for your machine, then install `transformers` and/or `ultralytics`. If the model fails to load, the app explains that no detections were returned and manual object addition remains available.

## Features connected in this integration

- Existing design database and all 98 provided asset files
- Automatic detection through `detection.py`
- Manual object addition, type expansion, bounding-box updates, and deletion
- Design lookup and transparent asset compositing
- Translation, scaling, rotation state, duplication, and layer ordering APIs
- Solid wall colors, wallpaper, and texture effects using polygon masks
- Undo/redo snapshots, reset, before/current comparison, and PNG export
- Robust asset paths independent of the terminal's current directory

## Adding another object category

1. Add its replacement image files beneath `assets/<category>/`.
2. Register designs with `add_design("mirror", "mirror_1", "Mirror 1", "assets/mirror/mirror_1.png")` (or add the metadata to `DESIGNS`).
3. Add prompts and post-processing settings to `detection.py` if AI detection should recognize it automatically. Manual object types and design lookup already allow new category names.

## Wall mask

The app asks for polygon vertices in original image pixel coordinates, one `x,y` pair per line. This avoids requiring a separate drawing-canvas dependency. Choose at least three points around the wall. Excluding object boxes helps keep the finish off doors, windows, and furniture.

## Notes

- Image operations use BGR arrays internally; Streamlit previews convert them to RGB.
- The project was integration-tested with syntax checks and local smoke tests. AI model inference was not run because it may download large weights and depends on the machine's installed model packages.
