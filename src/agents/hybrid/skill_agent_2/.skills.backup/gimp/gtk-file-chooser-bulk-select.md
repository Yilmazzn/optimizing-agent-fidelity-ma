---
annotations: []
description: Bulk-select many files in GIMP/GTK file chooser (Ctrl+A needs file list
  focus)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: gtk-file-chooser-bulk-select
---

When selecting many files (e.g., **File > Open…**, **File > Open as Layers…**, **Export** dialogs), keyboard shortcuts can target the wrong widget if the file list doesn’t have focus.

## Select all files reliably
1. In the file chooser, **click one file inside the main file list/grid** (not the filename box, path/location field, or search box).
2. Press **Ctrl+A** to select all files in that folder view.
3. Click **Open/Add/Export** (whatever the dialog’s confirmation button is).

## If Ctrl+A edits a text field instead
- Click back into the **file list** to move focus there, then press **Ctrl+A** again.