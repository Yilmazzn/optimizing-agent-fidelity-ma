---
annotations: []
description: Check/install Ubuntu apps via Snap (snap list/install; detect already
  installed)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: snap-install-check
---

## Pre-check: is Snap available?
- `command -v snap` (if missing, Snap isn’t installed/available on this system).

## Check whether an app is already installed (Snap)
- Fast check:
  - `snap list <app>`
    - Installed → prints a row for `<app>`.
    - Not installed → error like `snap "<app>" not found`.
- Scriptable check (no output):
  - `snap list <app> >/dev/null 2>&1`

## Install via Snap
1. `sudo snap install <app>` (example: `sudo snap install spotify`).
2. Verify:
   - `snap list <app>`

## Note
- This confirms the app is installed as a *snap* (not apt/flatpak).