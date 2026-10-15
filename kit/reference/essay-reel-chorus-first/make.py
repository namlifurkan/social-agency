from essay import *

C = lambda n: f"{D}/clips/{n}.mp4"
BILLIE = C("src-billie")
AUD = {"billie": BILLIE, "unholy": f"{D}/clips/aud-unholy.m4a", "charli": C("src-charli"), "roxette": C("src-roxette"),
       "aperture": f"{D}/clips/aud-aperture.m4a"}

SHORT = os.environ.get("CUT") == "shorts"
ORDER = ["hook", "billie", "jelly", "unholy", "hit", "unholy2", "study", "skip", "charli", "roxette", "flip", "card"]
if SHORT:
    ORDER.remove("roxette")
MIN = dict(hook=3.4, billie=6.4, jelly=5.2, unholy=3.0, hit=2.6, unholy2=3.8, study=7.6, skip=7.0, charli=6.6,
           roxette=6.6, flip=6.6, card=6.9 if os.environ.get("CUT") == "shorts" else 7.4)
LEAD, TAIL = 0.25, 0.15
VO = json.load(open(f"{D}/vo/timing.json"))
DUR = {k: max(MIN[k], LEAD + VO[k]["dur"] + TAIL) if k in VO else MIN[k] for k in ORDER}
T, acc = {}, 0.0
for k in ORDER:
    T[k] = acc
    acc += DUR[k]
T["end"] = acc
VO_AT = {k: T[k] + LEAD for k in ORDER if k in VO}


def sw(k, default, i=0):
    return LEAD + VO[k]["splits"][i] if len(VO[k].get("splits", [])) > i else default


def wt(k, word, default):
    return LEAD + VO[k]["words"][word] if word in VO[k].get("words", {}) else default


def part(k, t):
    text = dict(BEATS)[k]
    parts = text.split(" | ")
    i = sum(1 for j in range(len(parts) - 1) if t >= sw(k, 99, j) - 0.05)
    return parts[i]


BEATS = [l for l in json.load(open(f"{D}/beats.json"))]

