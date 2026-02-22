---
annotations: []
description: Create/export animated GIFs in GIMP (from layers or extracted video frames)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: export-animation-gif
---

## Case 1: Export an animated GIF from an existing multi-layer image
1. **File > Export As…** (**Ctrl+Shift+E**).
2. Name it `something.gif` → **Export**.
3. In **Export Image as GIF**:
   - Check **As animation**.
   - Set **Delay between frames where unspecified**.
   - Set **Loop forever** as needed.
4. Click **Export** again to write the file.

## Case 2: Make an animated GIF from a video (extract frames → open as layers → export)
### A) Extract numbered frames (VLC scene filter, headless)
```bash
mkdir -p ~/Desktop/frames
cvlc -I dummy \
  --video-filter=scene \
  --scene-format=png \
  --scene-prefix=frame_ \
  --scene-path=$HOME/Desktop/frames \
  --scene-ratio=1 \
  --start-time=START \
  --stop-time=END \
  ~/Desktop/src.mp4 \
  vlc://quit
```
- `START`/`END` are seconds.
- `--scene-ratio=N` saves **1 image every N frames** (`1` = every frame).
- `vlc://quit` prevents `cvlc` from staying open.

### B) Import frames into GIMP as animation layers
1. **File > Open as Layers…**
2. Multi-select all frames (they should be named like `frame_00001.png`, `frame_00002.png`, …) → **Open**.
3. Preview: **Filters > Animation > Playback**.
4. If playback order is reversed: **Layer > Stack > Reverse Layer Order**.

### C) Set the delay (match source FPS)
1. Get video FPS:
   ```bash
   ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=nk=1:nw=1 video.mp4
   ```
2. Convert FPS → per-frame delay:
   - `delay_ms ≈ round(1000 / fps)` (e.g., **30 fps → ~33 ms**)
   - If FPS is a fraction:
     ```bash
fps=$(ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=nk=1:nw=1 video.mp4)
python3 - <<'PY'
import os
n,d=map(int,os.environ['fps'].split('/'))
print(round(1000/(n/d)))
PY
     ```
3. Use that number in **Delay between frames where unspecified** in the GIF export dialog.

## Optional: preview/optimize before exporting
- Playback: **Filters > Animation > Playback**.
- Reduce size: **Filters > Animation > Optimize (for GIF)**.

## Notes / pitfalls
- The GIF export has a **second dialog**; clicking **Cancel** there aborts export (no `.gif` is created).
- If colors/banding look bad, try **Image > Mode > Indexed…** (reduce colors / adjust dithering) before exporting.