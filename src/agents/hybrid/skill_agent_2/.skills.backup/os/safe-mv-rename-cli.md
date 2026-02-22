---
annotations: []
description: Safely move/rename via mv without overwriting (mv -n/-i, -T, find path)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: safe-mv-rename-cli
---

When organizing files from the terminal, use `mv` defensively to avoid overwrites and “moved into directory” surprises.

## Move files into a folder without overwriting
- Prefer:
  ```bash
  mv -n -v -- *.pdf ~/Desktop/problematic/
  ```
  - `-n` = do not overwrite existing destination files
  - `-v` = show what happened
  - `--` = stop option parsing (protects names starting with `-`)
- If you want prompts on collisions instead:
  ```bash
  mv -i -- file.pdf ~/Desktop/problematic/
  ```

## Rename something when you don’t know its exact path (bounded find + safe mv)
### Rename a folder
```bash
old_path=$(find ~ -maxdepth 4 -type d -name 'OLD_NAME' -print -quit)
mv -nT -- "$old_path" "$(dirname -- "$old_path")/NEW_NAME"
```
### Rename a file
```bash
old_path=$(find ~ -maxdepth 4 -type f -name 'OLD_NAME.ext' -print -quit)
mv -nT -- "$old_path" "$(dirname -- "$old_path")/NEW_NAME.ext"
```
- `-T` treats the destination as a *path*, not a directory target (avoids “move into directory” behavior when the destination exists as a dir).
- Keep `-n` to prevent overwriting if `NEW_NAME` already exists.

## Verify quickly
- Folder: `test -d "$(dirname -- "$old_path")/NEW_NAME" && ! test -d "$old_path"`
- File: `test -f "$(dirname -- "$old_path")/NEW_NAME.ext" && ! test -f "$old_path"`

Note: If `mv -T` isn’t available (non-GNU systems), omit `-T` and be extra careful that the destination path is what you intend.