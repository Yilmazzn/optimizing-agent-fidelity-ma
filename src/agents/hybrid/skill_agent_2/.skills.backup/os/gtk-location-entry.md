---
annotations: []
description: In GTK file chooser, press Ctrl+L to type a folder path
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: gtk-location-entry
---

## Jump to a directory in a GTK file chooser
1. In an Open/Save/Export dialog, press **Ctrl+L** to focus the **Location** (path) field.
2. Type/paste a path (e.g., `~/Desktop` or `/home/<user>/Desktop`).
3. Press **Enter** to navigate.

Notes: If `~` doesn’t expand, use the full `/home/<user>/...` path. Press **Esc** to return focus to the file list.