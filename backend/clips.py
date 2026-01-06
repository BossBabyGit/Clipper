import os

def list_clips(base="data/clips"):
    if not os.path.exists(base):
        return []
    return sorted([
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d))
    ])
