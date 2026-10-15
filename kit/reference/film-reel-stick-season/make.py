import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
R = "/Users/furkannamli/Desktop/project/riffiter"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "kit", "reelkit"))
from layout import W, H, center_x
from clips import Clip

FPS, SR = 30, 44100
END = 61.4
XF = 0.4
INK, DIM, ACC, BG = (240, 236, 228), (178, 172, 162), (214, 80, 47), (8, 8, 7)
VID, GEN, ZS, CBS, MEL = "JKrDdsgXuso", "vHxjcDmdVg4", "SB0Man9hJuI", "eGGFH898obA", "4ndMHFh3DOg"
src = lambda k: f"{D}/clips/src-{k}.mp4"
font = lambda name, size: ImageFont.truetype(f"{R}/social/fonts/{name}.ttf", size)
SERIF, BIG, LABEL, CHAP, MARK = font("FrauncesItalic", 54), font("FrauncesItalic", 96), font("GeistRegular", 24), font("GeistRegular", 30), font("GeistSemiBold", 26)

SHOTS = [
    (0.0, 5.0, VID, 54.0, 0.5, 1.0, {}),
    (5.0, 8.4, GEN, 37.25, 0.70, 1.0, {}),
    (8.4, 11.4, VID, 135.0, 0.5, 0.6, {}),
    (11.4, 14.4, VID, 133.0, 0.62, 0.6, {}),
    (14.4, 21.6, VID, 63.0, 0.5, 0.83, {}),
    (21.6, 24.2, VID, 60.0, 0.5, 1.0, {}),
    (24.2, 31.4, MEL, 77.1, 0.5, 1.0, {}),
    (31.4, 35.4, VID, 51.0, 0.5, 0.75, {}),
    (35.4, 41.6, VID, 171.0, 0.45, 0.48, {}),
    (41.6, 46.4, CBS, 235.95, 0.69, 1.0, {"zoom": 1.18, "focus_y": 0.0}),
    (46.4, 50.4, VID, 147.0, 0.55, 0.75, {}),
    (50.4, END, VID, 56.0, 0.5, 0.36, {}),
]
HARD_CUTS = {46.4}

VOICES = [
    (5.3, GEN, 37.55, 46.4),
    (17.0, ZS, 27.15, 28.95),
    (19.1, ZS, 31.45, 33.35),
    (24.4, MEL, 77.3, 84.5),
    (31.7, ZS, 37.5, 43.9),
    (41.8, CBS, 236.15, 239.95),
]

CHAPTERS = [(0.2, 4.8, "STRAFFORD, VERMONT"), (8.4, 11.2, "I.   THE WORD"), (14.4, 17.4, "II.   THE TOWN"),
            (21.6, 24.6, "III.   THE STORE"), (31.4, 34.4, "IV.   THE COST"), (41.6, 42.8, "V.   HOME")]

SUBS = [
    (0.3, 4.9, ["1,094 people live here."], None),
    (2.2, 4.9, ["", "Their song was No. 1 in the UK for seven weeks."], None),
    (5.3, 8.65, ["It's a term that was used by some of the older folks in the town I grew up in"], "NOAH KAHAN"),
    (8.65, 10.65, ["to describe this really miserable time of year,"], None),
    (10.65, 14.2, ["when it's just kind of gray and cold and there's no snow yet."], None),
    (14.6, 16.8, ["Town House, built 1799."], None),
    (17.0, 18.95, ["And this is a place where nobody goes."], "NOAH KAHAN"),
    (19.1, 21.3, ["I know, like, every license plate in the area."], None),
    (21.7, 24.1, ["Coburn's General Store.", "Run by the Coburns, 1977–2024."], None),
    (24.4, 28.9, ["We've probably had, I'd say, half the states in the United States represented"], "MELVIN COBURN"),
    (28.9, 31.3, ["from people that come to see where he grew up."], None),
    (31.7, 36.6, ["I had taken this place that I love, and that people live a very private, quiet life in,"], "NOAH KAHAN"),
    (36.6, 38.3, ["and opened it up to the world."], None),
    (38.7, 41.4, ["July 2025.", "He asks fans to stay off private property."], None),
    (41.8, 43.65, ["The place that you feel like you were moving backwards"], "NOAH KAHAN"),
    (43.65, 46.2, ["is actually the place that sent me forward."], None),
    (52.0, 55.3, ["Stick season starts after Halloween."], None),
]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def fade(t, a, b, k=0.35):
    return ease((t - a) / k) * ease((b - t) / k)


