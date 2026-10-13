"""Local persistent project storage for Wall Project.
Projects are stored under ./projects and remain on this computer.
"""
from __future__ import annotations
import json, re, time
from pathlib import Path
import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent / "projects"

def _slug(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", (name or "My Wall Project").strip()).strip("_-")
    return (slug or "My_Wall_Project")[:64]

def list_projects():
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    out=[]
    for folder in PROJECT_ROOT.iterdir():
        meta=folder/"project.json"
        if folder.is_dir() and meta.exists():
            try:
                data=json.loads(meta.read_text(encoding="utf-8")); out.append({"id":folder.name,"name":data.get("name",folder.name),"updated":data.get("updated",""),"path":str(folder)})
            except (OSError, ValueError): pass
    return sorted(out,key=lambda x:x.get("updated",""),reverse=True)

def _write_image(path, image):
    ok, encoded=cv2.imencode(".png", image)
    if not ok: raise ValueError(f"Could not encode image: {path}")
    path.write_bytes(encoded.tobytes())

def save_project(name, original, canvas, objects, history, cursor, named_versions=None):
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    folder=PROJECT_ROOT/_slug(name); folder.mkdir(parents=True,exist_ok=True)
    _write_image(folder/"original.png", original)
    _write_image(folder/"canvas.png", canvas)
    # Keep recent undo states across sessions. Image snapshots are separate PNGs.
    hist=[]
    for i,snap in enumerate(history[-30:]):
        filename=f"history_{i:02d}.png"; _write_image(folder/filename,snap["image"])
        hist.append({"image":filename,"objects":snap.get("objects",[])})
    existing_versions=[]
    existing_meta=folder/"project.json"
    if existing_meta.exists():
        try: existing_versions=json.loads(existing_meta.read_text(encoding="utf-8")).get("named_versions",[])
        except (OSError, ValueError): pass
    meta={"name":name.strip() or "My Wall Project","updated":time.strftime("%Y-%m-%d %H:%M:%S"),"objects":objects,"history":hist,"history_cursor":max(0,min(int(cursor),len(hist)-1)),"named_versions":named_versions if named_versions is not None else existing_versions}
    (folder/"project.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
    return folder.name

def load_project(project_id):
    folder=PROJECT_ROOT/_slug(project_id)
    meta=json.loads((folder/"project.json").read_text(encoding="utf-8"))
    def read(name):
        image=cv2.imread(str(folder/name),cv2.IMREAD_COLOR)
        if image is None: raise ValueError(f"Project image missing or unreadable: {name}")
        return image
    history=[{"image":read(item["image"]),"objects":item.get("objects",[])} for item in meta.get("history",[])]
    if not history: history=[{"image":read("canvas.png"),"objects":meta.get("objects",[])}]
    return {"name":meta.get("name",project_id),"original":read("original.png"),"canvas":read("canvas.png"),"objects":meta.get("objects",[]),"history":history,"history_cursor":meta.get("history_cursor",len(history)-1),"named_versions":meta.get("named_versions",[])}

def save_named_version(name, canvas, objects, original, label=None):
    PROJECT_ROOT.mkdir(parents=True,exist_ok=True)
    folder=PROJECT_ROOT/_slug(name)
    if not (folder/"project.json").exists(): return None
    versions_dir=folder/"versions"; versions_dir.mkdir(exist_ok=True)
    versions=json.loads((folder/"project.json").read_text(encoding="utf-8"))
    label=(label or f"Version {len(versions.get('named_versions',[]))+1}").strip()
    filename=f"version_{int(time.time()*1000)}.png"; _write_image(versions_dir/filename,canvas)
    versions.setdefault("named_versions",[]).append({"name":label,"image":f"versions/{filename}","objects":objects,"saved":time.strftime("%Y-%m-%d %H:%M:%S")})
    (folder/"project.json").write_text(json.dumps(versions,indent=2,ensure_ascii=False),encoding="utf-8")
    return label


def read_named_version(project_name, label):
    folder=PROJECT_ROOT/_slug(project_name)
    meta=json.loads((folder/"project.json").read_text(encoding="utf-8"))
    item=next((v for v in meta.get("named_versions",[]) if v.get("name")==label),None)
    if item is None: raise KeyError(f"No saved version named {label}")
    image=cv2.imread(str(folder/item["image"]),cv2.IMREAD_COLOR)
    if image is None: raise ValueError("Saved version image is missing")
    return {"image":image,"objects":item.get("objects",[])}
