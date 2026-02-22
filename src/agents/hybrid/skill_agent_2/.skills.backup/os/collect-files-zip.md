---
annotations: []
description: Bundle selected files into a folder and create a clean .zip via CLI
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: collect-files-zip
---

## Collect a known set of files into a staging folder
1. Create a destination folder:
   ```bash
   DEST="$HOME/Desktop/presenter"
   mkdir -p "$DEST"
   ```
2. Copy the chosen files (explicit list; use `-n` to avoid overwriting on name collisions):
   ```bash
   cp -n -v \
     "$HOME/Desktop/<source-folder>/<file1>.jpg" \
     "$HOME/Desktop/<source-folder>/<file2>.jpg" \
     "$DEST/"
   ```

## Zip it with clean paths (run `zip` from the folder’s parent)
```bash
cd "$HOME/Desktop" || exit 1
rm -f presenter.zip
zip -r presenter.zip presenter/
```

## Verify
```bash
ls -l presenter presenter.zip
unzip -l presenter.zip | head
```

## Notes / pitfalls
- Zipping from the parent directory (e.g., `Desktop`) avoids embedding full/absolute paths in the archive.
- If `zip`/`unzip` are missing on Debian/Ubuntu: `sudo apt-get install zip unzip`.
- If you *do* want overwrites during the copy step, use `cp -f` instead of `cp -n`.