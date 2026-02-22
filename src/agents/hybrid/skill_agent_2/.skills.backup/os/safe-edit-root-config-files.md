---
annotations: []
description: Safely edit/patch files from shell (root-owned too) and capture run logs
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: safe-edit-root-config-files
---

When editor helpers aren’t available, use portable shell patterns. For root-owned files, avoid `sudo cmd > /etc/file` (redirection happens as your user).

## Inspect + locate the edit
```bash
sed -n '1,200p' path/to/file
nl -ba path/to/file | sed -n '1,200p'   # with line numbers
```

## Backup first (before scripted edits)
```bash
cp -a path/to/file path/to/file.bak
# root-owned:
sudo cp -a /path/to/FILE /path/to/FILE.bak
```

## Case 1: Manual edit of a root-owned file (safest)
```bash
sudoedit /path/to/FILE
```

## Case 2: Overwrite/replace a whole file (portable)
### Non-root file
```bash
cat > path/to/file <<'EOF'
...new content...
EOF
```

### Root-owned file (use tee, not `>`)
```bash
cat <<'EOF' | sudo tee /etc/file >/dev/null
...new content...
EOF
```

## Case 3: Scripted edits (non-root or root) via temp → validate → atomic replace
1) Create temp **in same dir** (atomic `mv`):
```bash
DIR=$(dirname /path/to/FILE)
BASE=$(basename /path/to/FILE)
TMP=$(mktemp --tmpdir="$DIR" ".${BASE}.XXXXXX")
# root-owned temp:
# TMP=$(sudo mktemp --tmpdir="$DIR" ".${BASE}.XXXXXX")
```
2) Write new content:
```bash
generate_cmd > "$TMP"          # non-root
# or:
generate_cmd | sudo tee "$TMP" >/dev/null
```
3) Validate (examples):
```bash
python3 -m json.tool "$TMP" >/dev/null   # JSON
python3 -m py_compile your_script.py      # Python
```
4) Replace:
```bash
mv -f "$TMP" /path/to/FILE
# root-owned:
# sudo mv -f "$TMP" /path/to/FILE
```

## Case 4: In-place substitutions (small changes; multiline-safe)
Prefer Perl (portable; `sed -i` varies by OS):
```bash
perl -0777 -pe 's/OLD/NEW/g' -i path/to/file
```

## Case 5: Patch text via a small script (simple insert/replace)
```bash
python3 - <<'PY'
from pathlib import Path
p = Path('file.py')
text = p.read_text()
text = text.replace('TODO_MARKER', "TODO_MARKER\n    your_code_here")
p.write_text(text)
PY
```

## Capture run output while still seeing it
```bash
python3 your_script.py | tee log.txt
python3 your_script.py 2>&1 | tee log.txt   # stdout+stderr
```

## If you suspect the file was truncated/corrupted
```bash
sudo test -s /path/to/FILE || echo "FILE is empty"
sudo cp -a /path/to/FILE.bak /path/to/FILE
```