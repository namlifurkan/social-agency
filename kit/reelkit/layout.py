import json, os, subprocess
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
        out = subprocess.run(["swift", os.path.join(HERE, "faces.swift"), *[os.path.join(folder, n) for n in todo]],
                             capture_output=True, text=True, check=True).stdout
        for line in out.strip().splitlines():
            path, boxes = line.split("\t")
            known[os.path.basename(path)] = json.loads(boxes)
        json.dump(known, open(cache, "w"), indent=1)
    return known


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
