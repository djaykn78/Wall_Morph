# Wall Project update notes

## Consolidated handoff build

- Added local persistent project storage with separate original/canvas images, recent undo history, named versions, restore, and side-by-side comparison.
- Added a project dashboard for recent/open projects and auto-save after edits/reruns.
- Added perspective-mapped wallpaper application from four selected wall corners; retained rectangle selection and full-image default.
- Added perspective-aware four-corner object rendering and made geometry edits transform the stored quad.
- Kept scale/rotation state attached to replacement rendering and added perspective-aware object outlines.
- Replaced the offered brick wallpaper options with curated botanical, floral, art-deco, linen, geometric, pinstripe, arch, and wave designs.
- Added indoor-style window assets, curtain assets, and wall-mounted AC assets.
- Added persistent custom wallpaper uploads.
- Added reset confirmation, project setup instructions, and storage round-trip tests.

## Known limitations

- The default full-image option is not semantic wall segmentation. For a room photo, users should select the wall region manually and protect objects.
- AI model inference and the browser-based Streamlit UI were not run in the build environment because Streamlit packages were not installed and package-index network access was unavailable. Run the setup instructions on Windows to validate those parts.
- Four-corner object selection is perspective-aware, but its initial object boundary is still user-marked; automatic segmentation of complex object edges is not included.