# ---------- audio ----------
def pcm(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def loudest(path, dur, lo=0.0, hi=None):
    x = pcm(path)
    a, b = int(lo * SR), int((hi or len(x) / SR) * SR)
    win, hop = int(dur * SR), SR // 4
    return max(range(a, b - win, hop), key=lambda i: np.sqrt(np.mean(x[i:i + win] ** 2))) / SR


def build_audio():
    t_hit, t_ch, t_fl = T["hit"], T["charli"], T["flip"]
    t_rx = T.get("roxette", t_fl)
    t_off = T["unholy"] + 0.9
    kc = loudest(AUD["charli"], t_rx - t_ch + 1, 40, 200)
    kr = 0.0 if SHORT else loudest(AUD["roxette"], t_fl - t_rx + 1, 30, 200)
    segs = [
        (AUD["billie"], 0.0, t_off, 0.0, 1.0, f",afade=t=out:st={t_off - 0.8}:d=0.8"),
        (AUD["unholy"], 0.0, t_ch - t_hit + 0.5, t_hit, 1.4, f",afade=t=out:st={t_ch - t_hit - 0.3}:d=0.8"),
        (AUD["charli"], kc, t_rx - t_ch + 0.5, t_ch - 0.3, 0.9, f",afade=t=in:d=0.5,afade=t=out:st={t_rx - t_ch}:d=0.8"),
        *([] if SHORT else [(AUD["roxette"], kr, t_fl - t_rx + 0.5, t_rx - 0.3, 2.2, f",afade=t=in:d=0.5,afade=t=out:st={t_fl - t_rx}:d=0.8")]),
        (AUD["aperture"], 0.0, T["end"] - t_fl + 0.3, t_fl - 0.3, 1.1, f",afade=t=in:d=0.4,afade=t=out:st={T['end'] - t_fl - 1.8}:d=2.0"),
    ]
    ins, fc = [], []
    for k, (src, ss, dur, at, vol, extra) in enumerate(segs):
        ins += ["-i", src]
        ms = int(max(0.0, at) * 1000)
        fc.append(f"[{k}:a]aresample=44100,aformat=channel_layouts=stereo,atrim={ss}:{ss + dur},asetpts=PTS-STARTPTS"
                  f",afade=t=in:d=0.03{extra},volume={vol * 0.7},adelay={ms}|{ms}[a{k}]")
    fc.append("".join(f"[a{k}]" for k in range(len(segs))) + f"amix=inputs={len(segs)}:normalize=0,apad,atrim=0:{T['end']}[mus]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(fc),
                    "-map", "[mus]", "-ar", "44100", "-ac", "2", f"{D}/mus.wav"], check=True)
    ins, fc, vk = [], [], []
    for j, (name, at) in enumerate(VO_AT.items()):
        ins += ["-i", f"{D}/vo/{name}.mp3"]
        ms = int(max(0.0, at - VO[name].get("lead_silence", 0.0)) * 1000)
        fc.append(f"[{j}:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.5,adelay={ms}|{ms}[v{j}]")
        vk.append(f"[v{j}]")
    fc.append("".join(vk) + f"amix=inputs={len(vk)}:normalize=0,apad,atrim=0:{T['end']}[vo]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(fc),
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
# name: (clip, src_start, focus_x, gray, speed)
SHOTS = {
    "harry-close": ("src-aperture", 124.0, 0.5, False, 1.0),
    "harry-face": ("src-aperture", 95.5, 0.5, False, 1.0),
    "harry-room": ("src-aperture", 86.0, 0.5, False, 1.0),
    "harry-esc": ("src-aperture", 108.0, 0.5, False, 1.0),
    "harry-end": ("src-aperture", 293.0, 0.5, False, 1.0),
    "sam-dance": ("src-unholy", 105.0, 0.5, False, 1.0),
    "sam-statues": ("src-unholy", 95.0, 0.6, False, 1.0),
    "sam-curtain": ("src-unholy", 90.0, 0.5, False, 1.0),
    "kim-hoop": ("src-unholy", 171.0, 0.5, False, 1.0),
    "kim-show": ("src-unholy", 177.0, 0.5, False, 1.0),
    "kim-heart": ("src-unholy", 167.0, 0.5, False, 1.0),
    "charli-hall": ("src-charli", 0.5, 0.45, False, 1.0),
    "charli-face": ("src-charli", 26.0, 0.5, False, 1.0),
    "charli-wine": ("src-charli", 126.0, 0.5, False, 1.0),
    "charli-shades": ("src-charli", 143.0, 0.5, False, 1.0),
    "rox-marie": ("src-roxette", 83.0, 0.5, False, 1.0),
    "rox-both": ("src-roxette", 74.0, 0.5, False, 1.0),
    "mj-sing": ("src-billie", 37.0, 0.5, False, 1.0),
    "mj-intro": ("src-billie", 0.0, 0.5, False, 1.0),
    "mj-walk": ("src-billie", 136.0, 0.5, False, 1.0),
}
VID = {}


def shot(name, t):
    if name not in VID:
        clip, s, fx, gray, sp = SHOTS[name]
        VID[name] = Video(clip, s, fx, gray, sp, {"src-unholy": 1.35, "src-billie": 1.3, "src-roxette": 1.15}.get(clip, 1.0), 0.12 if name == "sam-statues" else 0.5)
    return VID[name].frame_t(t)


STILLS = {}


def still(name, p, **kw):
    if name not in STILLS:
        STILLS[name] = Still(name, **kw)
    return STILLS[name].frame(p)


def montage(t, dur, items):
    n = len(items)
    i = min(n - 1, int(t / (dur / n)))
    lt = t - i * dur / n
    kind, name = items[i]
    if kind == "v":
        return shot(name, lt)
    return still(name, min(1.0, lt / (dur / n)))


def cuts(t, items):
    i = max(j for j, (at, _) in enumerate(items) if j == 0 or t >= at)
    at, item = items[i]
    end = items[i + 1][0] if i + 1 < len(items) else at + 3.0
    kind, name = item
    lt = t - (at if i else 0.0)
    if kind == "v":
        return shot(name, lt)
    return still(name, min(1.0, lt / max(0.5, end - at)))


def big(im, s, y, size=170, fill=FG, a=1.0, x=None):
    f = font("anton", size)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((center_x(y) - tw(s, f) / 2 if x is None else x, y), s, font=f, fill=fill)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)


def chip(im, s, a, y=940, size=44, x=None):
    if a <= 0:
        return
    f = font("anton", size)
    w = tw(s, f) + 36
    x = center_x(y) - w / 2 if x is None else x
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([x, y, x + w, y + size * 1.47], fill=ACCENT)
    d.text((x + 18, y + size * 0.07), s, font=f, fill=FG)
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)


