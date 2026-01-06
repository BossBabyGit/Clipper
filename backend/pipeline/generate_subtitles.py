import whisper, os

model = whisper.load_model("small")

for d in os.listdir("data/clips"):
    raw = f"data/clips/{d}/raw.mp4"
    if not os.path.exists(raw):
        continue

    result = model.transcribe(raw)
    with open(f"data/clips/{d}/subtitles.srt", "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], 1):
            f.write(
                f"{i}\n"
                f"00:00:{seg['start']:.3f} --> 00:00:{seg['end']:.3f}\n"
                f"{seg['text']}\n\n"
            )
