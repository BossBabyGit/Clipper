from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil, subprocess, os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PIPELINE_DIR = os.path.join(BASE_DIR, "pipeline")

os.makedirs("data/clips", exist_ok=True)
os.makedirs("data/vods", exist_ok=True)
os.makedirs("data/highlights", exist_ok=True)

from render import render_clip
from clips import list_clips
from config import load_config, save_config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data/vods", exist_ok=True)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    with open("data/vods/input.mp4", "wb") as f:
        shutil.copyfileobj(file.file, f)

    subprocess.run(["python", "pipeline/extract_audio.py"])
    subprocess.run(["python", "pipeline/detect_highlights.py"])
    subprocess.run(["python", "pipeline/cut_clips.py"])
    subprocess.run(["python", "pipeline/generate_subtitles.py"])

    return {"status": "processed"}

@app.get("/clips")
def clips():
    return list_clips("data/clips")

@app.get("/clips/{cid}")
def get_cfg(cid):
    return load_config(f"data/clips/{cid}")

@app.post("/clips/{cid}/config")
def save_cfg(cid: str, cfg: dict):
    save_config(f"data/clips/{cid}", cfg)
    return {"ok": True}

@app.post("/clips/{cid}/render")
def render(cid):
    render_clip(f"data/clips/{cid}")
    return {"ok": True}

app.mount("/clips", StaticFiles(directory="data/clips"), name="clips")
