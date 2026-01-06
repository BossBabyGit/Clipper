import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List

from config import DEFAULT_CONFIG
from paths import CLIPS_DIR, DATA_DIR

FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")
CLIP_DURATION = int(os.getenv("CLIP_DURATION", "30"))


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def cut_clips(
    video_path: str,
    highlights_path: str,
    clips_dir: Path | str = CLIPS_DIR,
    clip_duration: int = CLIP_DURATION,
) -> List[str]:
    """Split the VOD into shorter clips around each highlight timestamp."""
    clips_dir = Path(clips_dir)
    _safe_mkdir(clips_dir)

    if not os.path.exists(highlights_path):
        raise FileNotFoundError(f"Missing highlight file at {highlights_path}")

    with open(highlights_path, encoding="utf-8") as f:
        highlights: Iterable[int] = json.load(f)

    created: List[str] = []
    for i, start in enumerate(highlights, 1):
        clip_id = f"clip_{i:02d}"
        dest_dir = clips_dir / clip_id
        _safe_mkdir(dest_dir)

        output_video = dest_dir / "raw.mp4"

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
                str(output_video),
            ],
            check=True,
        )

        with open(dest_dir / "config.json", "w", encoding="utf-8") as cfg:
            json.dump(DEFAULT_CONFIG, cfg, indent=2)

        created.append(clip_id)

    # Clean up stale clip folders if the highlight count dropped
    if created:
        keep_paths = {clips_dir / c for c in created}
        for folder in clips_dir.iterdir():
            if folder not in keep_paths:
                shutil.rmtree(folder, ignore_errors=True)

    return created


if __name__ == "__main__":
    data_root = Path(DATA_DIR)
    video = os.getenv("VIDEO", str(data_root / "vods" / "input.mp4"))
    highlights = os.getenv(
        "HIGHLIGHTS", str(data_root / "highlights" / "highlights.json")
    )
    created = cut_clips(video, highlights)
    print("Created clips:", created)
