import base64, json, os, re, subprocess, sys, urllib.request

MODEL = os.environ.get("VO_MODEL", "eleven_multilingual_v2")
BREAK = 1.2
SR = 44100


AGENCY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..")


def key():
    if os.environ.get("ELEVENLABS_API_KEY"):
        return os.environ["ELEVENLABS_API_KEY"]
    for line in open(os.path.join(AGENCY, ".env")):
        if line.startswith("ELEVENLABS_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("ELEVENLABS_API_KEY missing in the agency .env")


def narrator(out_dir):
    if os.environ.get("ELEVENLABS_VOICE_ID"):
        return os.environ["ELEVENLABS_VOICE_ID"]
    d = os.path.realpath(out_dir)
    while d != os.path.dirname(d):
        p = os.path.join(d, "brand.json")
        if os.path.exists(p):
            return json.load(open(p))["narrator_voice"]
        d = os.path.dirname(d)
    sys.exit("no narrator: set narrator_voice in clients/<client>/brand.json")


def tts(text, voice):
    body = {"text": text, "model_id": MODEL,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.15, "use_speaker_boost": True}}
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(body).encode(), headers={"xi-api-key": key(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def words_from(chars, starts, lo, hi, offset):
    words, cur, st = {}, "", None
    for c, a in zip(chars[lo:hi], starts[lo:hi]):
        if c.isalnum() or c in "'.":
            if not cur:
                st = a
            cur += c
        elif cur:
            words.setdefault(cur.strip(".").lower(), st - offset)
            cur = ""
    if cur:
        words.setdefault(cur.strip(".").lower(), st - offset)
    return words


def generate(beats, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    spoken = [t.replace(" | ", " ") for _, t in beats]
    full = f' <break time="{BREAK}s" /> '.join(spoken)
    res = tts(full, narrator(out_dir))
    whole = os.path.join(out_dir, "_full.mp3")
    open(whole, "wb").write(base64.b64decode(res["audio_base64"]))
    al = res["alignment"]
    chars, starts, ends = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    joined = "".join(chars)

    spans, pos = [], 0
    for text in spoken:
        i = joined.find(text, pos)
        if i < 0:
            sys.exit(f"alignment lost the beat: {text[:40]}")
        spans.append((i, i + len(text)))
        pos = i + len(text)

    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", whole],
                                 capture_output=True, text=True).stdout)
    cuts = [0.0]
    for (a, b), (c, _) in zip(spans, spans[1:]):
        cuts.append((ends[b - 1] + starts[c]) / 2)
    cuts.append(total)

    out = {}
    for k, ((name, text), (a, b)) in enumerate(zip(beats, spans)):
        s0, s1 = cuts[k], cuts[k + 1]
        path = os.path.join(out_dir, f"{name}.mp3")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s0:.3f}", "-to", f"{s1:.3f}", "-i", whole,
                        "-af", f"asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(s1 - s0 - 0.06, 0):.3f}:d=0.06",
                        "-c:a", "libmp3lame", "-q:a", "2", path], check=True)
        lead = starts[a] - s0
        splits, j = [], a
        for part in text.split(" | ")[1:]:
            j = joined.find(part, j)
            splits.append(starts[j] - s0 - lead)
        split = splits[0] + lead if splits else None
        out[name] = {"dur": s1 - s0 - lead, "speech_end": ends[b - 1] - s0 - lead, "split": None if split is None else split - lead, "splits": splits,
                     "words": {w: v - lead for w, v in words_from(chars, starts, a, b, s0).items()}, "lead_silence": lead,
                     "file": path}
        print(f"{name:10s} {s0:6.2f}-{s1:6.2f}  speech {starts[a] - s0:.2f}-{ends[b - 1] - s0:.2f}")
    json.dump(out, open(os.path.join(out_dir, "timing.json"), "w"), indent=1)
    return out
