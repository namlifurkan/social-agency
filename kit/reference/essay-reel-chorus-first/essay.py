import json, math, os, random, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "kit", "reelkit"))
from layout import SAFE_L, SAFE_T, SAFE_B, safe_right, center_x, load_faces, best_dy, crop_box
from clips import Clip
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
R = "/Users/furkannamli/Desktop/project/riffiter"
W, H, FPS, SR = 1080, 1920, 30, 22050
BG, FG, MUTED, ACCENT = (18, 14, 12), (242, 235, 229), (195, 188, 184), (214, 80, 47)
PAPER, INK = (236, 231, 222), (28, 24, 22)
SUB_Y = 1180
SUB_BAND = [(SUB_Y - 30, SUB_Y + 150)]
random.seed(7)


def font(name, size):
    return ImageFont.truetype({"anton": f"{R}/social/fonts/Anton.ttf", "geist": f"{R}/social/fonts/GeistRegular.ttf",
                               "geistb": f"{R}/social/fonts/GeistSemiBold.ttf",
                               "fraunces": f"{R}/assets/fonts/fraunces-latin-600.ttf"}[name], size)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def tw(s, f):
    return ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(s, font=f)


WARM = np.array([1.04, 1.0, 0.93], dtype=np.float32)


def grade(im, gray=False, sat=0.85):
    a = np.asarray(im.convert("RGB"), dtype=np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    a = lum[..., None] + (a - lum[..., None]) * (0.0 if gray else sat)
    if gray:
        a = np.clip((a - 0.5) * 1.12 + 0.5, 0, 1)
    a = (0.05 + a * 0.9) * (np.ones(3, np.float32) if gray else WARM)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGB")


GRAIN = []
for _ in range(6):
    n = np.random.normal(0, 1, (H // 2, W // 2))
    a = (np.clip(np.abs(n) * 12, 0, 34)).astype(np.uint8)
    v = np.where(n > 0, 255, 0).astype(np.uint8)
    GRAIN.append(Image.fromarray(np.dstack([v, v, v, a]), "RGBA").resize((W, H), Image.NEAREST))
yy, xx = np.mgrid[0:H, 0:W]
rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGNETTE = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (np.clip((rr - 0.55) * 190, 0, 150)).astype(np.uint8)]), "RGBA")
BAND = Image.fromarray(np.dstack([np.full((H, W, 3), 10, np.uint8),
                                  (np.clip(1 - np.abs(yy - (SUB_Y + 50)) / 260, 0, 1) ** 1.5 * 120).astype(np.uint8)]), "RGBA")


def finish(im, f, band=True):
    if band:
        im.alpha_composite(BAND)
    im.alpha_composite(VIGNETTE)
    im.alpha_composite(GRAIN[(f // 2) % len(GRAIN)])
    return im


def wordmark(im, y=SAFE_T + 5, size=52, dark=False):
    d = ImageDraw.Draw(im)
    f = font("fraunces", size)
    wa, wb = tw("Riffiter", f), tw(".com", f)
    x = center_x(y) - (wa + wb) / 2
    d.text((x, y), "Riffiter", font=f, fill=INK if dark else FG)
    d.text((x + wa, y), ".com", font=f, fill=ACCENT)


def wrap(s, f, width):
    out, cur = [], ""
    for w in s.split():
        nxt = f"{cur} {w}".strip()
        if cur and tw(nxt, f) > width:
            out.append(cur)
            cur = w
        else:
            cur = nxt
    return out + ([cur] if cur else [])


def subtitle(im, s, a=1.0, dark=False, y=SUB_Y, cx=None):
    if a <= 0 or not s:
        return
    f = font("geistb", 46)
    rows = wrap(s, f, 780)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, row in enumerate(rows):
        x = (cx or center_x(y + 60)) - tw(row, f) / 2
        d.text((x, y + i * 60), row, font=f, fill=INK if dark else FG)
    if not dark:
        sh = lay.copy()
        sh.putalpha(sh.getchannel("A").point(lambda v: int(v * 0.85)))
        sh = Image.composite(Image.new("RGBA", im.size, (0, 0, 0, 255)), Image.new("RGBA", im.size, (0, 0, 0, 0)), sh.getchannel("A"))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)


class Still:
    def __init__(self, name, focus=(0.5, 0.45), gray=False, z=(1.0, 1.07)):
        self.name, self.focus, self.gray, self.z = name, focus, gray, z
        self.src = Image.open(f"{D}/img/{name}").convert("RGB")
        faces = FACES.get(name, [])
        sw, sh = self.src.size
        self.dy = best_dy(sw, sh, W, H, tuple(focus), z[0], z[1], tuple(tuple(b) for b in faces), tuple(SUB_BAND + [(140, 250)]))
        self.cache = {}

    def frame(self, p):
        z = self.z[0] + (self.z[1] - self.z[0]) * p
        key = round(z, 3)
        if key not in self.cache:
            sw, sh = self.src.size
            box = crop_box(sw, sh, W, H, self.focus, z, self.dy)
            self.cache = {key: grade(self.src.crop(box).resize((W, H), Image.LANCZOS), self.gray)}
        return self.cache[key].convert("RGBA")


class Video:
    def __init__(self, name, start, focus_x=0.5, gray=False, speed=1.0, zoom=1.0, focus_y=0.5):
        self.clip = Clip(f"{D}/clips/{name}.mp4", start=start, dur=6.0, focus_x=focus_x, gray=False, speed=speed, zoom=zoom, focus_y=focus_y)
        self.gray = gray

    def frame_t(self, t):
        return grade(self.clip.frame(t), self.gray).convert("RGBA")


FACES = {}


def load_all_faces(names):
    FACES.update(load_faces(f"{D}/img", sorted(set(names))))
