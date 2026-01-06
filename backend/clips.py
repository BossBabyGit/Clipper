import os
from typing import Iterable

from paths import CLIPS_DIR


def list_clips(base: str | os.PathLike[str] = CLIPS_DIR) -> Iterable[str]:
    base = str(base)
    if not os.path.exists(base):
        return []
    return sorted(
        [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
    )
