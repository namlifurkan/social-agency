---
name: film-reel
description: Build a film reel for any client — a 9:16, ~60 s MUBI-style mini documentary about one place (a town, street, store, studio) and what was made there, told in the subject's own interview voice over real footage, with no AI narrator and no news hook. Use when the founder asks for a mini belgesel / film / MUBI-style reel, or when a reel pitch is a place portrait instead of a reveal. Client specifics come from clients/<client>/PLAYBOOK.md. Renders locally.
---

# Film reel

The sibling of the story reel (story-reel skill). Same delivery and scheduling (the client's
PLAYBOOK), a different film. Read `clients/<client>/PLAYBOOK.md` first. Founder, 2026-10-10: "hep newstan gidiyoruz", so this one is quiet, artful and evergreen.
The first build, `~/Desktop/project/riffiter/social/studio/2026-10-14-reel-stick-season/` (Noah Kahan, Strafford VT), is
the reference: the founder called the video good ("güzel video") and did not like the topic; it was posted 10-14.
Copy its `make.py` into `clients/<client>/studio/` for a new film and swap the shots, voices,
texts, song and brand marks. Studio folders live only on this Mac.

## The bar

It should feel like a MUBI short, not a recap: long calm shots, a real voice, small type,
silence that is allowed to sit. If it looks like a news package, it failed.

## 1. Pick the place

- **One place, one record.** A town, a street, a store, a studio, a club where a song or an
  album was made and you can hear the place in it. One-line thesis: "Strafford is the chorus of
  Stick Season".
- **Filmable first.** The place has to exist on video: the official music video shot there, walk-
  throughs, local TV, fan phone footage.
- **The artist's voice has to exist.** At least 3 clean interview lines (4–12 s each) where the
  artist talks about the place. No voice, no film.
- **Topic taste.** Pitch two places before building; the client's audience (PLAYBOOK) decides.
  A video that works on a topic the founder does not want is still a miss.
