---
annotations: []
description: Find config files when a project folder contains repo subdirectories
  (ls + find -maxdepth)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: nested-repo-config
---

When a file "should be" in a project folder but `cat path/to/file` fails, first verify you’re in the actual repo directory (not its parent).

## Check whether the repo is nested
1. List the folder you were told to use:
   - `ls -la ~/Code/Website`
2. If you see repo-like subfolders, descend into the likely one (look for `.git`, `README*`, etc.).

## Search for the config file without assuming the path
1. Use a bounded recursive search (avoid scanning your whole home directory):
   - `find ~/Code/Website -maxdepth 3 -type f -name '_config.y*ml'`
2. Inspect/open the returned path(s) and use that real location.

## If you’re not sure which subfolder is the repo
- Find git repos quickly:
  - `find ~/Code/Website -maxdepth 3 -type d -name .git -print`