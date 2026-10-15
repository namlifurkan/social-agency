import math, os, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageChops

D = os.path.dirname(os.path.abspath(__file__))
R = "/Users/furkannamli/Desktop/project/riffiter"
W, H, FPS, SR = 1080, 1920, 30, 22050
BG, FG, MUTED, ACCENT = (18, 14, 12), (242, 235, 229), (195, 188, 184), (214, 80, 47)
random.seed(11)

def font(name, size):
    return ImageFont.truetype({"anton": f"{R}/social/fonts/Anton.ttf", "geist": f"{R}/social/fonts/GeistRegular.ttf",
                               "geistb": f"{R}/social/fonts/GeistSemiBold.ttf", "vt": f"{R}/social/fonts/VT323.ttf",
                               "fraunces": f"{R}/assets/fonts/fraunces-latin-600.ttf"}[name], size)

def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def ease_io(t):
    t = max(0.0, min(1.0, t))
    return 0.5 - math.cos(math.pi * t) / 2

SLOT, NSLOT = 2.0, 4
ORDER = ["hook", "y2021", "rew", "y2007", "ab", "credits", "first", "twist", "card"]
MIN = dict(hook=3.6, y2021=6.0, rew=0.8, y2007=6.0, ab=6.0, credits=6.2, first=4.0, twist=4.4, card=5.0)
LEAD, TAIL = 0.25, 0.6
VO = {}
if os.path.exists(f"{D}/vo/timing.json"):
    import json
    VO = json.load(open(f"{D}/vo/timing.json"))
DUR = dict(MIN)
if VO:
    for k in ORDER:
        if k == "rew" or k not in VO:
            continue
        need = LEAD + VO[k]["dur"] + TAIL - (MIN["rew"] if k == "y2007" else 0)
        DUR[k] = max(MIN[k], need)
AB_START = (LEAD + VO["ab"]["speech_end"] + 0.4) if "ab" in VO else 0.0
DUR["ab"] = AB_START + NSLOT * SLOT + 0.2
T, acc = {}, 0.0
for k in ORDER:
    T[k] = acc
    acc += DUR[k]
T["end"] = acc
VO_AT = {k: (T["rew"] if k == "y2007" else T[k]) + LEAD for k in ORDER if k in VO}

def sw(k, default):
    if k in VO and VO[k].get("split") is not None:
        return VO_AT[k] - T[k] + VO[k]["split"]
    return default

def wt(k, word, default):
    if k in VO and word in VO[k].get("words", {}):
        return VO_AT[k] - T[k] + VO[k]["words"][word]
    return default

# ---------- audio ----------
def pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768

def loudest(path, dur):
    x = pcm(path)
    win, hop = int(dur * SR), SR // 4
    return max(range(0, len(x) - win, hop), key=lambda i: np.sqrt(np.mean(x[i:i + win] ** 2))) / SR

def build_audio():
    g, m, dv = f"{D}/good4u.mp3", f"{D}/misery.mp3", f"{D}/dejavu.mp3"
    gA = loudest(g, T["rew"])
    mA = min(loudest(m, 10.0), 30 - 10.2)
    dA = loudest(dv, T["card"] - T["twist"])
    segs = [
        (g, gA, T["rew"], 0.0, 1.0, ""),
        (g, gA + T["rew"] - 3, 3.0, T["rew"], 0.7, ",areverse,atempo=2,atempo=2,highpass=f=300"),
        (m, mA, T["ab"] - T["y2007"], T["y2007"], 1.0, ""),
    ]
    for k in range(NSLOT):
        src, st = (g, gA + 2 + (k // 2) * SLOT) if k % 2 == 0 else (m, mA + 2 + (k // 2) * SLOT)
        segs.append((src, st, SLOT, T["ab"] + AB_START + k * SLOT, 1.0 / 0.85 if VO else 1.0, ""))
    segs += [
        (g, gA, T["first"] - T["credits"], T["credits"], 0.55, ""),
        (m, mA + 6, T["twist"] - T["first"], T["first"], 1.0, ""),
        (dv, dA, T["card"] - T["twist"], T["twist"], 0.9, ""),
        (g, gA + 3, T["end"] - T["card"], T["card"], 0.8, f",afade=t=out:st={T['end'] - T['card'] - 2.5}:d=2.5"),
    ]
    ins, fc = [], []
    segs = [(a, b, c, d, e * (0.85 if VO else 1.0), x) for a, b, c, d, e, x in segs]
    for k, (src, ss, dur, at, vol, extra) in enumerate(segs):
        ins += ["-i", src]
        fade = "" if "areverse" in extra else f",afade=t=in:d=0.03,afade=t=out:st={dur - 0.05}:d=0.05"
        ms = int(at * 1000)
        fc.append(f"[{k}:a]atrim={ss}:{ss + dur},asetpts=PTS-STARTPTS{fade},volume={vol}{extra},adelay={ms}|{ms}[a{k}]")
    mixed = "".join(f"[a{k}]" for k in range(len(segs))) + f"amix=inputs={len(segs)}:normalize=0,apad,atrim=0:{T['end']}"
    if not VO:
        fc.append(mixed + "[o]")
    else:
        fc.append(mixed + "[mus]")
        vk = []
        for name, at in VO_AT.items():
            j = len(ins) // 2
            ins += ["-i", f"{D}/vo/{name}.mp3"]
            ms = int(at * 1000)
            fc.append(f"[{j}:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.5,adelay={ms}|{ms}[v{j}]")
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
    out = f"{D}/story.wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[o]",
                    "-ar", "44100", "-ac", "2", out], check=True)
    return out

