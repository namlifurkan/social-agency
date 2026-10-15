---
title: Ekip kurulumu /client-setup görüşmesiyle yapılır
date: 2026-10-15
tags: [karar, onboarding, elevenlabs]
related: [2026-10-15-marka-brand-json, 2026-10-15-windows-destegi]
---

> Proje: [[Social Agency]] · Hub: [[Social Agency — Decisions]]

# Ekip kurulumu /client-setup görüşmesiyle yapılır

## Karar
Yeni müşteri ya da yeni ekip üyesi `/client-setup <client>` çalıştırır. Claude makineyi kontrol eder (ElevenLabs anahtarı, araçlar), markayı repodan/siteden önerir, kapanışı ("LINK IN BIO" ya da başka), teslimi ve hedefi sorar, seslendirici sesini kişinin kendi ElevenLabs hesabında tasarlatır (`kit/reelkit/voice.py`).

## Gerekçe
Ekip kendi tercihini yapabilmeli (founder, 2026-10-15). Repodan bulunabilen her şey önceden doldurulur, sadece kararlar sorulur. API anahtarı sohbete yapıştırılmaz, terminalden `.env`'ye eklenir.

## Alternatifler
- Founder her müşteriyi elle kurar: ekip büyüyünce darboğaz.

## Related
- [[2026-10-15-marka-brand-json]] — görüşmenin doldurduğu alanlar
- [[2026-10-15-windows-destegi]] — ekip Windows kullanıyor
