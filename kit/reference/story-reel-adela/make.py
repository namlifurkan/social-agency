import json, math, os, random, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "kit", "reelkit"))
from layout import SAFE_L, SAFE_T, SAFE_B, safe_right, center_x
from clips import Clip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
R = "/Users/furkannamli/Desktop/project/riffiter"
W, H, FPS, SR = 1080, 1920, 30, 22050
BG, FG, MUTED, ACCENT = (18, 14, 12), (242, 235, 229), (195, 188, 184), (214, 80, 47)
random.seed(7)
MV, FAL, ET = f"{D}/clips/src-mv.mp4", f"{D}/clips/src-fallon.mp4", f"{D}/clips/src-et.mp4"

def font(name, size):
    return ImageFont.truetype({"anton": f"{R}/social/fonts/Anton.ttf", "geist": f"{R}/social/fonts/GeistRegular.ttf",
                               "geistb": f"{R}/social/fonts/GeistSemiBold.ttf",
                               "fraunces": f"{R}/assets/fonts/fraunces-latin-600.ttf"}[name], size)

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

# real Tonight Show audio: (key, src_start, src_end); words from ElevenLabs STT on the source
REAL = {"fq": (698.15, 700.45), "k1": (717.75, 722.85), "k2": (724.85, 729.35)}
ORDER = ["hook", "who", "globes", "fallon", "fq", "k1", "k2", "chanel", "now", "card"]
MIN = dict(hook=5.6, who=3.6, globes=5.9, fallon=3.8, chanel=8.6, now=4.6, card=5.8)
LEAD, TAIL = 0.25, 0.15
VO = json.load(open(f"{D}/vo/timing.json"))
DUR = {}
for k in ORDER:
    DUR[k] = REAL[k][1] - REAL[k][0] if k in REAL else max(MIN[k], LEAD + VO[k]["dur"] + TAIL)
T, acc = {}, 0.0
for k in ORDER:
    T[k] = acc
    acc += DUR[k]
T["end"] = acc
VO_AT = {k: T[k] + LEAD for k in ORDER if k in VO}

def sw(k, default, i=0):
    if len(VO[k].get("splits", [])) > i:
        return LEAD + VO[k]["splits"][i]
    return default

def wt(k, word, default):
    return LEAD + VO[k]["words"][word] if word in VO[k].get("words", {}) else default

def rt(k, src_t):
    return src_t - REAL[k][0]

# ---------- audio ----------
SONG = f"{D}/kidman.mp3"

def pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768

def loudest(path, dur):
    x = pcm(path)
    win, hop = int(min(dur, 28) * SR), SR // 4
    return max(range(0, len(x) - win, hop), key=lambda i: np.sqrt(np.mean(x[i:i + win] ** 2))) / SR

def fits(start, dur):
    return max(0.0, min(start, 29.9 - dur))

def build_audio():
    tA = loudest(SONG, 8.0)
    hook = DUR["hook"]
    bed = T["fq"] - T["who"]
    tail = T["end"] - T["chanel"]
    segs = [
        (fits(tA, hook), hook, 0.0, 0.85, f",afade=t=out:st={hook - 0.25}:d=0.25"),
        (0.0, bed, T["who"], 0.7, f",afade=t=in:d=0.2,afade=t=out:st={bed - 0.5}:d=0.5"),
        (fits(tA - 3.0, tail), tail, T["chanel"], 0.9, f",afade=t=in:d=0.3,afade=t=out:st={tail - 2.4}:d=2.4"),
    ]
    ins, fc = [], []
    for k, (ss, dur, at, vol, extra) in enumerate(segs):
        ins += ["-i", SONG]
        ms = int(at * 1000)
        fc.append(f"[{k}:a]aresample=44100,aformat=channel_layouts=stereo,atrim={ss}:{ss + dur},asetpts=PTS-STARTPTS"
                  f",afade=t=in:d=0.03{extra},volume={vol * 0.45},adelay={ms}|{ms}[a{k}]")
    fc.append("".join(f"[a{k}]" for k in range(len(segs))) + f"amix=inputs={len(segs)}:normalize=0,apad,atrim=0:{T['end']}[mus]")
    vk, j = [], len(segs) - 1
    for name, at in VO_AT.items():
        j += 1
        ins += ["-i", f"{D}/vo/{name}.mp3"]
        ms = int(max(0.0, at - VO[name].get("lead_silence", 0.0)) * 1000)
        fc.append(f"[{j}:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.5,adelay={ms}|{ms}[v{j}]")
        vk.append(f"[v{j}]")
    for name, (a, b) in REAL.items():
        j += 1
        ins += ["-ss", str(a), "-t", str(b - a), "-i", FAL]
        ms = int(T[name] * 1000)
        fc.append(f"[{j}:a]aresample=44100,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5,"
                  f"afade=t=in:d=0.08,afade=t=out:st={b - a - 0.12}:d=0.12,volume=1.25,adelay={ms}|{ms}[v{j}]")
        vk.append(f"[v{j}]")
    fc.append("".join(vk) + f"amix=inputs={len(vk)}:normalize=0,apad,atrim=0:{T['end']}[vo]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(fc),
                    "-map", "[mus]", "-ar", "44100", "-ac", "2", f"{D}/mus.wav",
                    "-map", "[vo]", "-ar", "44100", "-ac", "2", f"{D}/vo.wav"], check=True)
    duck(f"{D}/mus.wav", f"{D}/mus-duck.wav")
    out = f"{D}/story.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{D}/mus-duck.wav", "-i", f"{D}/vo.wav",
                    "-filter_complex", "[0:a][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.95[o]",
                    "-map", "[o]", "-ar", "44100", "-ac", "2", out], check=True)
    return out

