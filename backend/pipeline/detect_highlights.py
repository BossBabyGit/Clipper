import librosa, cv2, json, numpy as np, os

VIDEO = "data/vods/input.mp4"
AUDIO = "data/vods/audio.wav"
OUT = "data/highlights/highlights.json"

AUDIO_WINDOW = 0.25
AUDIO_MULT = 2.5
FRAME_SKIP = 6
VISUAL_THRESH = 30
MIN_GAP = 180

WIN_AREA = dict(x=800, y=600, w=300, h=100)

os.makedirs("data/highlights", exist_ok=True)

# Audio
y, sr = librosa.load(AUDIO, sr=None)
hop = int(sr * AUDIO_WINDOW)
rms = librosa.feature.rms(y=y, hop_length=hop)[0]
thr = np.mean(rms) * AUDIO_MULT
audio_hits = [i * hop / sr for i, v in enumerate(rms) if v > thr]

# Video
cap = cv2.VideoCapture(VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
prev = None
visual_hits = []
i = 0

while cap.isOpened():
    if not cap.grab():
        break
    if i % FRAME_SKIP == 0:
        _, f = cap.retrieve()
        roi = f[
            WIN_AREA["y"]:WIN_AREA["y"]+WIN_AREA["h"],
            WIN_AREA["x"]:WIN_AREA["x"]+WIN_AREA["w"]
        ]
        g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        if prev is not None and np.mean(cv2.absdiff(g, prev)) > VISUAL_THRESH:
            visual_hits.append(i / fps)
        prev = g
    i += 1

# Combine
highlights, last = [], -999
for t in audio_hits:
    if any(abs(t - v) < 1.5 for v in visual_hits) and t - last > MIN_GAP:
        highlights.append(int(t))
        last = t

json.dump(highlights, open(OUT, "w"), indent=2)
print("Detected highlights:", highlights)
