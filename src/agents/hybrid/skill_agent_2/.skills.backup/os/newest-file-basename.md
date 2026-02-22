---
annotations: []
description: In shell scripts, pick newest file matching a glob and derive output
  name from its basename
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: newest-file-basename
---

## Pick the newest matching file (quick heuristic)
```bash
ODS=$(ls -t -- "$HOME/Desktop"/*.ods 2>/dev/null | head -n1)
[ -n "$ODS" ] || { echo "No .ods found"; exit 1; }
```

## Derive output path from the basename (strip extension)
```bash
CSV="${ODS%.ods}.csv"   # same directory, same basename
```

## Validate result
```bash
test -f "$CSV" && ls -l "$CSV"
```

## Notes / pitfalls
- `ls -t` is a pragmatic shortcut; it can misbehave with unusual filenames (e.g., embedded newlines) and if the glob matches nothing.
- Use `--` with `ls` to avoid filenames starting with `-` being treated as options.
- If you need maximum robustness, use `find` + sort by mtime, but `ls -t` is often good enough for "pick the file I just downloaded/edited" automation.