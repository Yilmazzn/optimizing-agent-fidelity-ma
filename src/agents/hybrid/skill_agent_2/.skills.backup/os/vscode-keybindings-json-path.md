---
annotations: []
description: Edit VS Code keybindings/settings JSON (disable defaults, validate JSON)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: vscode-keybindings-json-path
---

## Open the *editable* JSON from inside VS Code
1. `Ctrl+Shift+P`.
2. For keybindings: run **Preferences: Open Keyboard Shortcuts (JSON)**.
   - Avoid **Preferences: Open Default Keyboard Shortcuts (JSON)** (read-only; edits won’t apply).
3. For settings: run **Preferences: Open User Settings (JSON)** or **Preferences: Open Workspace Settings (JSON)**.
4. If the Command Palette seems stuck / doesn’t execute, press `Esc` and retry.

## Common file locations (edit outside the GUI)
### Keybindings
- VS Code (Linux): `~/.config/Code/User/keybindings.json`
- VSCodium (Linux): `~/.config/VSCodium/User/keybindings.json`

### Settings
- Workspace: `.vscode/settings.json`
- User settings typical paths:
  - Linux: `~/.config/Code/User/settings.json`
  - macOS: `~/Library/Application Support/Code/User/settings.json`
  - Windows: `%APPDATA%\Code\User\settings.json`

## Disable a *default* keybinding (non-obvious)
Default bindings can’t be deleted; disable them by adding a user override whose `command` is prefixed with `-`.

### Option A: UI (writes the override)
1. `Ctrl+Shift+P` → **Preferences: Open Keyboard Shortcuts**.
2. Search for the shortcut/command.
3. Right-click the row → **Remove Keybinding**.

### Option B: keybindings.json
Add an entry like:
```json
{
  "key": "ctrl+f",
  "command": "-list.find",
  "when": "listFocus && listSupportsFind"
}
```
**Pitfall:** copy the exact `when` clause from the default binding; omitting/mismatching it may disable the command in more contexts than intended (or fail to disable the specific default binding).

## Validate JSON when changes don’t apply
Broken JSON can cause settings/keybindings to be ignored.

### CLI check
```bash
python3 -m json.tool ~/.config/Code/User/keybindings.json >/dev/null
python3 -m json.tool ~/.config/Code/User/settings.json >/dev/null
```
- If invalid, `json.tool` prints a line/column error (missing comma/brace).

### Reformat (only after it parses)
- Command Palette: **Format Document** (won’t fix syntax errors).

## Force VS Code to pick up changes
- Command Palette: **Developer: Reload Window** (or restart VS Code).