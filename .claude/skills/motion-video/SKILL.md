---
name: motion-video
description: Design and build a motion video entirely in code (GSAP timeline, three.js for 3D, frame-by-frame render to mp4) for any client, judged against reference videos by fresh critics until it passes a measured quality bar. Use when the founder or team asks for a motion graphic, product/brand/promo video, animated explainer or "motion video" (16:9, 9:16 or both). Not for story or film reels over real footage (use story-reel / film-reel). Client specifics come from clients/<client>/PLAYBOOK.md.
---

# Motion video

Role: you design and build motion videos entirely in code, with GSAP for the animation and
three.js for any 3D. Every decision is judged against the best work in the references, and the
video isn't finished until it holds up next to them.

**First read `clients/<client>/PLAYBOOK.md`** (and `STRATEGY.md`, `LEARNINGS.md`, `brand.json`).
Where this skill and the playbook differ, the playbook wins. Run every on-screen text line through
`/humanizer`. Talk to the team in plain Turkish; this skill stays English.

## Brief (fill from the founder; if missing, decide yourself and write the call down)

- what the video is for (product, service, business)
- who is watching and what they care about
- what they should do at the end (CTA)
- length and sizes (e.g. 30 s, 16:9 and 9:16)
- brand: name, logo files, colours, fonts (from `clients/<client>/brand.json`)
- facts file: the only source for any number, name or claim on screen
- assets: footage, photos, screenshots, product files
- style references: links or a folder of videos whose motion we like

The founder may be away. Make the calls, keep going until every check below passes.

## Kit

Before anything else, clone and read https://github.com/echris6/motion-video-kit (into the
scratchpad or `kit/motion-video-kit/`, not into a client folder). Read `SKILL.md` first, then every
reference file it points to at the step where it says to read it. Its rules, critic prompts,
quality bar, 3D patterns, audio tools and scripts override your defaults.

## Setup

- every scene is an HTML page animated on a single GSAP timeline, three.js for any 3D, all as
  pinned local files
- render the timeline to video frame by frame with the kit's renderer
- ffmpeg for frames, contact sheets and audio measurement
- API keys only in environment variables (`.env` is gitignored); never write a key into a file
- render a 5 s test first and confirm it works before building the real video
- Windows team: Git Bash, `python` instead of `python3`, Chrome path differs (see other skills)

## Study the references

If references were given, study them before planning anything:

- fast numeric pass over every frame (change from last frame, brightness, edge detail) to find
  every cut and every fast moment
- one overview contact sheet per video, plus a dense sheet (16–20 fps, 1 s) around every transition
- a note per video: the key moment, how it works, how it could be used here
- pull out the motion rules and named techniques that hold across the best ones
- study only: never copy their footage, logos, layouts or music

No references → use the motion notes in the kit.

## Motion principles

1. The thing in front becomes the transition: a title, logo or object moves toward the camera
   while the next scene already waits underneath.
2. One object carries the story across shots and keeps its identity.
3. One main movement leads, smaller ones layer under it, all overlapping. The frame never stops
   and starts all at once.
4. Speed always changes: land slowly enough to read, leave fast, the next thing slows as it
   arrives. No linear motion.
5. Cuts only when size, direction and subject match on both sides.
6. Every action has a visible result (scan → findings, tap → new state, request → confirmation).
7. Type is motion too: big words enter from opposite sides, reveal the next scene, and never sit
   over busy picture without something behind them to stay readable.
8. Vary scale: close, wide, overhead, full-frame type. Never repeat a layout (e.g. heading over
   three cards).

## Storyboard (before any animation)

Write a brief and a storyboard first.

- one table: time, what's on screen, what the moment is for, how it leaves, which object carries
  into the next shot
- about 12–15 compositions per 30 s, each ~1.4–3.5 s
- main subject fills most of the frame; no small cards floating in empty space
- frame one is a finished picture, never a word halfway through flying in
- name three signature moments, described without effect names
- must make sense with the sound off
- send the storyboard to a fresh critic and fix what it finds before building

## Build

- every animated value is a function of timeline time only: no timers, no real-time animation,
  no unseeded randomness. Any frame renders the same every time.
- shared pieces first: colours, fonts, shared 3D models, exact pixel position of every handoff
- each scene is its own component with its own test page, rendered to stills and a short clip,
  and sent to a critic before it joins the film
- carried objects land on exactly the same pixels on both sides of a cut
- once shared pieces exist, run several builders in parallel on separate sections
- don't stop to ask for approval between steps

## 3D

- only where it explains something physical or spatial (layers, parts, placement, scale)
- product-shoot light: soft key from one side, rim light behind
- camera 35–55°; never look straight down on a large surface, never end tight on a flat one
- buildings: premium architectural model, real materials, a base
- no floating parts, no gaps where parts meet, no flat black glass, no repeating textures
- labels are HTML positioned from the 3D scene every frame, never text inside the 3D
- measure the rendered background pixel and adjust until it matches the brand colour
- anything that moves like a real product is measured from real footage frame by frame; the
  measurements are the curve

## Images and footage

- prefer building shots in code; generated images/clips only for supporting shots, labelled as
  concept
- upscale and smooth any generated clip to match the rest; regenerate anything that warps
- never generate a fake finished job, customer, review or result
- agency rule still holds: never AI-generate imagery of real people or real records

## Audio

- music energy matches picture and viewer, kept low
- prefer clean library music and SFX over generated; never name a brand in a music prompt
- one short soft whoosh per real scene change; clicks/pops only on real on-screen actions
- screen each effect for boom, hiss and length; set each just above the music in its own
  frequency range, with a cap so nothing gets harsh
- cut every scene change on a beat
- always export a music-only version

## Critic loop

The builder never judges its own work.

- after the storyboard, each component and each full render, send the render, the brief and the
  references to a fresh critic (Agent tool, `critic` or `general-purpose`) that has seen none of
  the building
- never tell a critic what you think you fixed or believe about the references; it pulls its own
  frames and measures
- the critic makes a contact sheet every 0.2 s plus dense frames around every transition,
  measures frozen time and loudness, and returns a ranked problem list with timestamps, ending
  with ship or one more pass
- fix the biggest problem first, render, then a new critic checks every previous item as fixed,
  partly fixed or still there, and hunts for new breakage
- keep a ledger of every round: found, changed, numbers before and after

## Quality bar (all measured)

- ≤ ~1 s of frozen screen per 30 s, no still stretch longer than ~0.5 s
- frame one is a finished composition
- all text ≥ 4.5:1 contrast; nothing collides with or flies through other text
- brand colours in 3D renders match brand values
- loudness steady and comfortable for web, no clipping, effects never louder than the music
- a first-time viewer understands it with the sound off
- a critic would put it next to the references without it looking weaker (no bugs ≠ good)

## Honesty

- only numbers, names and claims from the facts file appear on screen
- no invented testimonials, ratings, prices, savings, warranties or results
- anything conceptual or generated is labelled as such
- reports separate what was measured from what a human still needs to watch or listen to

## Deliverables

Into the client's delivery folder (per PLAYBOOK), under `clients/<client>/studio/<slug>/`:

- final mp4 in every requested size, 1080p, 60 fps
- music-only version
- contact sheet of the final video
- critic ledger and final quality bar results
- a short note on anything a human should still check

Nothing is published unless the client's PLAYBOOK has a publishing section.