DUCK, DOWN, UP, BRIDGE = 0.22, 0.4, 0.7, 1.2

def duck(src, dst):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "f32le", "-ac", "2", "-ar", "44100", "-"],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
    spans = sorted((VO_AT[k], VO_AT[k] + VO[k]["speech_end"]) for k in VO_AT)
    merged = []
    for s, e in spans:
        if merged and s - merged[-1][1] < BRIDGE:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    t = np.arange(len(x)) / 44100
    g = np.ones(len(x), dtype=np.float32)
    for s, e in merged:
        down = np.clip((t - (s - DOWN - 0.05)) / DOWN, 0, 1)
        up = np.clip(((e + 0.15 + UP) - t) / UP, 0, 1)
        w = np.minimum(down, up)
        w = 0.5 - np.cos(np.pi * w) / 2
        g = np.minimum(g, 1 - (1 - DUCK) * w)
    x *= g[:, None]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", "44100", "-i", "-",
                    "-c:a", "pcm_s16le", dst], input=x.tobytes(), check=True)

# ---------- shots ----------
# (path, src_start, src_dur, focus_x, speed, zoom, focus_y)
SHOTS = {
    "mv-face": (MV, 0.5, 2.9, 0.5, 1.0, 1.0, 0.5),
    "et-kiss": (ET, 76.5, 3.4, 0.5, 1.0, 1.0, 0.5),
    "mv-keys": (MV, 13.0, 3.0, 0.5, 0.8, 1.0, 0.5),
    "mv-face2": (MV, 42.2, 3.3, 0.5, 0.54, 1.0, 0.5),
    "mv-face3": (MV, 46.0, 1.9, 0.5, 0.6, 1.0, 0.5),
    "fal-wide": (FAL, 694.15, 3.95, 0.68, 1.0, 1.0, 0.5),
    "fq-wide": (FAL, 698.15, 700.17 - 698.15, 0.68, 1.0, 1.0, 0.5),
    "fq-close": (FAL, 700.17, 700.45 - 700.17, 0.46, 1.0, 1.0, 0.5),
    "k1-wide": (FAL, 717.75, 720.22 - 717.75, 0.0, 1.0, 1.0, 0.5),
    "k1-close": (FAL, 720.22, 722.85 - 720.22, 0.46, 1.0, 1.0, 0.5),
    "tablet": (FAL, 712.0, 3.5, 0.354, 1.0, 1.0, 0.5),
    "k2-close": (FAL, 727.75, 729.35 - 727.75, 0.46, 1.0, 1.0, 0.5),
    "et-k60": (ET, 60.4, 1.5, 0.5, 1.0, 1.0, 0.5),
    "et-k85": (ET, 85.5, 0.9, 0.5, 1.0, 1.0, 0.5),
    "et-dua": (ET, 54.5, 3.0, 0.5, 1.0, 1.0, 0.5),
    "et-pedro": (ET, 58.0, 1.5, 0.5, 1.0, 1.0, 0.5),
    "mv-swing": (MV, 187.0, 1.4, 0.5, 0.3, 1.0, 0.5),
    "mv-light": (MV, 190.4, 2.4, 0.5, 0.41, 1.0, 0.5),
}
CLIPS = {}
GRAY = os.environ.get("GRAY") == "1"

