---
annotations: []
description: Wrap lines in VS Code at a specific column (wordWrapColumn)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vscode-word-wrap-column
---

## Set soft-wrap at a fixed column (User or Workspace)
1. Open Settings: `Ctrl+,` (or Command Palette → **Preferences: Open Settings (UI)**).
2. In the Settings search box, search **word wrap**.
3. Set **Editor: Word Wrap** to **wordWrapColumn**.
4. Set **Editor: Word Wrap Column** to the desired number (e.g., `50`, `80`, `100`).

### Notes / pitfalls
- Setting only **Word Wrap Column** does nothing if **Word Wrap** is still **off** (or **on** = wraps at viewport width).
- Alternative mode: **bounded** wraps at the smaller of the viewport width and **Word Wrap Column**.

## JSON equivalent (useful when editing settings.json)
```json
{
  "editor.wordWrap": "wordWrapColumn",
  "editor.wordWrapColumn": 80
}
```
- User settings vs workspace settings differ: workspace lives in `.vscode/settings.json`.