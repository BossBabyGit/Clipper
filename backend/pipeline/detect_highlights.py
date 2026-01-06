import json
import os
from typing import Dict, List

import cv2
import librosa
import numpy as np

AUDIO_WINDOW = 0.25
AUDIO_MULT = 2.5
FRAME_SKIP = 6
VISUAL_THRESH = 30
MIN_GAP = 180

WIN_AREA: Dict[str, int] = {"x": 800, "y": 600, "w": 300, "h": 100}


def detect_highlights(video_path: str, audio_path: str, output_path: str) -> List[int]:
    """Blend audio spikes and visual motion to find candidate highlight timestamps."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Audio
    y, sr = librosa.load(audio_path, sr=None)
    hop = int(sr * AUDIO_WINDOW)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    thr = np.mean(rms) * AUDIO_MULT
    audio_hits = [i * hop / sr for i, v in enumerate(rms) if v > thr]

    # Video
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    prev = None
    visual_hits: List[float] = []
    i = 0

    while cap.isOpened():
        if not cap.grab():
            break
        if i % FRAME_SKIP == 0:
            _, f = cap.retrieve()
            roi = f[
                WIN_AREA["y"] : WIN_AREA["y"] + WIN_AREA["h"],
                WIN_AREA["x"] : WIN_AREA["x"] + WIN_AREA["w"],
            ]
            g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            if prev is not None and np.mean(cv2.absdiff(g, prev)) > VISUAL_THRESH:
                visual_hits.append(i / fps)
            prev = g
        i += 1

    cap.release()

    # Combine
    highlights: List[int] = []
    last = -999
    for t in audio_hits:
        if any(abs(t - v) < 1.5 for v in visual_hits) and t - last > MIN_GAP:
            highlights.append(int(t))
            last = t

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(highlights, f, indent=2)

    return highlights


if __name__ == "__main__":
    VIDEO = os.getenv("VIDEO", "data/vods/input.mp4")
    AUDIO = os.getenv("AUDIO", "data/vods/audio.wav")
    OUT = os.getenv("OUT", "data/highlights/highlights.json")
    detected = detect_highlights(VIDEO, AUDIO, OUT)
    print("Detected highlights:", detected)