def shot(name, t):
    if name not in CLIPS:
        p, s, d, fx, sp, z, fy = SHOTS[name]
        CLIPS[name] = Clip(p, start=s, dur=d, focus_x=fx, speed=sp, gray=GRAY, zoom=z, focus_y=fy)
    im = CLIPS[name].frame(t)
    return (im if GRAY else grade(im)).convert("RGBA")

WARM = np.array([1.04, 1.0, 0.93], dtype=np.float32)

def grade(im, sat=0.85):
    a = np.asarray(im, dtype=np.float32) / 255
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    a = lum[..., None] + (a - lum[..., None]) * sat
    a = (0.05 + a * 0.9) * WARM
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGB")

GRAIN = []
for _ in range(6):
    n = np.random.normal(0, 1, (H // 2, W // 2))
    a = (np.clip(np.abs(n) * 14, 0, 40)).astype(np.uint8)
    v = np.where(n > 0, 255, 0).astype(np.uint8)
    GRAIN.append(Image.fromarray(np.dstack([v, v, v, a]), "RGBA").resize((W, H), Image.NEAREST))

yy, xx = np.mgrid[0:H, 0:W]
rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGNETTE = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (np.clip((rr - 0.55) * 210, 0, 170)).astype(np.uint8)]), "RGBA")
SCRIM = Image.fromarray(np.dstack([np.full((H, W, 3), 12, np.uint8),
                                   (np.clip((yy - H * 0.46) / (H * 0.40), 0, 1) * 238).astype(np.uint8)]), "RGBA")

