---
annotations: []
description: Capture a still frame in VLC and locate the saved vlcsnap PNG
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vlc-snapshot-frame
---

## Take a snapshot in VLC
1. Make sure the VLC video window is focused.
2. Press **Shift+S** (or use **Video ▸ Take Snapshot**).
3. VLC writes a PNG named like `vlcsnap-YYYY-MM-DD-HHhMMmSSsNNN.png`.

## Find the file (default location)
- Usually saved in your Pictures folder (`~/Pictures` / `$(xdg-user-dir PICTURES)`).
- If multiple snapshots exist, sort by modified time to grab the newest.

## Rename/move to a required path (CLI)
```bash
pics=$(xdg-user-dir PICTURES 2>/dev/null || echo "$HOME/Pictures")
newest=$(ls -t "$pics"/vlcsnap-*.png 2>/dev/null | head -n 1)
cp -f "$newest" "$HOME/Desktop/interstellar.png"
```