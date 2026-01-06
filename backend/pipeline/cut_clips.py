import json

default_cfg = {
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

with open(f"{d}/config.json", "w") as f:
    json.dump(default_cfg, f, indent=2)
