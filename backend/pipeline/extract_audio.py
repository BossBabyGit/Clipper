import subprocess, os

FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"
VIDEO = "data/vods/input.mp4"
AUDIO = "data/vods/audio.wav"

os.makedirs("data/vods", exist_ok=True)

subprocess.run([
    FFMPEG, "-i", VIDEO, "-ac", "1", "-ar", "44100", AUDIO
])

print("Audio extracted")
