import os

import whisper

model = whisper.load_model(os.getenv("WHISPER_MODEL", "small"))


def _format_ts(seconds: float) -> str:
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    return f"{int(hrs):02d}:{int(mins):02d}:{secs:06.3f}".replace(".", ",")


def generate_subtitles(clips_dir: str = "data/clips") -> None:
    for clip in os.listdir(clips_dir):
        raw = os.path.join(clips_dir, clip, "raw.mp4")
        if not os.path.exists(raw):
            continue

        result = model.transcribe(raw)
        with open(
            os.path.join(clips_dir, clip, "subtitles.srt"), "w", encoding="utf-8"
        ) as f:
            for i, seg in enumerate(result.get("segments", []), 1):
                f.write(
                    f"{i}\n"
                    f"{_format_ts(seg['start'])} --> {_format_ts(seg['end'])}\n"
                    f"{seg['text'].strip()}\n\n"
                )


if __name__ == "__main__":
    generate_subtitles()
