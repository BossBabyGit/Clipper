import os
import tempfile
from pathlib import Path


def _default_data_dir() -> Path:
    """Resolve a writable data directory.

    - Respect an explicit CLIPPER_DATA_DIR env override.
    - Prefer /tmp when running in environments such as Vercel where the
      repository filesystem is read-only.
    - Fall back to the repository-level ``data`` folder when writable.
    """
    env_dir = os.getenv("CLIPPER_DATA_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    if os.getenv("VERCEL"):
        return Path(tempfile.gettempdir()) / "clipper"

    repo_data = Path(__file__).resolve().parent.parent / "data"
    if os.access(repo_data.parent, os.W_OK):
        return repo_data

    return Path(tempfile.gettempdir()) / "clipper"


DATA_DIR = _default_data_dir()
CLIPS_DIR = DATA_DIR / "clips"
VODS_DIR = DATA_DIR / "vods"
HIGHLIGHTS_DIR = DATA_DIR / "highlights"


def ensure_directories() -> None:
    for path in (CLIPS_DIR, VODS_DIR, HIGHLIGHTS_DIR):
        path.mkdir(parents=True, exist_ok=True)
