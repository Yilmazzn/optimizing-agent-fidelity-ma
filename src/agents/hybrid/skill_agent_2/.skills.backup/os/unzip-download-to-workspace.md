---
annotations: []
description: Extract a ZIP you just downloaded into a specific folder (unzip -d, newest
  file heuristic)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: unzip-download-to-workspace
---

## Extract the newest downloaded ZIP into a workspace folder
1. (Optional) Pick the newest ZIP in Downloads:
   ```bash
   ZIP=$(ls -t -- "$HOME/Downloads"/*.zip 2>/dev/null | head -n1)
   echo "$ZIP"
   ```
2. Choose a target directory (create if needed):
   ```bash
   TARGET="$HOME/Projects"
   mkdir -p "$TARGET"
   ```
3. Unzip into the target directory:
   ```bash
   unzip -o "$ZIP" -d "$TARGET"
   ```
4. Verify what was created:
   ```bash
   ls -la "$TARGET"
   # or: unzip -l "$ZIP" | head
   ```
5. (Optional) Open the target folder in the GUI file manager:
   ```bash
   xdg-open "$TARGET"
   ```

## Notes / pitfalls
- `-d` controls the extraction destination; most scaffolds already contain a top-level folder, so you usually *don’t* need to `mkdir` a project subfolder first.
- `-o` overwrites existing files without prompting; use `-n` instead if you want “never overwrite”.
- If `unzip` is missing: `sudo apt-get install unzip` (Debian/Ubuntu).