DUCK, DOWN, UP, BRIDGE = 0.16, 0.4, 0.7, 1.2

def duck(src, dst):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "f32le", "-ac", "2", "-ar", "44100", "-"],
                         check=True, capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()
    spans = sorted((VO_AT[k], VO_AT[k] + VO[k]["speech_end"]) for k in VO_AT if k != "ab")
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

# ---------- visual kit ----------
def bw(path):
    im = ImageOps.grayscale(Image.open(path)).convert("RGB")
    return ImageEnhance.Contrast(im).enhance(1.15)

PHOTOS = {k: bw(f"{D}/{k}.jpg") for k in ["olivia-office", "olivia-wh", "olivia-live", "paramore-warped",
                                           "paramore-2007", "hayley-live", "paramore-orig"]}

def kenburns(img, t, dur, focus, z0=1.0, z1=1.12, w=W, h=H):
    sw, sh = img.size
    base = max(w / sw, h / sh)
    z = z0 + (z1 - z0) * ease_io(t / dur)
    cw, ch = w / (base * z), h / (base * z)
    cx = min(max(focus[0] * sw, cw / 2), sw - cw / 2)
    cy = min(max(focus[1] * sh, ch / 2), sh - ch / 2)
    return img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((w, h), Image.BILINEAR)

GRAIN = []
for _ in range(6):
    n = np.random.normal(0, 1, (H // 2, W // 2))
    a = (np.clip(np.abs(n) * 22, 0, 60)).astype(np.uint8)
    v = np.where(n > 0, 255, 0).astype(np.uint8)
    GRAIN.append(Image.fromarray(np.dstack([v, v, v, a]), "RGBA").resize((W, H), Image.NEAREST))

yy, xx = np.mgrid[0:H, 0:W]
rr = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIGNETTE = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8), (np.clip((rr - 0.55) * 210, 0, 170)).astype(np.uint8)]), "RGBA")
SCRIM = Image.fromarray(np.dstack([np.full((H, W, 3), 12, np.uint8),
                                   (np.clip((yy - H * 0.48) / (H * 0.42), 0, 1) * 235).astype(np.uint8)]), "RGBA")
TOPSCRIM = Image.fromarray(np.dstack([np.full((H, W, 3), 12, np.uint8),
                                      (np.clip(1 - yy / (H * 0.3), 0, 1) * 200).astype(np.uint8)]), "RGBA")

def finish(im, f):
    im = im.convert("RGBA")
    im.alpha_composite(VIGNETTE)
    im.alpha_composite(GRAIN[f % len(GRAIN)])
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

SAFE_L, SAFE_R, SAFE_T, SAFE_B = 80, 940, 250, 1500
CX = (SAFE_L + SAFE_R) // 2

def fit(s, f):
    while tw(s, f) > SAFE_R - SAFE_L and f.size > 30:
        f = f.font_variant(size=f.size - 4)
    return f

def ctext(im, y, s, f, fill, a=1.0):
    f = fit(s, f)
    text_a(im, (CX - tw(s, f) / 2, y), s, f, fill, a)

def ltext(im, y, s, f, fill, a=1.0):
    text_a(im, (SAFE_L, y), s, fit(s, f), fill, a)

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
    f = font("anton", 64)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([x, y, x + tw(s, f) + 36, y + 92], fill=ACCENT)
    d.text((x + 18, y + 4), s, font=f, fill=FG)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)

