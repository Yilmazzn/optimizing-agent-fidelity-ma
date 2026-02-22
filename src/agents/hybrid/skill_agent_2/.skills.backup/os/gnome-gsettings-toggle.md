---
annotations: []
description: Use gsettings to change GNOME settings (discover keys, wallpaper, screencast
  path)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: gnome-gsettings-toggle
---

## Before you use `gsettings`
- Run as the logged-in desktop user (**no `sudo`**) so it updates that user’s dconf DB.
- Changes typically apply immediately.

## Case 1: Toggle a known setting (example: disable “Dim screen when inactive”)
1. Check current value:
   ```bash
   gsettings get org.gnome.settings-daemon.plugins.power idle-dim
   ```
2. Turn off dimming:
   ```bash
   gsettings set org.gnome.settings-daemon.plugins.power idle-dim false
   ```
3. Revert to default:
   ```bash
   gsettings reset org.gnome.settings-daemon.plugins.power idle-dim
   ```

## Case 2: Find the right schema/key when the UI option is hard to locate
1. List candidate schemas:
   ```bash
   gsettings list-schemas | grep -i <keyword>
   ```
2. List keys in a schema:
   ```bash
   gsettings list-keys <schema> | grep -i <keyword>
   ```
3. Search keys/values for a hint:
   ```bash
   gsettings list-recursively <schema> | grep -i <keyword>
   ```
4. Read a key’s description:
   ```bash
   gsettings describe <schema> <key>
   ```

## Case 3: Set GNOME wallpaper (handle dark appearance mode)
1. Build a file URI from an **absolute path** (no `~`):
   ```bash
   img="/abs/path/to/image.jpg"
   uri="file://$img"   # results in file:///abs/path...
   ```
2. Set both wallpaper keys (light + dark):
   ```bash
   gsettings set org.gnome.desktop.background picture-uri "$uri"
   gsettings set org.gnome.desktop.background picture-uri-dark "$uri"
   ```
   If `picture-uri-dark` isn’t supported on your GNOME build, that command will fail; then only `picture-uri` is available.
3. Optional (varies by distro/theme): lock screen wallpaper:
   ```bash
   gsettings set org.gnome.desktop.screensaver picture-uri "$uri"
   ```

## Case 4: Extract a still from a video, then set as wallpaper
```bash
vid="/path/to/video.mp4"
ts="00:12:34"                  # HH:MM:SS (or seconds like 754.2)
out="$HOME/Pictures/wallpaper.jpg"

# Crop-to-fill 1920x1080 (no stretching): scale up then crop
ffmpeg -y -ss "$ts" -i "$vid" -frames:v 1 \
  -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" \
  "$out"

uri="file://$out"
gsettings set org.gnome.desktop.background picture-uri "$uri"
gsettings set org.gnome.desktop.background picture-uri-dark "$uri"
```
Tip: put `-ss` **before** `-i` for speed (fast seek; usually fine for wallpapers).

## Case 5: Change GNOME screencast save folder
GNOME versions/distros may not ship a screencast path key at all.

### A) If a screencast path key exists
1. Search for likely schemas/keys (keywords often work):
   ```bash
   gsettings list-schemas | grep -i -E 'screencast|recorder|shell|media-keys'
   ```
2. Inspect candidate keys:
   ```bash
   gsettings list-keys <schema> | grep -i -E 'screencast|record|path|dir'
   ```
3. Verify current value then set it:
   ```bash
   gsettings get <schema> <key>
   gsettings set <schema> <key> "$HOME/Desktop"
   ```

### B) If no screencast path key exists: change the XDG Videos directory
Many apps (and some GNOME recorders) default to the XDG Videos directory.
1. Check current config:
   ```bash
   cat ~/.config/user-dirs.dirs
   ```
2. Backup then set `XDG_VIDEOS_DIR` (example: to Desktop):
   ```bash
   cp -a ~/.config/user-dirs.dirs ~/.config/user-dirs.dirs.bak.$(date +%F_%H%M%S)
   sed -i 's|^XDG_VIDEOS_DIR=.*$|XDG_VIDEOS_DIR="$HOME/Desktop"|' ~/.config/user-dirs.dirs
   ```
3. Apply and verify:
   ```bash
   xdg-user-dirs-update
   xdg-user-dir VIDEOS
   ```