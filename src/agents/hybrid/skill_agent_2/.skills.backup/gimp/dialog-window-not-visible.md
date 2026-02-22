---
annotations: []
description: When GIMP dialogs/panels seem missing (off-screen, behind, or docks hidden)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: dialog-window-not-visible
---

When a GIMP **dialog** (e.g., Preferences) or **panel/dock** (Toolbox, Layers, etc.) seems to “not open”, it’s usually one of these cases.

## Case 1: A dialog opened behind another window / off-screen
1. Use your OS task switcher (**Alt+Tab**) to focus the dialog.
2. If it’s tiny/off-screen, with the dialog focused press **Alt+F10** to maximize (common on Linux window managers).

## Case 2: All docks/panels are hidden
- Press **Tab** to toggle docks hidden/visible.
- Or use **Windows > Hide Docks**.

## Case 3: A specific panel (Toolbox/Layers/etc.) is closed
1. Use the top menu **Windows**.
2. Click the panel name (e.g., **Toolbox**) to toggle it back on.
3. For others, use **Windows > Dockable Dialogs** and select the dialog you need.