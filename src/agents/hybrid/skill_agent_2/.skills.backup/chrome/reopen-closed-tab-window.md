---
annotations: []
description: Restore a recently closed tab/window in Chrome (Ctrl+Shift+T, History
  > Recently closed)
metrics:
  negative_impact: 0
  neutral_impact: 1
  positive_impact: 0
  times_followed: 1.0
  times_requested: 1
name: reopen-closed-tab-window
---

## Reopen last closed tab/window (fast)
1. Focus the Chrome window.
2. Press **Ctrl+Shift+T** (Windows/Linux) or **Cmd+Shift+T** (macOS).
3. Repeat to reopen more items (most recently closed first).

## Reopen a specific tab/window (deterministic)
Use this if cycling **Ctrl/Cmd+Shift+T** isn’t bringing back the exact item quickly.
1. Open **⋮ (Chrome menu)**.
2. Go to **History**.
3. Under **Recently closed**, click the exact tab/window you want to restore.