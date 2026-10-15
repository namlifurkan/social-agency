---
title: OpenCV 5'te CascadeClassifier yok
date: 2026-10-15
tags: [incident, opencv, reelkit]
related: [2026-10-15-windows-destegi]
---

> Proje: [[Social Agency]] · Hub: [[Social Agency — Incidents]]

# OpenCV 5'te CascadeClassifier yok

## Semptom
`layout.py` Windows yedeği `AttributeError: module 'cv2' has no attribute 'CascadeClassifier'` verdi.

## Kök neden
`pip install opencv-python-headless` 5.0'ı kuruyor; OpenCV 5 Haar cascade'leri ana paketten çıkardı.

## Çözüm
`opencv-python-headless<5` ile sabitlendi (story-reel skill'indeki kurulum satırı). Daha iyi algılama gerekirse YuNet (`FaceDetectorYN`, ONNX model) yolu var.

## Related
- [[2026-10-15-windows-destegi]] — bu yedeğin neden var olduğu
