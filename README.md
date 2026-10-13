# Wall Project — Wall Visualization Studio

A local Streamlit application for experimenting with wall finishes and replacement object assets. The original photo is kept separately from the editable canvas. Projects are stored locally in `projects/`.

## Windows setup (recommended)

Open **Command Prompt** in the extracted `Wall_Project` folder. Use a project virtual environment so Windows does not accidentally run MSYS/system Python:

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If `py -3.11` is not available, install Python 3.11 (64-bit) from python.org and enable the Python Launcher during setup. Alternatively, use `python -m venv .venv` only after checking `where python` points to the intended Windows Python. Do not use `C:\msys64\...\python.exe` for this project.

Open the local URL printed by Streamlit (normally `http://localhost:8501`). The project does not require a cloud account. Local project images and metadata are stored under `projects/`; back up that folder if you need to transfer projects to another computer.

## Main workflow

1. Upload a wall/room photo, or open a recent local project.
2. Try automatic object detection. If detection fails, use the manual object selection panel and mark four corners.
3. Choose a wall finish. Full-image mode is the default; turn it off to draw a wall/region rectangle.
4. Protect object boxes where needed, apply the finish, and preview it.
5. Add replacement designs to selected objects; adjust position/size, scale and rotation.
6. Use Undo/Redo, save a named version, compare/restore versions, and download the final PNG.

## Notes and limitations

- All image processing is local. Auto-saved projects are plain files under `projects/`.
- The original uploaded photo is stored separately and is not overwritten by edits.
- Wallpaper mode offers curated botanical, floral, art-deco, linen, geometric, pinstripe, arch, and wave patterns. The older brick wallpapers are no longer offered in the gallery. Added object assets include indoor-style windows, curtains, and wall-mounted AC units.
- Four-corner object selections are rendered with a perspective transform. Ordinary detected/rectangular objects use bounding-box geometry and rotation.
- Full-image mode is intentionally the default, but it applies to the **whole image**, not a semantic wall segmentation mask. For room photos containing furniture/floor/ceiling, turn off full-image mode and draw around the wall, and keep object protection enabled. Fully automatic wall segmentation is not implemented in this build.
- AI object detection may need large model downloads and compatible dependencies. If it returns no detections, try another backend or use manual selection. AI detection was not exercised during local smoke tests.
- Streamlit's interactive browser UI must be tested on the target Windows computer; the current execution environment did not have Streamlit installed, so the app was syntax-checked and its non-UI tests were run, but a full browser session was not launched here.

## Tests

```bat
python -m pytest -q
python test_design_database.py
```

## Project data

`projects/` is created automatically. Each named project stores `original.png`, `canvas.png`, recent undo snapshots, object metadata, and named-version PNGs. Keep the folder with the project if moving the app to another machine.