- No news hook is needed. Two plain facts in tension still make the cold open ("1,094 people live
  here." / "Their song was No. 1 in the UK for seven weeks.").
- Every fact on screen is double-sourced. Never put song lyrics on screen.

## 2. Research

Spawn **social-researcher** with this brief: a place portrait, no news hook; 2 picks; for each,
8–12 clips with exact start–end, verbatim speech and a `focus_x` / "vertical?" column, 6–10
photos, 2–3 anchor facts double-sourced, 5–7 chapters (place moment + artist line + song
moment). Clips matter more than photos.

## 3. Footage

- **Full-screen 9:16, never letterboxed** (founder, 2026-10-10: a wide window wastes the phone).
  A 16:9 source keeps only its middle ~32% in 9:16, so choose moments where that slice still
  means something: one person, a road to a vanishing point, a doorway, a sign, a face. Native
  vertical (phone video, the artist's TikTok) is best. Music videos are often pillarboxed 4:3
  inside 16:9; that is fine, the crop stays inside the picture.
- **Download** with `reelkit/clips.py` `fetch(url, "clips/src-<id>.mp4")`: the whole video, once
  (YouTube 403s section downloads; `web_embedded` gives 1080p, `mweb` falls back to 360p). A 360p
  source can still carry its voice over other footage, but never show its picture.
- **Frame it** with `Clip(path, start, dur, focus_x, speed, gray=False, zoom, focus_y)`.
  `focus_x` can be a `(from, to)` pan. `zoom` + `focus_y=0` pushes a TV lower-third out of frame
  (CBS: `zoom=1.18, focus_y=0`). Find `focus_x` from a frame: subject centre `c` (0–1) in a
  1920-wide source scaled to cover 1080×1920 gives `focus_x ≈ (c·3413 − 540) / 2333`.
- **Check the range in the source before using it.** Pull a frame every second across each
  shot's range: shots end inside music videos (a road at 135–137 s became a blurred car shot at
  137 s; a road at 56–60 s became the store at 60 s). Slow motion (`speed` 0.36–0.83) stretches
  a short clean range.
- **Who is speaking?** Look at the frame under every voice line. On CBS, "You had to go
  backwards to go forward" was the interviewer, not Kahan, and was cut.

## 4. Voices and timing

- Word times come from YouTube's auto captions in `json3`:
  `yt-dlp --skip-download --write-auto-subs --sub-langs "en.*,en" --sub-format json3
  --extractor-args "youtube:player_client=web_embedded" -o cap-<id> <url>`, then read
  `events[].segs[]` (`tStartMs + tOffsetMs`). Cut each line just before its first word and
  after its last; split a line around a mumble ("you'll recognize… you") instead of keeping it.
  Local `whisper` is broken on this Mac (numba/NumPy); do not spend time on it.
- `VOICES = [(timeline_t, src, a, b)]`; lip-synced shots start the picture `0.2 s` before the
  voice (`src_start = a − (voice_t − shot_t0)`).
- Subtitles are the speaker's words, verbatim minus filler ("like", "um"), max ~2 lines, split at
  natural pauses, switched on the caption times. The first subtitle of each speaker carries a
  small label ("NOAH KAHAN", "MELVIN COBURN").

## 5. Structure (~60 s)

1. Cold open (0–5 s): the place, a small location label at the top, the two facts.
2. 4–5 chapters (6–10 s each), each a small tracked label ("II.   THE TOWN") for ~3 s, a place
   shot, one voice line, at most one fact card ("Town House, built 1799.").
3. A hard cut into the song at full volume (the chorus, found from the loudness map: the dip
   before a loud stretch), with the title card ("Stick Season" + "NOAH KAHAN · 2022").
4. One quiet closing line, then the client's close (PLAYBOOK) over the last shot dimmed to ~55%.

## 6. Look (numbers from the reference make.py)

- Grade, not B&W: lift blacks `0.06 + a·0.88`, saturation ×0.55, warm `[1.04, 1.0, 0.93]`.
- Scrim: bottom `clip((y − 0.44H)/0.24H)^1.3 · 0.88`, top `clip(1 − y/0.24H)^0.8 · 0.80`.
- Grain σ 7, changing every 2 frames. Dissolves 0.4 s between shots; the only hard cut is the
  song entrance.
- Type: the client's wordmark at y 190 (Riffiter: "RIFFITER" Geist SemiBold 26, tracked 10). Chapter label Geist 30, tracked 8,
  y 260. Subtitles Fraunces Italic 54, line height 70, block from y 1230, centred on
  `center_x()`, balanced line breaks (no orphan word). Labels Geist 24, tracked 6, `DIM`.
  Title Fraunces Italic 96. The client's accent only as a 36×3 px rule under the title.
- **No text over a face.** Chapter labels move off close-ups (put "I." on the next shot); if a
  subtitle reaches the chin, lower the zoom so the face rides higher.
- Text fades 0.35 s in and out.

## 7. Sound

- **No AI narrator, no ElevenLabs.** The voices are the interviews.
- Song bed = the official video's own audio (the full song, no 30 s preview limit),
  `loudnorm I=-14`. Voices `loudnorm I=-16`, 80 ms ramps.
- Bed envelope: 0.55 in the cold open, 0.42 between voices, ducked to 0.12 from 50 ms before a
  voice to 100 ms after (gaps under 1.2 s stay ducked), 1.0 from the hard cut, fade over the last
  2.8 s. No `sidechaincompress`.
- The bed under the voices is the song's intro and first verse, so the singer can sit under his
  own speaking voice. Check by ear; an instrumental stretch is better when the song has one.
- Check levels with the per-second printout in story-reel.

## 8. Render, check, deliver

- `/tmp/reelvenv/bin/python make.py 3.5 12 27 43` renders single check frames into `chk/`;
  look at a strip of them before the full render (~3.5 min for 60 s).
- Deliver exactly as story-reel §10 and the client's PLAYBOOK, with two differences: no
  AI-generated label (there is no AI voice), and the caption lists the clip sources ("Clips:
  Genius, CBS Mornings, …").
- The client's `LEARNINGS.md` records it with Device "film format", so it can be judged
  against the story reels.
