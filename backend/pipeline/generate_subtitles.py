import os
from pathlib import Path

import whisper
from paths import CLIPS_DIR

model = whisper.load_model(os.getenv("WHISPER_MODEL", "small"))


def _format_ts(seconds: float) -> str:
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    return f"{int(hrs):02d}:{int(mins):02d}:{secs:06.3f}".replace(".", ",")


def generate_subtitles(clips_dir: str | os.PathLike[str] = CLIPS_DIR) -> None:
    clips_dir = Path(clips_dir)
    if not clips_dir.exists():
        return
    for clip in clips_dir.iterdir():
        raw = clip / "raw.mp4"
        if not raw.exists():
            continue

        result = model.transcribe(str(raw))
        with open(clip / "subtitles.srt", "w", encoding="utf-8") as f:
            for i, seg in enumerate(result.get("segments", []), 1):
                f.write(
                    f"{i}\n"
                    f"{_format_ts(seg['start'])} --> {_format_ts(seg['end'])}\n"
                    f"{seg['text'].strip()}\n\n"
                )


if __name__ == "__main__":
    generate_subtitles()
