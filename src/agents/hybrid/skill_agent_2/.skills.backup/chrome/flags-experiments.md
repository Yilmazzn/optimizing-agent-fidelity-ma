---
annotations: []
description: Use chrome://flags to toggle experiments and relaunch (UI rollouts, feature
  flags)
metrics:
  negative_impact: 0
  neutral_impact: 1
  positive_impact: 0
  times_followed: 0.5
  times_requested: 1
name: flags-experiments
---

## Toggle a flag and relaunch
1. Open `chrome://flags`.
2. Use **Search flags** to find the feature.
3. Change the dropdown (e.g., **Enabled** / **Disabled**).
4. Click **Relaunch** (blue button) to apply.

## Disable a staged UI rollout (example: Chrome Refresh 2023)
1. Open `chrome://flags`.
2. Search: `refresh 2023`.
3. For each matching flag, set to **Disabled** (often includes **Chrome Refresh 2023**, **Chrome WebUI Refresh 2023**, **Realbox Chrome Refresh 2023**, plus related sub-flags like New Tab button / font style).
4. Click **Relaunch**.

## Notes / pitfalls
- UI rollouts are often split across multiple flags; disabling only one may not fully revert the UI.
- Flag names/availability vary by version; if search fails, try `webui refresh`, `chrome refresh`, or `realbox`.
- To undo changes quickly, use **Reset all** on `chrome://flags` and **Relaunch**.