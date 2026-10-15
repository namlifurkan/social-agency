---
title: Müşteri markası brand.json'da yapılandırılmış tutulur
date: 2026-10-15
tags: [karar, marka, client-setup]
related: [2026-10-15-client-setup-onboarding]
---

> Proje: [[Social Agency]] · Hub: [[Social Agency — Decisions]]

# Müşteri markası brand.json'da yapılandırılmış tutulur

## Karar
Her müşterinin logosu, renkleri (`bg`, `ink`, `accent`), fontları (`display`, `body`) ve seslendirici sesi `clients/<client>/brand.json`'da durur. `PLAYBOOK.md` "Look" bölümü sadece markanın nasıl kullanılacağını anlatır.

## Gerekçe
Önceden marka PLAYBOOK'ta düz metindi; art-director her render'da yorumluyordu ve renkler kayabiliyordu. Yapılandırılmış alan ekibin kurulumunu da kolaylaştırıyor.

## Alternatifler
- PLAYBOOK'ta düz metin (eski hal): esnek ama tutarsız.
- Ayrı `tokens.css`: sadece HTML renderer'a yarar, reel script'leri okuyamaz.

## Related
- [[2026-10-15-client-setup-onboarding]] — kurulum görüşmesi bu dosyayı doldurur