def clock(sec):
    return f"0:{int(sec):02d}"


def shake(im, t, start, amount=20):
    k = 1 - ease((t - start) / 0.35)
    if t < start or k <= 0:
        return im
    out = Image.new("RGBA", im.size, BG + (255,))
    out.paste(im, (int(random.uniform(-1, 1) * amount * k), int(random.uniform(-1, 1) * amount * k)))
    return out


BAR_X0, BAR_X1, BAR_Y = 80, 940, 1418
WINDOW = 60.0


def bx(sec):
    return BAR_X0 + (BAR_X1 - BAR_X0) * min(1.0, sec / WINDOW)


def player(im, head, marker, title, label, lit=False, a=1.0):
    if a <= 0:
        return
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fl, fs = font("geistb", 38), font("geistb", 28)
    d.rectangle([BAR_X0, BAR_Y, BAR_X1, BAR_Y + 6], fill=(255, 255, 255, 90))
    d.rectangle([BAR_X0, BAR_Y, bx(head), BAR_Y + 6], fill=FG)
    if marker is not None:
        mx = bx(marker)
        r = 13 if lit else 9
        d.ellipse([mx - r, BAR_Y + 3 - r, mx + r, BAR_Y + 3 + r], fill=ACCENT if lit else (255, 255, 255, 170))
        lx = min(max(mx - tw(label, fs) / 2, BAR_X0), BAR_X1 - tw(label, fs))
        d.text((lx, BAR_Y + 26), label, font=fs, fill=ACCENT if lit else (255, 255, 255, 200))
    d.ellipse([bx(head) - 8, BAR_Y - 5, bx(head) + 8, BAR_Y + 11], fill=FG)
    d.text((BAR_X0, BAR_Y - 56), clock(head), font=fl, fill=ACCENT if lit else FG)
    d.text((BAR_X1 - tw(title, fs), BAR_Y - 48), title, font=fs, fill=(255, 255, 255, 210))
    if a < 1:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    im.alpha_composite(lay)


def full(name, t, speed=1.0, src=None):
    key = (name, speed)
    if key not in VID:
        clip, s, fx, gray, sp = SHOTS[name]
        VID[key] = Video(clip, src if src is not None else s, fx, gray, speed,
                         {"src-unholy": 1.35, "src-billie": 1.3, "src-roxette": 1.15}.get(clip, 1.0), 0.12 if name == "sam-statues" else 0.5)
    return VID[key].frame_t(t)


def cover_full(name, p, fx=0.5):
    return still(name, p, focus=(fx, 0.5), z=(1.0, 1.08))


# ---------- scenes ----------
def s_hook(t, f):
    im = montage(t, DUR["hook"], [("v", "sam-curtain"), ("v", "charli-wine"), ("v", "harry-face"), ("v", "kim-hoop"), ("v", "mj-sing")])
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("hook", t))
    return im


def s_billie(t, f):
    land = wt("billie", "twenty", 3.4)
    sing = wt("billie", "sings", 4.6) - 0.1
    if t < sing:
        im = full("mj-intro", t, speed=8.0, src=0.0)
        head = 29.5 * ease(t / land) if t < land else 29.5
    else:
        im = full("mj-sing", t - sing)
        head = 29.5
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("billie", t))
    player(im, head, 29.5, "BILLIE JEAN · 1983", "first word 0:29", lit=t >= land)
    return shake(im, t, sing, 16) if t >= sing else im


def s_jelly(t, f):
    s1 = sw("jelly", 2.2)
    im = cuts(t, [(0.0, ("s", "quincy-2.jpg")), (s1 * 0.55, ("s", "quincy-1.jpg")), (s1, ("s", "mj-0.jpg")),
                  (s1 + 0.9, ("s", "mj-2.jpg")), (wt("jelly", "that's", 3.6) - 0.1, ("v", "mj-sing"))])
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("jelly", t))
    return im


def s_unholy(t, f):
    im = cover_full("cov-unholy.jpg", min(1.0, t / DUR["unholy"]), fx=0.5)
    im.alpha_composite(Image.new("RGBA", (W, H), BG + (120,)))
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("unholy", t))
    player(im, 0.0, 0.5, "UNHOLY · 2022", "first word", a=ease((t - 0.4) / 0.4))
    return im


