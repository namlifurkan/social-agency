# Social Agency

> **Writing rule:** Run every caption, tweet, narration and slide text through `/humanizer` before it ships.

The founder's social media agency: story reels, film reels, carousels, research, footage and image
hunting, for any brand. The craft was first built in the Riffiter repo (`~/Desktop/project/riffiter`,
its `social/` folder and skills); this is a brand-free copy made on 2026-10-14. **The Riffiter
repo is read-only from here**: nothing in it is changed. The scripts of its reference builds are
copied into `kit/reference/`, so the team can use them without it.

## Who uses it

The founder on a Mac (CLI) and the team on **Windows, in the Claude desktop app** (Code tab, a
local folder). Talk to the team in plain Turkish, no jargon. Everything must run on both: the
shell on Windows is Git Bash, Python is `python` there (`python3` on the Mac), Chrome and venv
paths differ (see the skills). A user can add the API key in the app's Terminal (Ctrl+`).

## Agents roam the web freely

Research is the job. Agents here search, open any site, browse with Claude in Chrome, use
`agent-reach` / `opencli` for social platforms, and download photos, clips and audio (`yt-dlp`,
`curl`) without asking first. Copyright is not a filter (founder call); take whatever the story
needs. Real images and real footage first; never AI-generate imagery of real people or real
records.

Still off-limits without the founder: posting, commenting, liking or logging in anywhere except
what a client's PLAYBOOK explicitly hands to us, and any admin dashboard (Cloudflare, hosting, DNS).

## Layout

| Path | What |
|---|---|
| `.claude/skills/` | `client-setup` (onboarding interview), `story-reel`, `film-reel`, `social-studio`: the generic craft |
| `.claude/agents/` | `social-researcher` (reporter), `art-director` |
| `kit/reelkit/` | Shared reel toolkit: `clips.py`, `vo.py`, `voice.py` (ElevenLabs voice design), `layout.py`, `faces.swift` |
| `kit/reference/` | Reference reel builds (scripts and notes only) to copy into a client's studio |
| `clients/<client>/` | One brand: `PLAYBOOK.md`, `VOICE.md`, `STRATEGY.md`, `LEARNINGS.md`, `brand.json`, `fonts/`, `studio/<slug>/` |
| `clients/_template/` | Copy for a new client |
| `vault/` | The agency's shared memory (Obsidian-compatible, Turkish notes) |
| `.env` | `ELEVENLABS_API_KEY` (gitignored) |

## Every job starts with the client

1. Which client? The founder names it, or it is obvious from the topic. Unsure → ask.
2. Read `clients/<client>/PLAYBOOK.md` (audience, look, close, delivery, publishing), then
   `STRATEGY.md` and `LEARNINGS.md`. The playbook wins over the skills.
3. New client, a new team member, or fields marked "Ask at setup" → `/client-setup <client>`: an
   interview that checks the ElevenLabs key, fills the brand, playbook and close, and sets up the
   narrator voice.

Nothing is published unless the client's PLAYBOOK has a publishing section.

## Vault

`vault/` in this repo, shared with the team through git. Agency-wide knowledge only;
client-specific facts stay in `clients/<client>/` (PLAYBOOK, VOICE, LEARNINGS).

Read `vault/README.md` and the relevant hub before a non-trivial job. Write a note, without being
asked, when:

| What | Where |
|---|---|
| A decision (format, tool, founder call) | `vault/decisions/YYYY-MM-DD-baslik.md` |
| A solved problem (render bug, broken tool) | `vault/incidents/YYYY-MM-DD-baslik.md` |
| Platform or craft knowledge (sizes, what travels) | `vault/domain/konu.md` |
| A working habit | `vault/conventions/konu.md` |
| Who on the team cares about what | `vault/people/isim.md` |

Note rules: Turkish; one idea per note; frontmatter `title`, `date`, `tags`; first line
`> Proje: [[Social Agency]] · Hub: [[Social Agency — <Kategori>]]`; a `## Related` section with at
least one `[[sibling-note]]`; add the note to its hub's `## Notlar`. No links to the founder's
other vaults. Tell the user which note was written.

Commit/push only when asked.
