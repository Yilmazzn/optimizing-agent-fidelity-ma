---
annotations: []
description: 'VS Code focus issues: stop editor stealing focus; jump from terminal
  to editor'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vscode-focus-management
---

## Case 1: Debugging pauses and VS Code forces focus back to the editor
1. Open Settings: **Ctrl+,**.
2. Search `debug.focusEditorOnBreak`.
3. Disable **Debug: Focus Editor On Break**.

Alternative (settings.json):
```json
"debug.focusEditorOnBreak": false
```

## Case 2: Add a shortcut to return focus from the integrated terminal to the editor
1. **Ctrl+Shift+P** → **Preferences: Open Keyboard Shortcuts (JSON)**.
2. Add a keybinding scoped to the terminal context:
```json
{
  "key": "ctrl+j",
  "command": "workbench.action.focusActiveEditorGroup",
  "when": "terminalFocus"
}
```
3. Save, click into the terminal, press your shortcut to confirm focus returns to the editor.

Note: Scoping with `when: "terminalFocus"` avoids global conflicts; if it doesn’t work, search the key in **Keyboard Shortcuts** UI to see what command wins in `terminalFocus`.