def s_hit(t, f):
    im = cuts(t, [(0.0, ("v", "sam-curtain")), (0.6, ("v", "kim-heart")), (1.2, ("v", "sam-dance")), (1.8, ("v", "kim-show"))])
    im = finish(im, f)
    wordmark(im)
    player(im, t, 0.5, "UNHOLY · 2022", "first word 0:00.5", lit=t >= 0.5)
    return shake(im, t, 0.0, 26)


def s_unholy2(t, f):
    im = cuts(t, [(0.0, ("v", "kim-hoop")), (1.2, ("v", "sam-statues")), (2.4, ("v", "sam-curtain"))])
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("unholy2", t))
    return im


def s_study(t, f):
    s1 = sw("study", 3.6)
    if t < s1:
        im = cuts(t, [(0.0, ("v", "mj-walk")), (s1 * 0.25, ("v", "rox-both")), (s1 * 0.5, ("v", "charli-face")),
                      (s1 * 0.75, ("v", "sam-dance"))])
        im = finish(im, f)
        wordmark(im)
        subtitle(im, part("study", t))
        return im
    k = ease((t - s1 - 0.4) / 1.6)
    im = cuts(t - s1, [(0.0, ("v", "mj-walk")), (0.8, ("v", "rox-both")), (1.6, ("v", "charli-shades")), (2.4, ("v", "kim-hoop"))])
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("study", t))
    year = 1986 + int(29 * k)
    marker = 20.0 - 15.0 * k
    player(im, 0.0, marker, f"TOP-TEN HITS · {year}", f"first word ~0:{int(round(marker)):02d}", lit=k >= 1)
    return im


SKIP_COVERS = [("cov-sabrina.jpg", 0.5), ("cov-chappell.jpg", 0.5), ("cov-billie.jpg", 0.45), ("cov-harryshouse.jpg", 0.5)]


def s_skip(t, f):
    s1 = sw("skip", 3.4)
    if t < s1:
        land = wt("skip", "thirty", 2.4) + 0.2
        im = cuts(t, [(0.0, ("v", "charli-hall")), (s1 * 0.5, ("v", "charli-shades"))])
        im = finish(im, f)
        wordmark(im)
        subtitle(im, part("skip", t))
        head = 30.0 * ease(t / land) if t < land else 30.0
        player(im, head, 30.0, "SPOTIFY", "counts as a stream", lit=t >= land)
        return im
    lt = t - s1
    seg = (DUR["skip"] - s1) / 4
    i = min(3, int(lt / seg))
    p = (lt - i * seg) / seg
    name, fx = SKIP_COVERS[i]
    im = cover_full(name, p, fx)
    skipped = i == 1
    if skipped and p > 0.55:
        k = ease((p - 0.55) / 0.3)
        out = Image.new("RGBA", (W, H), BG + (255,))
        out.alpha_composite(im, (int(-W * k), 0))
        im = out
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("skip", t))
    head = min(5.0, p * seg * 2.2) if skipped else p * seg * 2.2
    player(im, head, 5.0 if skipped else None, "", "SKIPPED" if skipped else "", lit=skipped and p > 0.5)
    return im


def s_charli(t, f):
    im = cuts(t, [(0.0, ("v", "charli-hall")), (0.9, ("v", "charli-face")), (1.8, ("v", "charli-wine")),
                  (2.9, ("v", "charli-shades")), (sw("charli", 3.6), ("v", "charli-face")), (sw("charli", 3.6) + 1.2, ("v", "charli-wine"))])
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("charli", t))
    return im


def s_roxette(t, f):
    s1 = sw("roxette", 2.4)
    if t < s1:
        im = cuts(t, [(0.0, ("v", "rox-both")), (1.2, ("s", "roxette-1.jpg"))])
    else:
        p = min(1.0, (t - s1) / (DUR["roxette"] - s1))
        if "rox-title" not in STILLS:
            STILLS["rox-title"] = Still("cov-roxette.jpg", focus=(0.78, 0.6), z=(1.1, 1.18))
        im = STILLS["rox-title"].frame(p)
        im = finish(im, f, band=False)
        wordmark(im, dark=True)
        subtitle(im, part("roxette", t), dark=True, y=640, cx=640)
        return im
    im = finish(im, f)
    wordmark(im)
    subtitle(im, part("roxette", t))
    return im