F_STORY = font("anton", 96)

def story_lines(im, t, lines, start=0.25, step=0.0, y=1060, size=None, colors=None):
    f = size or F_STORY
    for s in lines:
        f = fit(s, f)
    for i, s in enumerate(lines):
        a = ease((t - start - i * step) / 0.35)
        text_a(im, (80, y + i * (f.size + 18) + 24 * (1 - a)), s, f, colors[i] if colors else FG, a)

def tape_glitch(im, strength):
    r, g, b, al = im.split()
    sh = int(14 * strength)
    im = Image.merge("RGBA", (ImageChops.offset(r, sh, 0), g, ImageChops.offset(b, -sh, 0), al))
    d = ImageDraw.Draw(im)
    for _ in range(int(10 * strength)):
        y = random.randint(0, H - 40)
        hgt = random.randint(4, 30)
        im.paste(im.crop((0, y, W, y + hgt)), (random.randint(-60, 60), y))
        d.rectangle([0, y, W, y + 2], fill=(255, 255, 255, 60))
    return im

def odometer(im, t, dur, a, b, label):
    v = a + (b - a) * ease_io(t / dur)
    f = font("anton", 330)
    down = b < a
    lo = int(math.ceil(v)) if down else int(math.floor(v))
    frac = (lo - v) if down else (v - lo)
    nxt = lo - 1 if down else lo + 1
    box = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    for val, off in [(lo, -frac), (nxt, 1 - frac)]:
        s = str(val)
        bd.text(((W - bd.textlength(s, font=f)) / 2, 20 + off * 400), s, font=f, fill=ACCENT)
    im.alpha_composite(box, (0, 720))
    text_a(im, (SAFE_L, SAFE_T + 70), label, font("vt", 110), FG)

def photo_scene(key, t, dur, focus, z0, z1, f, dim=0):
    im = kenburns(PHOTOS[key], t, dur, focus, z0, z1).convert("RGBA")
    if dim:
        im.alpha_composite(Image.new("RGBA", (W, H), BG + (dim,)))
    im.alpha_composite(SCRIM)
    return finish(im, f)

# ---------- scenes ----------
def s_hook(t, f):
    im = photo_scene("olivia-office", t, 3.6, (0.5, 0.33), 1.25, 1.1, f)
    wordmark(im)
    ctext(im, 1050, "OLIVIA'S NO. 1 HIT", font("anton", 120), FG, ease((t - 0.25) / 0.3))
    ctext(im, 1200, "WAS MISSING", font("anton", 120), ACCENT, ease((t - 1.2) / 0.3))
    ctext(im, 1350, "2 WRITERS.", font("anton", 120), ACCENT, ease((t - 1.2) / 0.3))
    return im

def s_2021(t, f):
    im = photo_scene("olivia-wh", t, 6.0, (0.36, 0.42), 1.9, 1.65, f)
    wordmark(im)
    chip(im, "MAY 2021", ease((t - 0.1) / 0.3))
    s1 = sw("y2021", 3.0)
    if t < s1:
        story_lines(im, t, ["GOOD 4 U GOES", "STRAIGHT TO NO. 1."], 0.3, 0.3, colors=[FG, ACCENT])
    else:
        story_lines(im, t - s1, ["THEN TIKTOK", "HEARS SOMETHING."], 0.0, 0.3, colors=[FG, ACCENT])
    return im

def s_rew(t, f):
    im = s_2021(DUR["y2021"] - 0.1, f)
    im.alpha_composite(Image.new("RGBA", (W, H), BG + (int(200 * ease(t / 0.2)),)))
    im = tape_glitch(im, 1.0)
    odometer(im, t, 0.8, 2021, 2007, "<< REW")
    return im

def s_2007(t, f):
    s2 = sw("y2007", 3.0)
    if t < s2:
        im = photo_scene("paramore-warped", t, s2, (0.22, 0.38), 1.25, 1.1, f)
    else:
        im = photo_scene("hayley-live", t - s2, DUR["y2007"] - s2, (0.52, 0.26), 2.3, 2.1, f)
    if t < 0.25 or s2 <= t < s2 + 0.2:
        im = tape_glitch(im, 0.7)
    wordmark(im)
    chip(im, "2007", ease((t - 0.1) / 0.3))
    if t < s2:
        story_lines(im, t, ["PARAMORE.", "“MISERY BUSINESS.”"], 0.3, 0.3, colors=[FG, ACCENT])
    else:
        story_lines(im, t - s2, ["HAYLEY WILLIAMS", "IS 18."], 0.0, 0.3, colors=[FG, ACCENT])
    return im

