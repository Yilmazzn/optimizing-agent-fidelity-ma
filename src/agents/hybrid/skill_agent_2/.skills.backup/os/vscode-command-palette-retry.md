---
annotations: []
description: When a VS Code Command Palette command does nothing after Enter
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vscode-command-palette-retry
---

## Run the intended Command Palette item reliably
1. Press `Ctrl+Shift+P`.
2. Type enough of the command that you can see the **exact** intended entry.
3. Use `↑/↓` to explicitly highlight that entry (don’t rely on whatever is preselected).
4. Press `Enter` once.

## If it still doesn’t execute
- Press `Esc` to close the palette, then repeat steps 1–4.
- Don’t keep typing into a “stuck” palette; you’ll often just change the filter instead of executing the command.