---
annotations: []
description: Install a locally downloaded Chrome extension via “Load unpacked” (folder
  with manifest.json)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: load-unpacked-extension
---

## Identify whether the extension is already unpacked
- **“Load unpacked” requires selecting a folder** whose top level contains `manifest.json` (pick the *parent folder*, not the file).
- If you only have a `.zip`/`.crx`, extract it first; you need a folder tree on disk.

### Quick check (Linux/macOS terminal)
1. Look for archives:
   - `find ~/Desktop -maxdepth 2 -type f \( -iname '*.zip' -o -iname '*.crx' \) -print`
2. Find the unpacked extension root:
   - `find ~/Desktop -maxdepth 3 -type f -iname 'manifest.json' -print`
3. Use the **parent directory** of the found `manifest.json` as the folder to load.

## Load the folder in Chrome
1. In the address bar (Ctrl+L), open: `chrome://extensions/`
2. Toggle **Developer mode** (top-right). If you don’t see **Load unpacked**, Developer mode is off.
3. Click **Load unpacked**.
4. In the file chooser, select the **folder that contains `manifest.json`** (extension root) → **Select**.
5. Confirm the extension appears and is enabled; optionally pin it via the puzzle-piece **Extensions** icon.