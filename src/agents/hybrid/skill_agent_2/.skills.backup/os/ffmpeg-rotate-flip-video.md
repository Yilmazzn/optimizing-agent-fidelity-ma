---
annotations: []
description: Rotate/flip an upside-down or mirrored video via ffmpeg (transpose/hflip/vflip)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: ffmpeg-rotate-flip-video
---

Use when a video is upside down, rotated, or mirrored and you want a fast CLI fix (Linux).

## Workflow
1. Decide input + output paths (Desktop is usually `~/Desktop`).
2. Run `ffmpeg` with the appropriate video filter.
3. Verify the output file exists (and optionally play it).

## Common transforms (H.264 MP4 output)
```bash
# Upside-down / 180° (equivalent to rotate 180)
ffmpeg -y -i "input.mp4" -vf "hflip,vflip" \
  -c:v libx264 -crf 18 -preset veryfast \
  -c:a copy "~/Desktop/output.mp4" 

# Rotate 90° right (clockwise)
ffmpeg -y -i "input.mp4" -vf "transpose=1" \
  -c:v libx264 -crf 18 -preset veryfast \
  -c:a copy "~/Desktop/output.mp4"

# Rotate 90° left (counter-clockwise)
ffmpeg -y -i "input.mp4" -vf "transpose=2" \
  -c:v libx264 -crf 18 -preset veryfast \
  -c:a copy "~/Desktop/output.mp4"

# Mirror/flip only
ffmpeg -y -i "input.mp4" -vf "hflip" -c:v libx264 -crf 18 -preset veryfast -c:a copy "~/Desktop/output.mp4"
ffmpeg -y -i "input.mp4" -vf "vflip" -c:v libx264 -crf 18 -preset veryfast -c:a copy "~/Desktop/output.mp4"
```

Notes:
- `-c:a copy` keeps audio without re-encoding; if it errors, replace with `-c:a aac -b:a 192k`.

## Quick verification
```bash
ls -lh ~/Desktop/output.mp4
vlc --play-and-exit ~/Desktop/output.mp4  # optional
```