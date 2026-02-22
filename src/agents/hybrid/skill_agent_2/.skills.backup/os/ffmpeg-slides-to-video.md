---
annotations: []
description: Turn exported slide PNGs into an H.264 MP4 via ffmpeg (scale/pad) and
  play in VLC
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: ffmpeg-slides-to-video
---

Use when you have slide images (e.g., exported from LibreOffice/Impress) and need a playable video file.

## Case 1: One PNG → MP4 (hold still for N seconds)
```bash
# 5-second clip at 30fps, letterboxed to 720p, broadly compatible pixel format
ffmpeg -y -loop 1 -t 5 -i slide.png \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -r 30 -c:v libx264 out.mp4
```

## Case 2: Numbered PNG sequence → slideshow MP4 (constant duration per slide)
Assume files like `slide_001.png`, `slide_002.png`...
```bash
# 5 seconds per slide => input framerate = 1/5
ffmpeg -y -framerate 1/5 -i slide_%03d.png \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -r 30 -c:v libx264 out.mp4
```

Notes:
- `format=yuv420p` avoids players that can’t handle yuv444p.
- The scale+pad keeps aspect ratio and centers the slide (no stretching).

## Play from terminal (exit when done)
```bash
vlc --play-and-exit out.mp4
```