def finish(im, f, dim=0):
    if dim:
        im.alpha_composite(Image.new("RGBA", (W, H), BG + (dim,)))
    im.alpha_composite(SCRIM)
    im.alpha_composite(VIGNETTE)
    im.alpha_composite(GRAIN[(f // 2) % len(GRAIN)])
    return im

def text_a(im, pos, s, f, fill, a=1.0):
    if a <= 0:
        return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text(pos, s, font=f, fill=fill)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)

def tw(s, f):
    return ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(s, font=f)

CX = center_x(SAFE_B)

def fit(s, f, y=SAFE_B, x0=SAFE_L):
    while tw(s, f) > safe_right(y + f.size) - x0 and f.size > 30:
        f = f.font_variant(size=f.size - 4)
    return f

def ctext(im, y, s, f, fill, a=1.0):
    f = fit(s, f, y)
    text_a(im, (center_x(y + f.size) - tw(s, f) / 2, y), s, f, fill, a)

def wordmark(im, y=SAFE_T + 5, size=56):
    d = ImageDraw.Draw(im)
    f = font("fraunces", size)
    wa, wb = tw("Riffiter", f), tw(".com", f)
    x = CX - (wa + wb) / 2
    d.text((x, y), "Riffiter", font=f, fill=FG)
    d.text((x + wa, y), ".com", font=f, fill=ACCENT)

def chip(im, s, a, x=SAFE_L, y=940):
    if a <= 0:
        return
    f = font("anton", 60)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([x, y, x + tw(s, f) + 36, y + 88], fill=ACCENT)
    d.text((x + 18, y + 4), s, font=f, fill=FG)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)

F_STORY = font("anton", 100)

def lines(im, t, rows, start=0.2, step=0.25, y=1100, colors=None, size=None):
    f = size or F_STORY
    for s in rows:
        f = fit(s, f, y + len(rows) * (f.size + 18))
    for i, s in enumerate(rows):
        a = ease((t - start - i * step) / 0.35)
        text_a(im, (SAFE_L, y + i * (f.size + 18) + 24 * (1 - a)), s, f, colors[i] if colors else FG, a)

def shake(im, t, start, amount=22):
    k = 1 - ease((t - start) / 0.35)
    if t < start or k <= 0:
        return im
    dx, dy = int(random.uniform(-1, 1) * amount * k), int(random.uniform(-1, 1) * amount * k)
    out = Image.new("RGBA", im.size, BG + (255,))
    out.paste(im, (dx, dy))
    return out

def wrap(s, f, width):
    out, cur = [], ""
    for w in s.split():
        nxt = (cur + " " + w).strip()
        if tw(nxt, f) <= width or not cur:
            cur = nxt
        else:
            out.append(cur)
            cur = w
    return out + [cur]

def quote(im, t, who, s, t0, t1, y=1160):
    a = min(ease((t - t0) / 0.15), 1 - ease((t - t1 + 0.15) / 0.15))
    if a <= 0:
        return
    f = font("anton", 76)
    text_a(im, (SAFE_L, y - 56), who, font("geistb", 30), ACCENT, a)
    for i, row in enumerate(wrap(s, f, safe_right(y + 200) - SAFE_L)):
        text_a(im, (SAFE_L, y + i * 92), row, f, FG, a)

# ---------- scenes ----------
def s_hook(t, f):
    s1 = sw("hook", 2.65)
    if t < s1:
        im = finish(shot("mv-face", t), f)
        wordmark(im)
        lines(im, t, ["THIS SONG IS CALLED", "“NICOLE KIDMAN.”"], 0.15, wt("hook", "nicole", 1.3) - 0.35,
              y=1180, colors=[FG, ACCENT])
        return im
    im = finish(shot("et-kiss", t - s1), f)
    wordmark(im)
    lines(im, t - s1, ["NICOLE KIDMAN", "JUST LIP-SYNCED IT."], 0.0, 0.45, y=1180, colors=[FG, ACCENT])
    return shake(im, t, s1, 20)

def s_who(t, f):
    im = finish(shot("mv-keys", t), f)
    wordmark(im)
    lines(im, t, ["BY ADÉLA.", "FROM SLOVAKIA."], 0.2, wt("who", "singer", 1.2) - 0.3, y=1260, colors=[ACCENT, FG])
    return im

def s_globes(t, f):
    s1 = sw("globes", 2.8)
    im = finish(shot("mv-face2", t), f)
    wordmark(im)
    if t < s1:
        lines(im, t, ["SHE WROTE IT AFTER", "A GOLDEN GLOBES", "PARTY."], 0.2, 0.35, y=1200, colors=[FG, ACCENT, ACCENT], size=font("anton", 92))
        return im
    lines(im, t - s1, ["THAT NIGHT, SHE FELT", "LIKE NICOLE KIDMAN."], 0.0, 0.5, y=1260, colors=[FG, ACCENT], size=font("anton", 92))
    return im

def s_fallon(t, f):
    im = finish(shot("fal-wide", t), f)
    wordmark(im)
    chip(im, "SEPT 2026", ease((t - 0.1) / 0.3))
    lines(im, t, ["JIMMY FALLON", "ASKS KIDMAN."], wt("fallon", "jimmy", 0.9) - 0.1, 0.5, colors=[FG, ACCENT])
    return im

def s_fq(t, f):
    cut = 700.17 - 698.15
    im = finish(shot("fq-wide", t) if t < cut else shot("fq-close", t - cut), f)
    wordmark(im)
    quote(im, t, "JIMMY FALLON", "“DO YOU KNOW ADÉLA?”", rt("fq", 698.25), rt("fq", 699.6))
    quote(im, t, "NICOLE KIDMAN", "“YES.”", rt("fq", 700.1), 9)
    return im

def s_k1(t, f):
    cut = 720.22 - 717.75
    im = finish(shot("k1-wide", t) if t < cut else shot("k1-close", t - cut), f)
    wordmark(im)
    quote(im, t, "NICOLE KIDMAN", "“I CAN'T BELIEVE IT.”", rt("k1", 717.8), rt("k1", 718.98))
    quote(im, t, "NICOLE KIDMAN", "“SHE WROTE A SONG CALLED NICOLE KIDMAN.”", rt("k1", 719.0), rt("k1", 721.28))
    quote(im, t, "NICOLE KIDMAN", "“I'M LIKE, WHO IS THAT PERSON?”", rt("k1", 721.3), 9)
    return im

def s_k2(t, f):
    cut = rt("k2", 727.75)
    im = finish(shot("tablet", t) if t < cut else shot("k2-close", t - cut), f)
    wordmark(im)
    quote(im, t, "NICOLE KIDMAN", "“IN HER VIDEO, SHE DID ALL THE FILMS I'VE DONE.”", rt("k2", 724.9), rt("k2", 727.72))
    quote(im, t, "NICOLE KIDMAN", "“HALF OF THEM I CAN'T EVEN REMEMBER.”", rt("k2", 727.76), 9)
    return im

def s_chanel(t, f):
    s1 = sw("chanel", 3.8)
    seq = [("et-k60", 0.0, 1.5, 0.0), ("et-k85", 1.5, 2.4, 0.0), ("et-kiss", 2.4, s1, 1.0), ("et-dua", s1, s1 + 2.6, 0.0),
           ("et-pedro", s1 + 2.6, s1 + 4.1, 0.0), ("et-kiss", s1 + 4.1, 99, 2.4)]
    for name, a, b, off in seq:
        if a <= t < b:
            im = finish(shot(name, t - a + off), f)
            break
    wordmark(im)
    chip(im, "OCT 6 · PARIS", ease((t - 0.1) / 0.3))
    if t < s1:
        lines(im, t, ["AT CHANEL'S SHOW,", "SHE LIP-SYNCS IT."], 0.3, wt("chanel", "she", 2.3) - 0.3, colors=[FG, ACCENT])
        return im
    lines(im, t - s1, ["+ DUA LIPA"], 0.0, 0, colors=[ACCENT])
    if t >= wt("chanel", "pedro", s1 + 1.3) - 0.1:
        lines(im, t - wt("chanel", "pedro", s1 + 1.3) + 0.1, ["", "+ PEDRO PASCAL"], 0.0, 0, colors=[ACCENT, ACCENT])
    return im

def s_now(t, f):
    im = finish(shot("mv-swing", t), f)
    wordmark(im)
    chip(im, "THIS WEEK", ease((t - 0.1) / 0.3))
    ctext(im, 1130, "NO. 2", font("anton", 240), ACCENT, ease((t - wt("now", "two", 1.6) + 0.1) / 0.2))
    ctext(im, 1400, "ON SPOTIFY WORLDWIDE", font("anton", 80), FG, ease((t - wt("now", "spotify", 2.2)) / 0.3))
    return shake(im, t, wt("now", "two", 1.6), 18)

def s_card(t, f):
    im = finish(shot("mv-light", t), f, dim=60)
    wordmark(im)
    ctext(im, 920, "IS IT A HIT?", font("anton", 120), FG, ease((t - 0.3) / 0.3))
    ctext(im, 1080, "Rate Nicole Kidman on Riffiter.", font("anton", 66), FG, ease((t - 1.6) / 0.35))
    ap, gp = Image.open(f"{D}/appstore.png"), Image.open(f"{D}/gplay.png")
    ap, gp = ap.resize((int(ap.width * 0.8), int(ap.height * 0.8))), gp.resize((int(gp.width * 0.8), int(gp.height * 0.8)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = CX - (ap.width + gp.width + 24) // 2
    lay.paste(ap, (x, 1190), ap)
    lay.paste(gp, (x + ap.width + 24, 1190), gp)
    ld = ImageDraw.Draw(lay)
    ff_, fb_ = font("geistb", 36), font("geistb", 30)
    s = "Follow for a new song story every day."
    ld.text((CX - tw(s, ff_) / 2, 1320), s, font=ff_, fill=FG)
    ld.text((CX - tw("LINK IN BIO", fb_) / 2, 1384), "LINK IN BIO", font=fb_, fill=MUTED)
    b = ease((t - 2.2) / 0.35)
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * b)))
    im.alpha_composite(lay)
    return im

SCENES = [("hook", s_hook), ("who", s_who), ("globes", s_globes), ("fallon", s_fallon), ("fq", s_fq), ("k1", s_k1),
          ("k2", s_k2), ("chanel", s_chanel), ("now", s_now), ("card", s_card)]

def frame_at(t, f):
    keys = [k for k, _ in SCENES] + ["end"]
    for i, (k, fn) in enumerate(SCENES):
        if T[k] <= t < T[keys[i + 1]]:
            return fn(t - T[k], f)
    return SCENES[-1][1](T["end"] - T["card"] - 0.01, f)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        os.makedirs(f"{D}/stills", exist_ok=True)
        for s in sys.argv[2:]:
            t = float(s)
            CLIPS.clear()
            frame_at(t, int(t * FPS)).convert("RGB").save(f"{D}/stills/{t:05.2f}.jpg", quality=85)
        print({k: round(v, 2) for k, v in T.items()})
        return
    audio = build_audio()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", f"{D}/reel-raw{'-bw' if GRAY else ''}.mp4"], stdin=subprocess.PIPE)
    for f in range(int(T["end"] * FPS)):
        p.stdin.write(frame_at(f / FPS, f).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print({k: round(v, 2) for k, v in T.items()})

main()
