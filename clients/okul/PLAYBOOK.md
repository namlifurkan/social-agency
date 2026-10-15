# okul.com.tr — client playbook

Prefilled from the client's repos and the vault on 2026-10-15; `/client-setup` confirms it with the team.
The generic skills read it and it wins over them.

## Who and where
okul.com.tr: "Türkiye'nin en büyük okul arama platformu", bringing families looking for a school
together with private and state schools at every level (since 2016). Repo
`/Users/furkannamli/project/okul`.

Accounts (site footer): Instagram `@okul.com.tr`, Facebook `okulcomtr`, X `@okulcomtr`, LinkedIn
`okul-com-tr`, YouTube `@Okulcomtr`. No TikTok found. Which ones we post for: ask at setup.

## Audience and stories
Parents choosing a school (B2C); schools buy leads and visibility (B2B). Numbers the site uses:
30.000+ okul, "her ay milyonlarca aile". Never the old "100 bin veli" target.

Content the product can back: school search, Okul Karşılaştırma (up to 5 side by side), fees and
discounts, ~41.5k veli yorumu, "Çocuğuma Uygun Eğitim Yaklaşımı" test (11 soru), "Çocuğuma Uygun
Okulu Bul", campaigns (`/kampanyalar`), bursluluk sınavları, "Türkiye'nin En İyi Kolejleri", free
education advisor ("Ücretsiz Eğitim Danışmanı").

Never: exact fees (shown only to logged-in users; listed price excludes özel burs), "every
bursluluk is free", a reviewer's or a child's name (KVKK).

## Look
The values live in `brand.json`: `colors` (hex for `bg`, `ink`, `accent`), `fonts` (family names,
TTF/OTF files in `fonts/`), `logo` (file in this folder, SVG or transparent PNG) and
`narrator_voice`. Here: how the brand should feel, where the wordmark sits, what never to do.

From the site (`resources/assets/styles/responsive.css`): accent `--okul-primary` #FF495C, text
#273444, second brand colour blue #00A0DF (the ".com.tr" in the logo), sky surface #F2FAFD.
Website fonts are Raleway (display) and Source Sans Pro, here as its successor Source Sans 3.
`logo.svg` is the plain red/blue wordmark; the site's `yatay_logo_10.svg` carries the "10 yaşında"
badge, for anniversary posts only.

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
