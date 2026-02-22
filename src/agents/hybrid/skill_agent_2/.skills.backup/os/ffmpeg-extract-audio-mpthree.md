---
annotations: []
description: Extract audio-only MP3 from a local video file using ffmpeg (-vn, -q:a)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: ffmpeg-extract-audio-mpthree
---

## Convert video (MP4/MOV/etc.) → audio-only MP3 (re-encode)
```bash
cd ~/Desktop   # or wherever the file is
ffmpeg -y -i "input.mp4" -vn -c:a libmp3lame -q:a 2 "output.mp3"
```
Notes:
- `-vn` drops the video stream.
- `-q:a 2` is good VBR quality (lower = higher quality).
- If multiple audio tracks, pick one explicitly: add `-map 0:a:0`.

## Avoid re-encoding (extract original audio)
Use this when you don’t specifically need MP3.
```bash
ffmpeg -y -i "input.mp4" -vn -c:a copy "output.m4a"
```

## Quick verification
```bash
file "output.mp3"  # or output.m4a
ffprobe -hide_banner "output.mp3" | head
```