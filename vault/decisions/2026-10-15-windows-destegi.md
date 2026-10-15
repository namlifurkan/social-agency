---
title: Ajans Windows + Claude desktop uygulamasında çalışır
date: 2026-10-15
tags: [karar, windows, reelkit]
related: [2026-10-15-opencv-5-cascade-yok, 2026-10-15-client-setup-onboarding]
---

> Proje: [[Social Agency]] · Hub: [[Social Agency — Decisions]]

# Ajans Windows + Claude desktop uygulamasında çalışır

## Karar
Ekip Windows'ta Claude desktop uygulamasını kullanıyor; repo iki platformda da çalışacak şekilde düzenlendi:
- Yüz algılama: Mac'te Apple Vision (`faces.swift`), diğer yerlerde OpenCV Haar (`opencv-python-headless<5`).
- `studio/reelkit` symlink'leri kaldırıldı; script'ler `kit/reelkit`'i göreli `sys.path` ile bulur (Windows git symlink'i düz dosya yapar).
- Örnek reel build'leri (sadece script ve notlar) `kit/reference/`'a kopyalandı; önceden sadece founder'ın Mac'inde, Riffiter'da gitignore'luydu.
- Chrome yolu, `python` vs `python3`, venv `Scripts/` yolu skill'lerde iki platform için yazılı; `PYTHONUTF8=1` proje ayarında.

## Alternatifler
- WSL: ekip için kurulumu ağır.
- Sadece Mac: ekip kullanamaz.

## Related
- [[2026-10-15-opencv-5-cascade-yok]] — Windows yüz algılamasını kurarken çıkan sorun
- [[2026-10-15-client-setup-onboarding]] — kurulumda Windows araçları
