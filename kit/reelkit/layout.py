import json, os, shutil, subprocess
from functools import lru_cache

W, H = 1080, 1920
SAFE_L, SAFE_T, SAFE_B = 80, 160, 1500
SAFE_R_HIGH, SAFE_R_LOW, RAIL_FROM = 1000, 940, 900
LOWER_BAND = [(900, SAFE_B)]
HERE = os.path.dirname(os.path.abspath(__file__))


def safe_right(y):
    return SAFE_R_LOW if y >= RAIL_FROM else SAFE_R_HIGH


def center_x(y):
    return (SAFE_L + safe_right(y)) // 2


def load_faces(folder, names):
    cache = os.path.join(folder, "faces.json")
    known = json.load(open(cache)) if os.path.exists(cache) else {}
    todo = [n for n in names if n not in known]
    if todo:
        known.update(_detect([os.path.join(folder, n) for n in todo]))
        json.dump(known, open(cache, "w"), indent=1)
    return known


def _detect(paths):
    if shutil.which("swift"):
        out = subprocess.run(["swift", os.path.join(HERE, "faces.swift"), *paths], capture_output=True, text=True, check=True).stdout
        return {os.path.basename(p): json.loads(b) for p, b in (line.split("\t") for line in out.strip().splitlines())}
    # ponytail: OpenCV Haar cascade off macOS, misses profiles and small faces; swap for a DNN detector if text lands on faces
    import cv2, numpy as np
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    found = {}
    for p in paths:
        im = cv2.imdecode(np.fromfile(p, np.uint8), cv2.IMREAD_GRAYSCALE)
        if im is None:
            found[os.path.basename(p)] = []
            continue
        h, w = im.shape
        boxes = cascade.detectMultiScale(im, 1.1, 6, minSize=(w // 25, w // 25))
        found[os.path.basename(p)] = [[round(x / w, 3), round(y / h, 3), round(bw / w, 3), round(bh / h, 3)] for x, y, bw, bh in (boxes.tolist() if len(boxes) else [])]
    return found


def _crop(sw, sh, w, h, focus, z):
    base = max(w / sw, h / sh)
    cw, ch = w / (base * z), h / (base * z)
    cx = min(max(focus[0] * sw, cw / 2), sw - cw / 2)
    cy = min(max(focus[1] * sh, ch / 2), sh - ch / 2)
    return cx, cy, cw, ch


def _overlap(sw, sh, w, h, cx, cy, cw, ch, faces, bands):
    s = h / ch
    total = 0.0
    for fx, fy, fw, fh in faces:
        top = (fy * sh - (cy - ch / 2)) * s
        bot = top + fh * sh * s
        left = (fx * sw - (cx - cw / 2)) * s
        right = left + fw * sw * s
        if bot - top < 60 or right < 0 or left > w or bot < 0 or top > h:
            continue
        for a, b in bands:
            total += max(0.0, min(bot, b) - max(top, a)) * (min(right, w) - max(left, 0))
    return total


@lru_cache(maxsize=None)
def best_dy(sw, sh, w, h, focus, z0, z1, faces, bands):
    if not faces or not bands:
        return 0.0
    best = None
    for step in range(-60, 61):
        dy = step * sh / 120
        cost = 0.0
        for z in (z0, z1):
            cx, cy, cw, ch = _crop(sw, sh, w, h, focus, z)
            ncy = min(max(cy + dy, ch / 2), sh - ch / 2)
            cost += _overlap(sw, sh, w, h, cx, ncy, cw, ch, faces, bands)
        key = (round(cost), abs(dy))
        if best is None or key < best[0]:
            best = (key, dy)
    return best[1]


def crop_box(sw, sh, w, h, focus, z, dy):
    cx, cy, cw, ch = _crop(sw, sh, w, h, focus, z)
    cy = min(max(cy + dy, ch / 2), sh - ch / 2)
    return int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2)
