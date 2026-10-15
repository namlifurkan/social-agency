---
name: story-reel
description: Build a story reel for any client — a 9:16, 40–75 s video that tells one reveal ("who really wrote it", "where the sample came from") or argues one question (essay reel) in beats over real photos and footage, with an ElevenLabs narrator, music that follows the story and the client's close. Use for every Instagram/TikTok/Shorts reel the founder asks for and for daily reel picks. Client specifics (audience, narrator, close, delivery, publishing) come from clients/<client>/PLAYBOOK.md. Renders locally; publishing only as the playbook says.
---

# Story reel

Founder rules from the 2026-10-04/05 sessions (built for Riffiter, the first client; they hold
for every client). **First read `clients/<client>/PLAYBOOK.md`**: it sets the audience, the
narrator, the brand marks, the close, the delivery folder and how (or whether) we publish. Where
this skill and the playbook differ, the playbook wins.

The working reference build is
`kit/reference/story-reel-olivia-paramore/` (`make.py` = visuals + audio mix, `vo.py` =
narration; scripts only, the Riffiter build's media is not in the repo; `R` in them points at the
Riffiter repo for its fonts and marks, swap in the client's `brand.json`), wired to the shared
`kit/reelkit/` (`vo.py`, `layout.py`, `faces.swift`, `clips.py`) by a relative `sys.path` to
`kit/reelkit`. Copy that folder into
`clients/<client>/studio/<post-date>-reel-<slug>/`, swap the story, the photos, the songs, the
narration, the wordmark and the close. Studio folders are gitignored; they live only on the
machine that made them.

A place portrait with the artist's own voice and no narrator is a different film: use the
**film-reel** skill (2026-10-10).

## Essay reels (format, founder 2026-10-14)

A second format built with the same kit: a **thesis question** ("Why do so many songs now start
right on the hook?") argued in 60–75 s, instead of one reveal. Reference build:
`kit/reference/essay-reel-chorus-first/` (`essay.py` = montage helpers, `make.py` = scenes).
Everything above still applies (narrator, two sources, safe zone, no text on faces, the mix, the
close); what changes:
- **Every narrated line is shown, literally.** The noun the narrator says gets 2–5 real images or
  clips of exactly that thing ("hits" = five hit videos, "Quincy Jones" = two Quincy photos), hard
  cuts every ~0.6–1.2 s, a slow push-in on stills. Constant cutting is what holds the viewer; a
  single photo held for a whole beat is a story reel, not an essay.
- **Small subtitles, not Anton titles.** The narrator's current line in Geist SemiBold 46 px,
  centred around y 1180 on a soft dark band; big Anton type only for the one number that matters
  (a clock, "1 IN 4").
- **Every frame is full-bleed footage or a photo (founder, 2026-10-14).** No text cards (a quote,
  a study title, a platform rule set as type on a plain background) and no clip shrunk into a
  frame or "TV" box on a dark page: the founder called both "full yazılı" and "kareye sıkışmış,
  hiç kreatif durmuyor". Evidence is said by the narrator and shown through the thing itself (the
  album cover cropped to its title, the artist's footage), with the source in the caption.
- **One small overlay device carries the argument.** Here: a thin player bar near the bottom
  (elapsed time, track · year, a marker where the first word lands) that runs over the full-bleed
  footage: 0:29 for Billie Jean, 0:00.5 for Unholy, the marker sliding from 0:20 to 0:05 for the
  study, 0:45 for Aperture. Name it in the ledger's Device column.
- **Correct the premise before writing.** The researcher's dossier decides the thesis: a claim the
  sources call plausible is said as a fact about what happened, never as the cause.
- Video timestamps from a 24-tile contact sheet are approximate; pick shots from a 1-fps strip of
  the range (`ffmpeg -ss S -t 24 -vf fps=1,scale=-1:150,tile=12x2`). A 2.39:1 music video inside
  16:9 needs `zoom=1.35` or the bars show in a 9:16 crop.

## The bar

Someone who sees it says **"wow, look at that creativity."** A playlist of clips with labels,
a chart of our own averages, a cover with a caption: all rejected. If you cannot name the
reveal in one sentence, there is no reel.

## 1. Pick the story

- **Read the client's `LEARNINGS.md` first.** It holds what has travelled so far and why; a pick
  that ignores a lesson says so and gives the reason.
- **Each reel changes one thing on purpose** and names it in the ledger's Test column
  (`close: …`, `device: …`, `format: …`). Changes to this skill's own rules (the look, the
  devices, the structure) come only through the client's format check (Riffiter: /daily-ops 5e), after the founder
  picks one.

- **The client's audience decides the topic range** (PLAYBOOK "Audience").
- **One reveal, flipped late.** Familiar thing first, then the fact that changes it.
- **Every fact checked against two sources** (WebSearch). Anything you could not confirm stays
  off the screen and out of the narration.

## 2. Beats and look

- 6–9 beats, one idea each, A2 English, ≤ 8 words a line on screen.
- Each beat is a **full-bleed real photo or video clip**: film grain, vignette, Ken Burns, the
  client's accent (`brand.json` `colors.accent`). The client's logo (`brand.json` `logo`) sits at the
  top of every frame (PLAYBOOK "Look").
- **Colour or B&W is chosen per reel, by the content (founder, 2026-10-10: "hep siyah meyah mı
  gideceğiz").** Colour when the source is colourful and the colour is part of the story (a pink
  music video, a red carpet, a live show, a TV studio): `Clip(gray=False)` plus the soft grade
  in `kit/reference/story-reel-adela/make.py` `grade()` (saturation ×0.85, blacks lifted to 0.05, warm
  `[1.04, 1.0, 0.93]`). B&W when the story is archive or the photos are old and mixed. A reel may
  mix them: B&W for the past, colour for now. Write the choice in the ledger's Device column.
  ADÉLA (10-10) ran colour on Instagram/X/Threads and B&W on TikTok/Shorts as a first A/B (the
  platforms differ too, so read it as a hint, not a result).
- **At least one visual device that is more than a photo with text on it**, built from photos or
  type, never a drawn prop. These passed: split-screen opening, VHS rewind/fast-forward with a year
  counter (`<< REW`), the song title cut in half over the person who wanted half, a hard cut with a
  screen shake on the turn, a "now playing" strip where the writer credit types in, the A/B
  ping-pong (below). These failed: a drawn vinyl splitting in half ("amatör"), a row of 10 stars.
- **Reels safe zone (founder, 2026-10-06).** Instagram covers the bottom ~420 px (username,
  caption, audio), the right ~140 px only where the buttons are (below y 900) and a thin top strip
  ("Reels", camera). Text, wordmark, chips, labels and badges stay inside **x 80–940 below y 900,
  x 80–1000 above it, y 160–1500**. The first try used 250 top and 140 right at every height:
  the founder called it overdone, and it pushed the text up onto faces. `reelkit/layout.py`
  holds the numbers (`safe_right(y)`, `center_x(y)`); `fit()` shrinks a line that does not fit.
- **No text on a face (founder, 2026-10-06).** `reelkit/layout.py` reads each photo's faces once
  with Apple Vision on a Mac (`reelkit/faces.swift`), OpenCV elsewhere (`opencv-python-headless<5`;
  misses profiles, so look at the frames) ( cached in the reel folder's `faces.json`) and
  `best_dy()` slides the crop so no face larger than 60 px sits in the scene's text bands. Every
  photo scene passes `bands` = where its text is (`LOWER_BAND` for bottom text, both bands when
  a title sits on top). A close-up that is too big for the gap between bands (a laughing
  portrait in a split half under a title) gets swapped for a photo with a smaller face.
  Check strip: the three unsafe bands in red, and look at every face.
- **Faces must show.** Check every crop on a frame strip before you move on. A hair flip or
  a lighting truss in the frame where the face should be is a miss (it happened twice with
  Hayley Williams). Fix the `focus` coordinates.

## 3. Photos and footage

**Founder, 2026-10-10: copyright is not a concern. Take whatever the story needs.** Choose per
beat, not per reel, and stop at the first rung that gives the real thing:

1. **The real moment on video.** The interview line, the music-video shot, the live clip, the TV
   appearance, the chart show. Search YouTube (WebSearch or `yt-dlp "ytsearch10:<query>"
   --flat-playlist --print "%(id)s %(duration)s %(title)s"`), then find the exact seconds with
   the **watch** skill: `python3 ~/.claude/skills/watch/scripts/watch.py "<url>" --question
   "<what you need>" --start <T> --end <T>` gives timestamped frames and the transcript. Download
   only that section: `reelkit/clips.py` `fetch(url, out, "00:01:10", "00:01:18")`.
2. **A real photo.** Wikimedia Commons (API below), US government photos (public domain, the
   best Olivia/pop source), press photos, album art, a screenshot of the chart or the article.
3. **The place.** For a city or venue beat, real footage of that street or skyline (Commons
   `filetype:video`, YouTube walk-throughs, Pexels).
4. **Generate (Higgsfield) only when nothing real exists**, and it must not look AI-made: an
   iPhone-real environment, hard cuts, no glowing morphs.

Clips render through `reelkit/clips.py`: `Clip(path, start, dur, focus_x, speed, gray)` streams
frames, so a scene calls `clip.frame(t)` where it would call `kenburns()`, then the usual scrim
and `finish()`. B&W and contrast match the photos by default; `speed=0.5` is slow motion;
`focus_x` slides the 9:16 crop sideways. The clip's own audio is dropped. Keep a clip's sound
(mix it in `build_audio()` from the downloaded file) only when the sound is the beat, such as
the quote itself. Clips skip `faces.json`, so check a frame strip and move `focus_x` until no
face sits under text. Credit the source (channel or photographer) in the caption.

Commons search through the API needs a User-Agent (an empty UA gets a 403):

```bash
UA="SocialAgency/1.0 (furkannamli@gmail.com)"
curl -s -A "$UA" -G https://commons.wikimedia.org/w/api.php --data-urlencode action=query \
  --data-urlencode format=json --data-urlencode generator=search --data-urlencode gsrnamespace=6 \
  --data-urlencode "gsrsearch=Olivia Rodrigo filetype:bitmap" --data-urlencode prop=imageinfo \
  --data-urlencode "iiprop=url|size|extmetadata"
```

Build a contact sheet (`magick … -resize x360 +append`) and look at it before choosing.

## 4. Song audio

- 30 s previews from Deezer: `curl -s https://api.deezer.com/track/<id>` returns a freshly
  signed `preview` URL. Search with a plain `q=` (the `artist:"…"` form returns nothing from curl).
- `loudest(path, dur)` picks the loudest window, which is usually the chorus. It is automatic,
  so tell the founder which moment you meant and let him check it by ear.
- Sound follows the story: the hit as the hook, the tape reversed and sped up on a rewind, the
  older song on its beat, the hit's peak returning as a callback.

## 5. Narration (ElevenLabs)

- **Voice: the client's own designed voice**, `narrator_voice` in `clients/<client>/brand.json`
  (`vo.py` finds it by walking up from the reel folder). No voice yet → `/client-setup <client>`,
  which designs one with ElevenLabs Voice Design (`reelkit/voice.py`) before the first reel. Never use a library voice the internet knows
  (Brian, Liam, Adam, Jessica, Matilda, Sarah, the "Peter" narrator), and never a real person's voice.
- Model `eleven_multilingual_v2`, settings stability 0.45, similarity 0.8, style 0.15, speaker
  boost on. **One request for the whole narration** (`reelkit/vo.py` `generate(BEATS, dir)`):
  the beats joined with `<break time="1.2s" />`, then cut in the middle of each silence. One
  request per beat ended every clip on its last letter with no decay, and the founder heard
  sub-second cut-offs (2026-10-06). Each clip keeps ~0.6 s of natural tail; `lead_silence` in
  `timing.json` tells make.py to start the clip early so speech lands on LEAD. TAIL is 0.15.
  Key: `ELEVENLABS_API_KEY` in the agency root `.env`.
- **The script says what the screen says**, word for word where possible. Short sentences,
  contractions, present tense for the story ("Hayley Williams is eighteen"). No "Did you know",
  no "insane", no hype. Run it through /humanizer before generating.
- `python3 vo.py` regenerates the whole narration in one take (a single changed line means a
  new take, so check the other beats still match the screen). Use `" | "` inside a beat's text to mark where the on-screen text
  switches.
- Tell the founder to tick the platform's AI-generated label when he uploads.

## 6. Timing comes from the narration

`make.py` reads `vo/timing.json`:
- scene length = `max(MIN, LEAD 0.25 + vo duration + TAIL 0.6)`;
- `sw(beat)` = the time of the `|` switch inside a scene;
- `wt(beat, "word")` = when a word is spoken, so a name types in exactly when it is said
  ("+ Hayley Williams", "+ Taylor Swift").
Give text time to be read. 40–58 s is fine. If it runs long, cut the side twist first, never the
main reveal.

## 7. The mix

- **Never `sidechaincompress`.** It pumped the music back up in every gap between words
  ("kısıp açmada sorun var"). Use the envelope in `duck()`: the music drops to 0.16 just before
  the narration, stays down through gaps shorter than 1.2 s, and comes back over 0.7 s after it.
- Music under the voice sits about 10–12 dB below it. Check with the per-second level printout
  (the snippet at the end of this file) instead of guessing.

## 8. A/B ping-pong (the comparison device)

When the story is "these two songs sound alike":
1. The narrator says the setup line ("Now play them back to back.") **over silence**.
2. Only after the narrator stops, the two songs alternate at full volume, **2 s each, 4 turns**,
   with no voice on top. The active half of the split screen is lit and the other is dimmed.
Voice and switching at the same time is a cacophony (the founder's word).

## 9. The close

The client's close (PLAYBOOK "The close"). Whatever it says, the narrator only asks the
question: **no "Comment X or Y"**, no big letters, no stars.

**Stack the close from real heights, not guessed y values (founder, 2026-10-09: "dip dipe").**
Store badges are 96 px tall at 0.8 scale and an Anton line is ~1.2× its size. Leave at least
24 px between headline, CTA, badges, follow line and LINK IN BIO, and keep the last line above
SAFE_B. When it does not fit, move the whole block up (and the photo's face `bands` with it)
instead of squeezing the gaps. Crop the close frame at full size and look at it before rendering.

## 10. Render, check, deliver

```bash
python3 -m venv /tmp/reelvenv && /tmp/reelvenv/bin/pip -q install numpy pillow
cd clients/<client>/studio/<date>-reel-<slug> && /tmp/reelvenv/bin/python make.py   # ~80 s
```

Windows (Git Bash): `python` instead of `python3`, the venv's interpreter is
`/tmp/reelvenv/Scripts/python`, and add `"opencv-python-headless<5"` to the pip install.

- Pull a frame strip at the key moments (hook, each beat, the device, the close) and look at it:
  faces visible, no text overflow, nothing crossed by the centre seam, names typing on their word.
- **Deliver a platform-spec file, never the raw render (founder, 2026-10-09: Old Town Road
  looked low-res).** make.py's `-crf 18` plus per-frame grain lands at 35–56 Mbps; Reels caps at
  25 Mbps and Instagram re-compresses anything above it hard, and grain is what breaks first.
  Encode the delivered `reel.mp4` with:
  `ffmpeg -i reel.mp4 -c:v libx264 -profile:v high -preset slow -crf 20 -maxrate 18M -bufsize 36M -pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -ar 48000 -movflags +faststart out.mp4`
  and check it lands under 20 Mbps with ffprobe. In new make.py files keep the grain light:
  alpha factor 14 instead of 22, and change the grain frame every 2 frames
  (`GRAIN[(f // 2) % len(GRAIN)]`), not every frame.
- **A Short over 60 s with any Content ID claim is blocked worldwide** (2026-10-14). A reel over
  60 s needs a ≤ 59 s Shorts cut (drop the side twist) before upload; Instagram and TikTok keep
  the full length.
- Deliver into the client's output folder with one ready-to-paste txt per platform and a
  schedule file (PLAYBOOK "Delivery"; the founder asked for files, not chat text). Captions name
  the photo and clip credits. `open` the file.
- Publish or schedule only as the client's PLAYBOOK says. A client with no publishing section
  gets the files and nothing else.
- Tell the founder to tick the platform's AI-generated label when the reel carries an AI narrator.

Level check:

```python
import subprocess, numpy as np
for f in ["mus-duck.wav", "vo.wav"]:
    x = np.frombuffer(subprocess.run(["ffmpeg","-loglevel","error","-i",f,"-ac","1","-f","f32le","-"],
                      capture_output=True).stdout, dtype=np.float32)
    print(f, " ".join(f"{20*np.log10(np.sqrt(np.mean(x[i:i+44100]**2))+1e-6):.0f}" for i in range(0, len(x), 44100)))
```