def half(key, t, dur, focus, z0, z1):
    return kenburns(PHOTOS[key], t, dur, focus, z0, z1, W // 2, H).convert("RGBA")

def s_ab(t, f):
    dur = T["credits"] - T["ab"]
    k = int((t - AB_START) / SLOT) if t >= AB_START else -1
    active = k % 2 if k >= 0 else None
    left = half("olivia-office", t, dur, (0.5, 0.36), 1.15, 1.25)
    right = half("paramore-2007", t, dur, (0.47, 0.34), 1.6, 1.75)
    pulse = 1 - ease((t - AB_START - k * SLOT) / 0.25) if k >= 0 else 0
    for side, img in ((0, left), (1, right)):
        if side != active:
            img.alpha_composite(Image.new("RGBA", img.size, BG + (175,)))
        else:
            img = ImageEnhance.Brightness(img).enhance(1 + 0.25 * pulse)
            if side == 0:
                left = img
            else:
                right = img
    im = Image.new("RGBA", (W, H))
    im.paste(left, (0, 0))
    im.paste(right, (W // 2, 0))
    im.alpha_composite(TOPSCRIM)
    im.alpha_composite(SCRIM)
    d = ImageDraw.Draw(im)
    d.rectangle([W // 2 - 4, 600, W // 2 + 4, 1300], fill=ACCENT)
    im = finish(im, f)
    wordmark(im)
    ctext(im, 340, "NOW PLAY THEM", font("anton", 120), FG, ease(t / 0.3))
    ctext(im, 475, "BACK TO BACK.", font("anton", 120), ACCENT, ease(t / 0.3))
    for side, x, title, yr in ((0, 290, "good 4 u", "OLIVIA, 2021"), (1, 750, "Misery Business", "PARAMORE, 2007")):
        on = side == active
        fn = font("anton", 56)
        ctext_x = x - tw(title, fn) / 2
        text_a(im, (ctext_x, 1330), title, fn, FG if on else MUTED)
        f2 = font("geistb", 38)
        text_a(im, (x - tw(yr, f2) / 2, 1410), yr, f2, ACCENT if on else MUTED)
        if on:
            ImageDraw.Draw(im).rectangle([x - 90, 1470, x + 90, 1480], fill=ACCENT)
    return im

def type_line(im, x, y, s, f, fill, p, f_idx):
    n = int(len(s) * max(0.0, min(1.0, p)))
    if n:
        text_a(im, (x, y), s[:n] + ("|" if n < len(s) and f_idx % 10 < 5 else ""), f, fill)

def s_credits(t, f):
    im = photo_scene("olivia-live", t, 6.2, (0.5, 0.5), 1.4, 1.25, f, dim=150)
    wordmark(im)
    chip(im, "AUG 2021", ease((t - 0.1) / 0.3), y=SAFE_T + 85)
    ltext(im, 470, "THE CREDITS CHANGE.", font("anton", 104), FG, ease((t - 0.3) / 0.3))
    ltext(im, 700, "good 4 u", font("anton", 120), FG, ease((t - 0.6) / 0.3))
    ltext(im, 860, "WRITTEN BY", font("geistb", 40), MUTED, ease((t - 0.8) / 0.3))
    fr = font("geistb", 64)
    ltext(im, 930, "Olivia Rodrigo", fr, FG, ease((t - 1.0) / 0.3))
    ltext(im, 1020, "Daniel Nigro", fr, FG, ease((t - 1.15) / 0.3))
    type_line(im, 80, 1110, "+ Hayley Williams", fr, ACCENT, (t - wt("credits", "hayley", 2.0)) / 0.7, f)
    type_line(im, 80, 1200, "+ Josh Farro", fr, ACCENT, (t - wt("credits", "josh", 3.1)) / 0.5, f)
    pg = wt("credits", "writers", 3.6) + 0.5
    ltext(im, 1300, "Paramore's singer and", font("geist", 52), FG, ease((t - pg) / 0.35))
    ltext(im, 1370, "its first guitarist.", font("geist", 52), FG, ease((t - pg) / 0.35))
    return im

def s_first(t, f):
    im = photo_scene("paramore-orig", t, 4.0, (0.93, 0.33), 2.3, 2.5, f)
    wordmark(im)
    chip(im, "14 YEARS LATER", ease((t - 0.1) / 0.3))
    story_lines(im, t, ["THEIR FIRST NO. 1", "AS SONGWRITERS."], 0.35, 0.35, colors=[FG, ACCENT])
    return im

def s_twist(t, f):
    im = photo_scene("olivia-live", 6.2 + t, 10.6, (0.5, 0.5), 1.4, 1.25, f, dim=170)
    wordmark(im)
    ltext(im, 350, "SAME ALBUM.", font("anton", 104), MUTED, ease(t / 0.3))
    ltext(im, 470, "SAME STORY.", font("anton", 104), FG, ease((t - 0.4) / 0.3))
    ltext(im, 700, "deja vu", font("anton", 120), FG, ease((t - 0.8) / 0.3))
    ltext(im, 860, "ALSO WRITTEN BY", font("geistb", 40), MUTED, ease((t - 1.0) / 0.3))
    fr = font("geistb", 64)
    type_line(im, 80, 930, "+ Taylor Swift", fr, ACCENT, (t - wt("twist", "taylor", 1.3)) / 0.5, f)
    type_line(im, 80, 1020, "+ Jack Antonoff", fr, ACCENT, (t - wt("twist", "jack", 2.0)) / 0.5, f)
    type_line(im, 80, 1110, "+ St. Vincent", fr, ACCENT, (t - wt("twist", "st", 2.7)) / 0.5, f)
    ltext(im, 1330, "Because of “Cruel Summer.”", font("geist", 52), FG, ease((t - wt("twist", "because", 3.3)) / 0.35))
    return im

def s_card(t, f):
    dur = T["end"] - T["card"]
    left = half("olivia-office", t, dur, (0.5, 0.36), 1.0, 1.08)
    right = half("hayley-live", t, dur, (0.52, 0.27), 2.4, 2.25)
    im = Image.new("RGBA", (W, H))
    reveal = ease_io(t / 0.45)
    im.paste(left, (0, int(H * (1 - reveal))))
    im.paste(right, (W // 2, int(-H * (1 - reveal))))
    im.alpha_composite(TOPSCRIM)
    im.alpha_composite(SCRIM)
    ImageDraw.Draw(im).rectangle([W // 2 - 4, 640, W // 2 + 4, 1060], fill=ACCENT)
    im = finish(im, f)
    wordmark(im)
    ctext(im, 340, "WHICH ONE", font("anton", 130), FG, ease((t - 0.3) / 0.3))
    ctext(im, 485, "HITS HARDER?", font("anton", 130), ACCENT, ease((t - 0.3) / 0.3))
    a = ease((t - 0.6) / 0.3)
    for x, sub in ((290, "OLIVIA, 2021"), (750, "PARAMORE, 2007")):
        fs = font("anton", 60)
        text_a(im, (x - tw(sub, fs) / 2, 1090), sub, fs, FG, a)
    ctext(im, 1250, "Rate both on Riffiter.", font("anton", 96), FG, ease((t - 1.4) / 0.35))
    ap, gp = Image.open(f"{D}/appstore.png"), Image.open(f"{D}/gplay.png")
    ap, gp = ap.resize((int(ap.width * 0.8), int(ap.height * 0.8))), gp.resize((int(gp.width * 0.8), int(gp.height * 0.8)))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = CX - (ap.width + gp.width + 24) // 2
    lay.paste(ap, (x, 1355), ap)
    lay.paste(gp, (x + ap.width + 24, 1355), gp)
    fl = font("geistb", 32)
    ImageDraw.Draw(lay).text((CX - tw("LINK IN BIO", fl) / 2, 1460), "LINK IN BIO", font=fl, fill=MUTED)
    b = ease((t - 2.4) / 0.35)
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * b)))
    im.alpha_composite(lay)
    return im

SCENES = [("hook", s_hook), ("y2021", s_2021), ("rew", s_rew), ("y2007", s_2007), ("ab", s_ab),
          ("credits", s_credits), ("first", s_first), ("twist", s_twist), ("card", s_card)]

def main():
    audio = build_audio()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", f"{D}/reel.mp4"], stdin=subprocess.PIPE)
    keys = [k for k, _ in SCENES] + ["end"]
    for f in range(int(T["end"] * FPS)):
        t = f / FPS
        for i, (k, fn) in enumerate(SCENES):
            if T[k] <= t < T[keys[i + 1]]:
                im = fn(t - T[k], f)
                break
        p.stdin.write(im.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()

main()