def wrap(text, f, width=840):
    if f.getlength(text) <= width:
        return [text]
    words = text.split(" ")
    best = min(range(1, len(words)), key=lambda i: max(f.getlength(" ".join(words[:i])), f.getlength(" ".join(words[i:]))))
    head, tail = " ".join(words[:best]), " ".join(words[best:])
    return wrap(head, f, width) + wrap(tail, f, width) if f.getlength(head) > width else [head] + wrap(tail, f, width)


def tracked(d, cx, y, s, f, fill, track=8):
    total = sum(f.getlength(c) for c in s) + track * (len(s) - 1)
    x = cx - total / 2
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += f.getlength(c) + track


yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
SCRIM = np.maximum(np.clip((yy - H * 0.44) / (H * 0.24), 0, 1) ** 1.3 * 0.88,
                   np.clip(1 - yy / (H * 0.24), 0, 1) ** 0.8 * 0.80)[..., None]
GRAIN = [np.random.normal(0, 7, (H, W, 1)).astype(np.float32) for _ in range(6)]


def grade(img, f, dim=0.0):
    a = np.asarray(img, dtype=np.float32) / 255
    a = 0.06 + a * 0.88
    lum = a.mean(axis=2, keepdims=True)
    a = (lum + (a - lum) * 0.55) * np.array([1.04, 1.0, 0.93], np.float32)
    s = np.minimum(SCRIM + dim, 1.0)
    a = a * (1 - s) + (BG[0] / 255) * s
    return a * 255 + GRAIN[(f // 2) % len(GRAIN)]


CLIPS = [Clip(src(k), start=s0, dur=(t1 - t0 + XF) * sp + 0.5, focus_x=fx, speed=sp, gray=False, **kw)
         for t0, t1, k, s0, fx, sp, kw in SHOTS]


def picture(t):
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t)
    t0 = SHOTS[i][0]
    cur = np.asarray(CLIPS[i].frame(t - t0), dtype=np.float32)
    if i and t - t0 < XF and t0 not in HARD_CUTS:
        prev = np.asarray(CLIPS[i - 1].frame(t - SHOTS[i - 1][0]), dtype=np.float32)
        k = ease((t - t0) / XF)
        cur = prev * (1 - k) + cur * k
    return cur


ap, gp = Image.open(f"{D}/appstore.png").convert("RGBA"), Image.open(f"{D}/gplay.png").convert("RGBA")
ap, gp = (b.resize((int(b.width * 0.8), int(b.height * 0.8))) for b in (ap, gp))


def text_layer(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def put(fn, a):
        if a <= 0:
            return
        sub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fn(ImageDraw.Draw(sub))
        sub.putalpha(sub.getchannel("A").point(lambda v: int(v * a)))
        lay.alpha_composite(sub)

    tracked(d, center_x(190), 190, "RIFFITER", MARK, DIM, 10)
    for a, b, s in CHAPTERS:
        put(lambda dd, s=s: tracked(dd, center_x(260), 260, s, CHAP, INK), fade(t, a, b))
    cx = center_x(1200)
    for a, b, lines, label in SUBS:
        def draw(dd, lines=lines, label=label):
            y = 1230
            for ln in lines:
                for w in wrap(ln, SERIF) if ln else [""]:
                    dd.text((cx, y), w, font=SERIF, fill=INK, anchor="ma")
                    y += 70
            if label:
                tracked(dd, cx, y + 22, label, LABEL, DIM, 6)
        put(draw, fade(t, a, b))

    def title(dd):
        dd.text((cx, 1130), "Stick Season", font=BIG, fill=INK, anchor="ma")
        tracked(dd, cx, 1270, "NOAH KAHAN  ·  2022", LABEL, DIM, 6)
        dd.rectangle((cx - 18, 1330, cx + 18, 1333), fill=ACC)
    put(title, fade(t, 47.0, 51.6))

    def close(dd):
        dd.text((cx, 1080), "Rate the album on Riffiter.", font=SERIF, fill=INK, anchor="ma")
        x = cx - (ap.width + gp.width + 24) // 2
        lay2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lay2.paste(ap, (x, 1196), ap)
        lay2.paste(gp, (x + ap.width + 24, 1196), gp)
        sub_img = dd._image
        sub_img.alpha_composite(lay2)
        tracked(dd, cx, 1330, "LINK IN BIO", LABEL, DIM, 8)
    put(close, fade(t, 55.7, END + 1))
    return lay


def frame(t, f):
    dim = 0.55 * ease((t - 55.3) / 0.6)
    pic = grade(picture(t), f, dim)
    im = Image.fromarray(np.clip(pic, 0, 255).astype(np.uint8)).convert("RGBA")
    im.alpha_composite(text_layer(t))
    return im.convert("RGB")


def pcm(path, a=None, b=None, norm=None):
    cmd = ["ffmpeg", "-loglevel", "error"] + (["-ss", str(a), "-to", str(b)] if a is not None else []) + ["-i", path]
    if norm:
        cmd += ["-af", f"loudnorm=I={norm}:TP=-2:LRA=11"]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()


def place(out, x, t):
    i = int(t * SR)
    n = min(len(x), len(out) - i)
    out[i:i + n] += x[:n]


def ramp(x, k=0.08):
    n = min(int(k * SR), len(x) // 2)
    env = np.ones(len(x), np.float32)
    env[:n], env[-n:] = np.linspace(0, 1, n), np.linspace(1, 0, n)
    return x * env[:, None]


def build_audio():
    n = int(END * SR)
    out = np.zeros((n, 2), np.float32)
    song = pcm(src(VID), norm=-14)
    bed = np.zeros((n, 2), np.float32)
    a = song[int(3.0 * SR):int(49.4 * SR)]
    place(bed, ramp(a, 0.02), 0.0)
    b = song[int(86.8 * SR):int((86.8 + END - 46.4) * SR)]
    place(bed, ramp(b, 0.02), 46.4)
    spans = []
    for t0, k, s0, s1 in VOICES:
        v = ramp(pcm(src(k), s0, s1, norm=-16))
        place(out, v, t0)
        spans.append((t0, t0 + len(v) / SR))
    merged = []
    for s in spans:
        if merged and s[0] - merged[-1][1] < 1.2:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(s)
    pts = [(0.0, 0.55)]
    for s0, s1 in merged:
        pts += [(s0 - 0.35, 0.42), (s0 - 0.05, 0.12), (s1 + 0.1, 0.12), (s1 + 0.8, 0.42)]
    pts += [(46.3, 0.42), (46.4, 1.0), (END - 2.8, 1.0), (END, 0.0)]
    tt, gg = zip(*pts)
    env = np.interp(np.arange(n) / SR, tt, gg).astype(np.float32)
    out += bed * env[:, None]
    peak = np.abs(out).max()
    if peak > 0.95:
        out *= 0.95 / peak
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-",
                    f"{D}/mix.wav"], input=out.tobytes(), check=True)
    return f"{D}/mix.wav"


def main():
    audio = build_audio()
    only = sys.argv[1:]
    if only:
        for s in only:
            t = float(s)
            frame(t, int(t * FPS)).save(f"{D}/chk/f-{t:05.1f}.jpg", quality=88)
        return
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", f"{D}/reel-raw.mp4"], stdin=subprocess.PIPE)
    for f in range(int(END * FPS)):
        p.stdin.write(frame(f / FPS, f).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    main()
