import os
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

import status
from clips import list_clips
from config import load_config, save_config
from pipeline.extract_audio import extract_audio
from pipeline.detect_highlights import detect_highlights
from pipeline.cut_clips import cut_clips
from pipeline.generate_subtitles import generate_subtitles
from render import render_clip

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
CLIPS_DIR = os.path.join(DATA_DIR, "clips")
VODS_DIR = os.path.join(DATA_DIR, "vods")
HIGHLIGHTS_DIR = os.path.join(DATA_DIR, "highlights")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for path in (CLIPS_DIR, VODS_DIR, HIGHLIGHTS_DIR):
    os.makedirs(path, exist_ok=True)


async def _run_step(
    step_id: str, running_detail: str, success_detail: str, func, *args, **kwargs
):
    status.mark_step(step_id, "in_progress", running_detail)
    try:
        result = await run_in_threadpool(func, *args, **kwargs)
    except Exception as exc:
        status.mark_step(step_id, "failed", str(exc))
        status.fail(str(exc))
        raise HTTPException(status_code=500, detail=f"{step_id} failed: {exc}") from exc
    status.mark_step(step_id, "completed", success_detail)
    return result


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    status.reset(file.filename)
    status.mark_step("upload", "in_progress", "Saving uploaded video")

    vod_path = os.path.join(VODS_DIR, "input.mp4")
    with open(vod_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    status.mark_step("upload", "completed", "Upload stored")

    audio_path = os.path.join(VODS_DIR, "audio.wav")
    highlights_path = os.path.join(HIGHLIGHTS_DIR, "highlights.json")

    await _run_step(
        "extract_audio",
        "Extracting mono audio track",
        "Audio ready",
        extract_audio,
        vod_path,
        audio_path,
    )
    await _run_step(
        "detect_highlights",
        "Scanning for peak action",
        "Highlights detected",
        detect_highlights,
        vod_path,
        audio_path,
        highlights_path,
    )
    created_clips = await _run_step(
        "cut_clips",
        "Cutting highlights into clips",
        "Clips saved",
        cut_clips,
        vod_path,
        highlights_path,
        CLIPS_DIR,
    )
    await _run_step(
        "generate_subtitles",
        "Transcribing speech with Whisper",
        "Subtitles generated",
        generate_subtitles,
        CLIPS_DIR,
    )

    status.complete(f"Created {len(created_clips)} clip(s)")
    return {"status": "processed", "clips": created_clips}

@app.get("/clips")
def clips():
    return list_clips(CLIPS_DIR)

@app.get("/clips/{cid}")
def get_cfg(cid):
    return load_config(os.path.join(CLIPS_DIR, cid))

@app.post("/clips/{cid}/config")
def save_cfg(cid: str, cfg: dict):
    save_config(os.path.join(CLIPS_DIR, cid), cfg)
    return {"ok": True}

@app.post("/clips/{cid}/render")
def render(cid):
    render_clip(os.path.join(CLIPS_DIR, cid))
    return {"ok": True}

@app.get("/status")
def processing_status():
    return status.get_status()


app.mount("/clips", StaticFiles(directory=CLIPS_DIR), name="clips")
