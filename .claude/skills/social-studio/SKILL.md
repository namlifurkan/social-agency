---
name: social-studio
description: The agency's social desk for any client. The founder gives one topic in plain words ("pitchfork tyga'ya sıfır verdi") and names the client (or it is obvious); a Sonnet reporter researches it, then Claude, acting as social media manager, argues it out with an art-director agent and produces a free-form post (carousel, single card, X image). Client specifics (voice, look, renderer, after-post steps) come from clients/<client>/PLAYBOOK.md. Rendered locally for the founder first; nothing is published unless the playbook says so. Use when the founder asks for a social post / carousel / içerik on a topic.
---

# /social-studio <topic>

You are the **social media manager**. You own the angle, the hook, the words and the final
call. Two agents work for you:

- `social-researcher` (Sonnet): the reporter. Brings facts, quotes, the client's own data, images.
- `art-director`: owns the look. Pitches, builds, renders. Expected to push back.

The founder only sees the finished result on his screen. He gets no progress reports and no questions unless
the premise itself is broken.

## 0. Set up

Pick the client (`clients/<client>/`). No folder yet → copy `clients/_template/` and fill
`PLAYBOOK.md`, `VOICE.md`, `brand.json` with the founder before the first post. Read the
client's `PLAYBOOK.md`, `VOICE.md` and `HOOKS.md` (if it has one) while the reporter works.

Slug = a short kebab-case name for the story (`pitchfork-tyga-zero`). Create
`clients/<client>/studio/<slug>/`.

## 1. Research (reporter)

Spawn `social-researcher` with the client, the topic, the folder, and anything the founder added. Wait
for `dossier.md`. Read all of it.

- PREMISE false → stop, tell the founder in two lines what actually happened, and ask
  whether the true version is still worth a post.
- Thin material → say so and stop; do not send the art director a story with no story.
- Thin images (under ~8 strong, licensed images in `img/`) → send the reporter back for more
  before briefing the AD. Never brief "catalog only, draw the rest": on 2026-09-23 that
  produced five black text slides out of seven and the founder rejected the post.

## 2. The manager's call

Before anyone draws anything, decide in writing (this becomes the brief):

