import json
import os
import shutil
import subprocess
from typing import Iterable, List

from config import DEFAULT_CONFIG

FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")
CLIP_DURATION = int(os.getenv("CLIP_DURATION", "30"))


def _safe_mkdir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def cut_clips(
    video_path: str,
    highlights_path: str,
    clips_dir: str = "data/clips",
    clip_duration: int = CLIP_DURATION,
) -> List[str]:
    """Split the VOD into shorter clips around each highlight timestamp."""
    _safe_mkdir(clips_dir)

    if not os.path.exists(highlights_path):
        raise FileNotFoundError(f"Missing highlight file at {highlights_path}")

    with open(highlights_path, encoding="utf-8") as f:
        highlights: Iterable[int] = json.load(f)

    created: List[str] = []
    for i, start in enumerate(highlights, 1):
        clip_id = f"clip_{i:02d}"
        dest_dir = os.path.join(clips_dir, clip_id)
        _safe_mkdir(dest_dir)

        output_video = os.path.join(dest_dir, "raw.mp4")

        subprocess.run(
            [
                FFMPEG,
                "-ss",
                str(max(0, start)),
                "-i",
                video_path,
                "-t",
                str(clip_duration),
                "-c",
                "copy",
                output_video,
            ],
            check=True,
        )

        with open(os.path.join(dest_dir, "config.json"), "w", encoding="utf-8") as cfg:
            json.dump(DEFAULT_CONFIG, cfg, indent=2)

        created.append(clip_id)

    # Clean up stale clip folders if the highlight count dropped
    if created:
        keep_paths = {os.path.join(clips_dir, c) for c in created}
        for folder in os.listdir(clips_dir):
            full = os.path.join(clips_dir, folder)
            if full not in keep_paths:
                shutil.rmtree(full, ignore_errors=True)

    return created


if __name__ == "__main__":
    video = os.getenv("VIDEO", "data/vods/input.mp4")
    highlights = os.getenv("HIGHLIGHTS", "data/highlights/highlights.json")
    created = cut_clips(video, highlights)
    print("Created clips:", created)
