---
annotations: []
description: Safely clone into a directory; skip if exists and verify origin URL
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: guarded-clone-and-verify
---

## Guard against an existing destination folder
`git clone` fails if the destination directory exists (especially if non-empty). Guard explicitly before cloning.

```sh
cd /target/path || exit 1
if [ -e repo-name ]; then
  echo "repo-name exists; not cloning"
else
  git clone <repo-url>.git repo-name
fi
```

## Verify the clone succeeded (script-friendly)
```sh
cd /target/path/repo-name || exit 1
git rev-parse --is-inside-work-tree   # expect: true
git remote -v                         # confirm origin matches intended URL
# optional: git remote get-url origin
```

## If you need a fresh clone but the folder exists
Rename or delete explicitly, then re-run the clone:

```sh
cd /target/path || exit 1
mv repo-name repo-name.bak   # safer
# or: rm -rf repo-name        # destructive
```