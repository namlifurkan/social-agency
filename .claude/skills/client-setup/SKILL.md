---
name: client-setup
description: Onboard a client, or a new team member on an existing client — an interview that checks the machine (ElevenLabs key, tools), then fills clients/<client>/ (brand.json, PLAYBOOK, VOICE, STRATEGY) with the person, including the reel close and the narrator voice they design or pick on their own ElevenLabs account. Use when someone says "yeni müşteri kur", "setup", "kurulum", "ilk kez kullanıyorum", names a client with no folder, or a skill finds brand.json or PLAYBOOK fields empty or marked "Ask at setup".
---

# /client-setup <client>

An interview, in Turkish, one topic at a time. Prefilled values are proposals: show them, let the
person keep or change them. Never ask what the repo, the client's site or code already answers;
look first, then confirm. Use AskUserQuestion for choices, plain questions for free text.

## 1. Machine

- `.env` at the agency root with `ELEVENLABS_API_KEY`. Check with
  `python3 kit/reelkit/voice.py check`. Missing or 401 → walk them through it:
  elevenlabs.io → sign in → Developers → API Keys → Create key, with access to Text to Speech,
  Voices (read + write) and Voice Generation. Ask them to add it themselves so the key stays out of
  the chat: `! echo 'ELEVENLABS_API_KEY=sk_...' >> .env`. Run `check` again.
- Tools: `ffmpeg`, `yt-dlp`, `magick`, `python3`, Google Chrome. Missing → `brew install <tool>`
  (ask first).

## 2. Client folder

Folder missing → `cp -R clients/_template clients/<client>`. Then the brand, from the client's site
or repo if they give one (CSS variables, logo SVGs, `font-family`):

- `logo`: SVG or transparent PNG in the client folder. Crop the artboard to the mark
  (`magick -background none -density 384 logo.svg -format "%@" info:` gives the box).
- `colors`: `bg`, `ink`, `accent` hex.
- `fonts`: display and body family names; TTFs into `fonts/` from github.com/google/fonts.
- Render one test card (art-director's HTML + headless Chrome recipe) with a Turkish line
  (ğüşıöç) and show it.

## 3. Interview

Write each answer into the file named, in English except quoted copy:

1. **Accounts** we make posts for (PLAYBOOK "Who and where").
2. **Audience** and the topics that travel; what never to say (PLAYBOOK "Audience and stories").
3. **Voice**: sen or siz, tone, words to avoid (VOICE.md).
4. **The close**: how a reel ends. Offer "LINK IN BIO", the site URL, a CTA line from the client's
   own copy, a badge, or nothing; they can write their own (PLAYBOOK "The close").
5. **Delivery**: output folder and what goes in it (PLAYBOOK "Delivery").
6. **Publishing**: default is none, the person gets the files. Only fill it if they ask.
7. **Goal and cadence** (STRATEGY.md).

## 4. Narrator voice

The voice lives on the person's own ElevenLabs account; its id goes in `brand.json`
`narrator_voice`. Three ways, their pick:

- **Design one (default for reels)**: write the description together (age, gender, accent
  "native Turkish, Istanbul accent", pace, warmth). Sample text: 100–1000 characters of the
  client's own copy, including the brand name. Then
  `python3 kit/reelkit/voice.py design "<desc>" "<text>" clients/<client>/voice/` makes three
  previews; play them with `afplay`, let them choose, then `voice.py save <generated_voice_id>
  "<Client> narrator" "<desc>"` prints the voice id. Not happy → change the description, run again.
- **Use one they already have**: `voice.py list`, they pick by name.
- **Clone their own voice**: only a voice they have the right to use (their own, with consent).
  ElevenLabs site → Voices → Add a new voice → Instant Voice Clone, 1–2 minutes of clean audio;
  copy the voice id.

Never a well-known library voice (Brian, Liam, Adam, Jessica, Matilda, Sarah) and never a real
person's voice without consent. Last step: `voice.py test <voice_id> "<a line with the brand
name>" clients/<client>/voice/test.mp3`, play it, check the brand name is pronounced right
(rewrite the spelling in scripts if not, and note it in VOICE.md).

## 5. Done

Show what changed per file. `voice/` and `studio/` stay local. Commit only if asked.
