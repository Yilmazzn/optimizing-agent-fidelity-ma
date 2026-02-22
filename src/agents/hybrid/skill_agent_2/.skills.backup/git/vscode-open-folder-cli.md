---
annotations: []
description: Open VS Code in a specific folder from terminal (code . / PATH)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vscode-open-folder-cli
---

## Open a project folder directly
1. In a terminal, change to the target directory and open VS Code as that workspace:
   - `cd /path/to/project && code .`
   - (Equivalent without `cd`: `code /path/to/project`)

## If `code` is not found
- Ensure VS Code’s CLI launcher is on your `PATH`.
- If available: Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) → **Shell Command: Install 'code' command in PATH**.
- Otherwise, install/enable the `code` command via your OS/package manager method for VS Code.

## Optional flags
- Reuse an existing window: `code -r .`
- Force a new window: `code --new-window .`