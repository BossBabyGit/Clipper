import json
import os
from datetime import datetime
from typing import Dict, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATUS_PATH = os.path.join(DATA_DIR, "status.json")

STEP_DEFS = [
    ("upload", "Upload received"),
    ("extract_audio", "Extract audio"),
    ("detect_highlights", "Detect highlights"),
    ("cut_clips", "Create clips"),
    ("generate_subtitles", "Transcribe clips"),
]


def _timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _write_status(payload: Dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    payload["updated_at"] = _timestamp()
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def reset(upload_name: str) -> Dict:
    steps: List[Dict] = [
        {"id": sid, "label": label, "state": "pending", "detail": ""}
        for sid, label in STEP_DEFS
    ]
    status = {
        "upload": upload_name,
        "state": "processing",
        "steps": steps,
        "error": None,
    }
    _write_status(status)
    return status


def get_status() -> Dict:
    if not os.path.exists(STATUS_PATH):
        return {
            "state": "idle",
            "steps": [
                {"id": sid, "label": label, "state": "pending", "detail": ""}
                for sid, label in STEP_DEFS
            ],
            "error": None,
            "upload": None,
            "updated_at": _timestamp(),
        }
    with open(STATUS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    if "updated_at" not in data:
        data["updated_at"] = _timestamp()
    return data


def mark_step(step_id: str, state: str, detail: str = "") -> Dict:
    status = get_status()
    for step in status.get("steps", []):
        if step.get("id") == step_id:
            step["state"] = state
            if detail:
                step["detail"] = detail
            break
    _write_status(status)
    return status


def complete(detail: str = "") -> Dict:
    status = get_status()
    status["state"] = "completed"
    if detail:
        status["summary"] = detail
    _write_status(status)
    return status


def fail(reason: str) -> Dict:
    status = get_status()
    status["state"] = "error"
    status["error"] = reason
    _write_status(status)
    return status
