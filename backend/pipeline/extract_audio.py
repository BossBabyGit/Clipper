import os
import subprocess

FFMPEG = os.getenv("FFMPEG_PATH", "ffmpeg")


def extract_audio(video_path: str, output_audio: str, sample_rate: int = 44100) -> None:
    """Extract a mono WAV track from the provided video."""
    os.makedirs(os.path.dirname(output_audio), exist_ok=True)
    subprocess.run(
        [FFMPEG, "-i", video_path, "-ac", "1", "-ar", str(sample_rate), output_audio],
        check=True,
    )


if __name__ == "__main__":
    video = os.getenv("VIDEO", "data/vods/input.mp4")
    audio = os.getenv("AUDIO", "data/vods/audio.wav")
    extract_audio(video, audio)
    print("Audio extracted")
