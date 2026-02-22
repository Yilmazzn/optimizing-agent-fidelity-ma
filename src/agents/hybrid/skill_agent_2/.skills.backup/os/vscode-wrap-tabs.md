---
annotations: []
description: Wrap VS Code tabs (Wrap Tabs); avoid Settings links; verify Show Tabs
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vscode-wrap-tabs
---

## Enable tab wrapping
1. Open Settings (UI): `Ctrl+,`.
2. In the Settings search box, type **wrap tabs**.
3. Enable **Workbench › Editor: Wrap Tabs**.

### Pitfall: Settings search results contain clickable links
Search results can include links to related settings (e.g., **Workbench › Editor: Show Tabs**). Ignore them unless troubleshooting; clicking can bounce you away from the toggle you meant to change.

## If tabs still don’t wrap
1. In Settings search, type **show tabs**.
2. Ensure **Workbench › Editor: Show Tabs** is enabled (wrapping won’t matter if tabs are hidden).
3. Search **wrap tabs** again (or use Back) to return to the original toggle.