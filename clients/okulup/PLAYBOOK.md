# OkulUp — client playbook

Prefilled from the client's repos and the vault on 2026-10-15; `/client-setup` confirms it with the team.
The generic skills read it and it wins over them.

## Who and where
OkulUp: one official school channel that replaces scattered WhatsApp groups, in one app for
parents, teachers, school admins and staff. Site https://okulup.com, App Store id6761079786, Play
`com.okul.kampus`. Repos `~/Desktop/project/okulup/` (app, api, crm, website).

Accounts: Instagram `@okul.up`, LinkedIn `okulup`. Which ones we post for: ask at setup.

Same company as okul.com.tr, separate brand: okul.com.tr is presented as "the biggest corporate
customer". Never "okul.com.tr çatısı altında"; keep the visual identity separate.

## Audience and stories
The buyer is the school owner or management; parents come in through the school. Offer: 1 year
free, setup done by us ("Excel'inizi gönderin, okulunuzu biz kuralım"). Never talk prices, no
demo-call promises.

Features to show: duyuru/anket, günlük takip, yoklama, mesajlaşma, galeri, yemek menüsü, randevu,
ödeme takibi. Never the school bus route or document requests (they don't exist). Modern
classrooms only. Never AI-generated app screens; use real screenshots.

Stats cleared for marketing: 25+ okul, 1000+ veli/öğrenci, 100+ öğretmen.

## Look
The values live in `brand.json`: `colors` (hex for `bg`, `ink`, `accent`), `fonts` (family names,
TTF/OTF files in `fonts/`), `logo` (file in this folder, SVG or transparent PNG) and
`narrator_voice`. Here: how the brand should feel, where the wordmark sits, what never to do.

From the logo and okul.com.tr's OkulUp pages (`--okulup-*` in `customer.css`): orange #F27A23,
amber #FCB715 (the "up"), warm surface #FAF7F4, ink #2B231D, deep orange #B4560F. The app itself
uses #FF5F1F; posts follow the logo orange. Font Archivo (the OkulUp web pages). Logo variants
(white, orange tile, icon only) are in the app repo `assets/SVG/okulup-logo-fin-0[1-6].svg`.

## The close
Ask at setup (`/client-setup`).

## Our data (optional)
How the researcher reads the client's own data, read only.

## Carousel renderer (optional)
Leave empty to use HTML + headless Chrome (art-director default).

## Delivery
Ask at setup (`/client-setup`).

## Publishing (optional)
None: the team gets the files.

## Ledger
`LEARNINGS.md`: one row per post (date, topic, Test, Device, reach, follows).
