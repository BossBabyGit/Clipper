import json, subprocess, os

FFMPEG = os.getenv("FFMPEG_PATH", r"C:\ffmpeg\bin\ffmpeg.exe")

def render_clip(clip_dir):
    with open(os.path.join(clip_dir, "config.json")) as f:
        cfg = json.load(f)

    face = cfg["facecam"]
    subs = cfg["subtitles"]

    raw = os.path.join(clip_dir, "raw.mp4")
    srt = os.path.join(clip_dir, "subtitles.srt")
    out = os.path.join(clip_dir, "preview.mp4")

    filter_complex = (
        f"[0:v]crop={face['w']}:{face['h']}:{face['x']}:{face['y']},"
        f"scale=1080:{face['out_height']}[face];"
        "[0:v]crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        f"scale=1080:{1920-face['out_height']}[game];"
        "[face][game]vstack=inputs=2"
    )

    cmd = [
        FFMPEG,
        "-i", raw,
        "-vf",
        f"{filter_complex},subtitles={srt}:force_style="
        f"'FontSize={subs['font_size']},MarginV={subs['margin_v']}'",
        "-c:a", "copy",
        out
    ]

    subprocess.run(cmd, check=True)