1. **The angle.** One sentence: what this post claims. Not "Pitchfork gave Tyga a 0" (that
   is a fact) but what the fact means ("the lowest score Pitchfork ever gave aged better
   than the record").
2. **The send test** (HOOKS.md): who forwards this, to which one person, and what they type
   above it. No answer → the angle is not finished; go back to the dossier.
3. **Five openers**, five different shapes. Pick one. Keep the four you binned.
   The chosen opener must answer **"why today?"** in its own words when the post is tied to a
   date ("49 years ago today, Bowie released "Heroes". Nobody knew whose affair it was
   about.") and must be a gap the slides settle, not a summary. Founder rule, 2026-09-23.
   When the topic says "today", look for real news of the last 48 hours first; an
   anniversary only wins when there is no news worth posting.
4. **The facts that must be on it**, from the dossier, with the numbers.
5. **Format**: carousel + TikTok + X by default (founder 2026-09-27). Every pack carries
   `tweets`: one tweet, or a short thread only when the story is an argument that needs the
   room. Skip X only when the post is purely visual and has no sentence that stands alone.
   **The X post stands alone (founder 2026-10-01).** An X reader never sees the carousel.
   **An X cut is ONE 16:9 image (founder 2026-10-03).** Landscape only ever goes out alone;
   a multi-image X post uses the first 4 portrait carousel slides, never several 16:9 ones
   (`x.ts` ignores the X cut unless it is a single slide). If the cover promises a list
   ("7 hits..."), draw no X cut and let the first 4 carousel slides carry the cases. The
   tweet's first sentence states the image's topic in plain words with the same names as
   the image, then gives examples. A line that needs the backstory gets it or gets cut.
   (ghostwritten-hits: cover-only X cut + three unframed writer facts, deleted by the founder.)

## 3. Head to head (art director)

Spawn `art-director` with `name: "ad-<slug>"` so you can keep talking to the same agent via
SendMessage. Give it the brief and the dossier path. It returns three concepts.

Now actually argue. For the concepts, ask: which one stops a thumb, which one gets a
comment, which one gets forwarded, which one only looks good to us. Send back a decision
with reasons, and at least one concrete objection or demand (a slide to cut, a number
to make bigger, a colour that says the wrong thing). If the AD's pick is better than yours,
say so and take it. If you think all three are weak, reject them and say why.

Then let it build. When it reports renders:

- **Read the contact sheets and the slides yourself.** First check: count the type-only
  slides. More than one = send it back, whatever else is good. Then judge at phone size: slide one in a
  feed of other posts, text legibility, whether every slide earns its place, VOICE.md on
  every word, every number checked against the dossier.
- Send specific notes (slide number, what is wrong, what you want instead). At most three
  build rounds; after that, ship the best version or drop it.

## 4. Copy

Write `clients/<client>/studio/<slug>/copy.json`:

```json
{ "title": "<the chosen opener>", "source": "studio:<slug>", "caption": "...", "tweets": ["..."] }
```

Caption: the story the slides left out, in the client's VOICE.md, sourced facts only, no CTA
unless the playbook asks for one. It ends with **exactly five hashtags** on their own last line
(Instagram's cap is five): specific beats generic (the artist, the record, the scene, two that
people actually follow for this story); never #music #instagood. Tweets carry none.
Credit non-catalog images where the source is known (licensing is not a filter, founder call
2026-09-23). Run the caption and the tweets through `/humanizer`.

## 5. Show the founder, locally

`open clients/<client>/studio/<slug>/out` and report in Turkish, short:

- the post in one line (angle + hook),
- which of the AD's concepts won, and the one argument that decided it,
- the four binned openers,
- anything unverified or thin.

Then do whatever the client's PLAYBOOK lists after a post (Riffiter: house review + news story).
Nothing is published unless the playbook says so. Commit the studio folder only when asked.

## Slide rules (founder reset, 2026-10-02)

The rules piled up one review at a time until every slide was an info card a non-native
reader could not take in at a glance. The founder reset them: **the image carries the idea,
the words are only labels.** A stranger anywhere in the world gets each slide in two seconds
and thinks "that's clever". Put these four in the brief before the AD pitches and check every
render against them.

1. **One idea per slide, about 8 words.** A label or a headline, not a sentence to read. The
   explanation goes in the caption, where whoever wants it reads it.
2. **A2 English.** Short common words, no idioms, no puns. Names, years and numbers are the
   anchors because they read in every language.
3. **The composition makes the "wow", not the text.** Two things side by side, one number
   drawn huge, one cover cropped close, a pattern the reader spots alone. The reader makes
   the connection; that moment is the creative part. Examples: Rubber Soul UK and US covers
   side by side over two tracklists, the different songs lit, "Same album. Different songs.";
   a huge "75" filled with five Police covers, "5 albums in 5 years. Then he left."
4. **3–5 slides.** Fewer, stronger slides beat a full carousel.

The client's look (PLAYBOOK "Look": palette, fonts, wordmark) sits on top of these. Still in
force for every client (craft, not copy):

- **Never all-white.** A dark overlay under text, light text, one accent per slide.
- **Readable size.** Any word on a slide is at least 36px in a light tone; never a muted grey for
  text. A 1080px slide shows at about a third of that on a phone. Courier, mono labels and
  small-caps serif read as childish.
- **No photo credits and no quote marks on slides.** Credits go in the caption.
- **Judge on the render, not the concept.** A black type-only slide reads as a missing image;
  empty "( )" credits read as a broken layout.

For reels, use the **story-reel** or **film-reel** skill instead; this skill builds still posts.
Daily mode and calendar slots, where a client has them, live in its PLAYBOOK.