def s_flip(t, f):
    land = wt("flip", "forty", 4.2)
    one = wt("flip", "number", 2.0)
    im = cuts(t, [(0.0, ("v", "harry-room")), (1.2, ("v", "harry-esc")), (2.4, ("v", "harry-face")), (3.8, ("v", "harry-close"))])
    im = finish(im, f)
    wordmark(im)
    chip(im, "#1 · BILLBOARD HOT 100 · FEB 2026", ease((t - one) / 0.25), y=300, size=36)
    head = 45.4 * ease(t / land) if t < land else 45.4
    subtitle(im, part("flip", t))
    player(im, head, 45.4, "APERTURE · 2026", "first word 0:45", lit=t >= land)
    return shake(im, t, land, 14) if t >= land else im


def s_card(t, f):
    im = shot("harry-end", t)
    im.alpha_composite(Image.new("RGBA", (W, H), BG + (150,)))
    im = finish(im, f, band=False)
    wordmark(im)
    fh = font("anton", 112)
    for i, (s, col, at) in enumerate([("WOULD YOU WAIT", FG, 0.3), ("45 SECONDS?", ACCENT, wt("card", "forty", 1.6))]):
        a = ease((t - at) / 0.3)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((center_x(720) - tw(s, fh) / 2, 640 + i * 130), s, font=fh, fill=col)
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(lay)
    b = ease((t - 3.6) / 0.35)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    fr = font("anton", 64)
    s = "Rate Aperture on Riffiter."
    ld.text((center_x(1000) - tw(s, fr) / 2, 960), s, font=fr, fill=FG)
    ap, gp = Image.open(f"{D}/appstore.png"), Image.open(f"{D}/gplay.png")
    ap, gp = ap.resize((int(ap.width * 0.8), int(ap.height * 0.8))), gp.resize((int(gp.width * 0.8), int(gp.height * 0.8)))
    x = center_x(1100) - (ap.width + gp.width + 24) // 2
    lay.paste(ap, (x, 1080), ap)
    lay.paste(gp, (x + ap.width + 24, 1080), gp)
    ff_, fb_ = font("geistb", 36), font("geistb", 30)
    s = "Follow for a new song story every day."
    ld.text((center_x(1220) - tw(s, ff_) / 2, 1080 + ap.height + 32), s, font=ff_, fill=FG)
    ld.text((center_x(1300) - tw("LINK IN BIO", fb_) / 2, 1080 + ap.height + 96), "LINK IN BIO", font=fb_, fill=MUTED)
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * b)))
    im.alpha_composite(lay)
    return im


SCENES = [s for s in [("hook", s_hook), ("billie", s_billie), ("jelly", s_jelly), ("unholy", s_unholy), ("hit", s_hit),
          ("unholy2", s_unholy2), ("study", s_study), ("skip", s_skip), ("charli", s_charli), ("roxette", s_roxette),
          ("flip", s_flip), ("card", s_card)] if s[0] in ORDER]


def frame_at(t, f):
    keys = [k for k, _ in SCENES] + ["end"]
    for i, (k, fn) in enumerate(SCENES):
        if T[k] <= t < T[keys[i + 1]]:
            return fn(t - T[k], f)
    return SCENES[-1][1](T["end"] - T["card"] - 0.01, f)


def main():
    load_all_faces([n for n in os.listdir(f"{D}/img") if n.endswith(".jpg")])
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        os.makedirs(f"{D}/stills", exist_ok=True)
        for s in sys.argv[2:]:
            t = float(s)
            VID.clear()
            frame_at(t, int(t * FPS)).convert("RGB").save(f"{D}/stills/{t:05.2f}.jpg", quality=85)
        print({k: round(v, 2) for k, v in T.items()})
        return
    audio = build_audio()
    if len(sys.argv) > 1 and sys.argv[1] == "audio":
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{D}/reel-raw.mp4", "-i", audio, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{D}/reel-remux.mp4"], check=True)
        os.replace(f"{D}/reel-remux.mp4", f"{D}/reel-raw.mp4")
        return
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", f"{D}/reel-raw{'-shorts' if SHORT else ''}.mp4"], stdin=subprocess.PIPE)
    for f in range(int(T["end"] * FPS)):
        p.stdin.write(frame_at(f / FPS, f).convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print({k: round(v, 2) for k, v in T.items()})


main()
