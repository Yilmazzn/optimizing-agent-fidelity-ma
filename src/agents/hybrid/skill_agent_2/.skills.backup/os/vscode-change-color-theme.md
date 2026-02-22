---
annotations: []
description: Change VS Code color theme; handle “Reload Window” prompt
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vscode-change-color-theme
---

## Open the Color Theme picker (2 reliable entry points)

### Method A: Command Palette
1. Press `Ctrl+Shift+P`.
2. Type `Preferences: Color Theme`.
3. Press `Enter`.

### Method B: Keyboard chord (sequential)
- Press `Ctrl+K`, **release**, then press `Ctrl+T`.
  - If you hold keys or press simultaneously, nothing obvious may happen.

## Apply a theme
1. In the picker, start typing the theme name.
2. Press `Enter` to apply the highlighted theme.

## If VS Code asks to reload/restart (common with Marketplace themes)
- If a modal or notification appears (e.g., **“Reload Window”**, **“Restart”**, **“OK”**), click it and **wait for VS Code to finish reloading** before judging whether the theme applied.
- After reload, open the theme picker again (`Ctrl+K`, `Ctrl+T`) if needed.

## If the requested theme name doesn’t match exactly
- Try close variants / built-in naming patterns.
  - Example: users may ask for **“Visual Studio Dark”**, but the built-in theme is **`Dark (Visual Studio)`**.
  - Searching for `Visual Studio`, `(Visual Studio)`, or `Dark (` can reveal it.
- Prefer selecting a built-in theme from this list before installing a Marketplace theme with a similar name.