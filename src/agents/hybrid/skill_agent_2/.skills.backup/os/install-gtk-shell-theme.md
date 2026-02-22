---
annotations: []
description: Install/switch GNOME GTK themes + enable Shell themes (User Themes) on
  Ubuntu
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: install-gtk-shell-theme
---

## Install a theme (per-user)
1. Create a themes directory:
   ```bash
   mkdir -p ~/.themes
   ```
   *(Some distros also look in `~/.local/share/themes`.)*
2. Extract the downloaded theme archive into it:
   ```bash
   tar -xf ~/Downloads/THEME.tar.* -C ~/.themes
   ```
3. Verify the folder layout:
   - You should have `~/.themes/<ThemeName>/` (or variants like `-Dark`).
   - If you see an extra nesting level (e.g., `~/.themes/THEME/<ThemeName>/`), move the inner `<ThemeName>` folder(s) up.

*(System-wide themes live in `/usr/share/themes/<ThemeName>/`.)*

## Switch the GTK (Applications) theme
- **GUI:** GNOME Tweaks → **Appearance** → **Applications**.
- **CLI:**
  ```bash
  gsettings set org.gnome.desktop.interface gtk-theme 'Orchis'
  ```

## Enable + switch the GNOME Shell theme (top bar, overview)
### Prerequisites
- The theme must include: `gnome-shell/` (e.g., `~/.themes/<ThemeName>/gnome-shell/`).
- The **User Themes** extension must be enabled.

### Install required tools/extensions (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install gnome-tweaks gnome-shell-extensions
```
(“User Themes” is included in `gnome-shell-extensions`.)

### Enable “User Themes”
1. Open the **Extensions** app (press **Super**, type **Extensions**).
2. Toggle **User Themes** → **On**.
3. Open **Tweaks** → **Appearance** → **Shell** and select the theme.

## Troubleshooting: “User Themes” missing / Shell dropdown disabled
### Case 1: Extension not listed after install
- Confirm install: `apt policy gnome-shell-extensions`
- Log out/in (or reboot), then re-check **Extensions**.

### Case 2 (Ubuntu GNOME mode): extension exists but won’t show/enable
Some Ubuntu GNOME sessions hard-code enabled extensions via `/usr/share/gnome-shell/modes/ubuntu.json`.

1. Confirm the extension exists on disk:
   ```bash
   ls /usr/share/gnome-shell/extensions/user-theme@gnome-shell-extensions.gcampax.github.com
   ```
2. Back up + edit the mode file:
   ```bash
   sudo cp /usr/share/gnome-shell/modes/ubuntu.json /usr/share/gnome-shell/modes/ubuntu.json.bak
   sudoedit /usr/share/gnome-shell/modes/ubuntu.json
   ```
3. Add this UUID to the JSON `enabledExtensions` list:
   ```json
   "user-theme@gnome-shell-extensions.gcampax.github.com"
   ```
4. Restart GNOME Shell:
   - Most reliable: log out/in.
   - On X11: **Alt+F2**, then `r`, Enter.

Note: OS updates may overwrite `/usr/share/...`; re-check after GNOME upgrades.