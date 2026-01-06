import json, os

DEFAULT_CONFIG = {
    "facecam": {
        "x": 1000,
        "y": 120,
        "w": 900,
        "h": 500,
        "out_height": 420,
        "enabled": True
    },
    "subtitles": {
        "font_size": 42,
        "margin_v": 560
    }
}

def load_config(clip_dir):
    path = os.path.join(clip_dir, "config.json")
    if not os.path.exists(path):
        save_config(clip_dir, DEFAULT_CONFIG)
    with open(path) as f:
        return json.load(f)

def save_config(clip_dir, cfg):
    with open(os.path.join(clip_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)
