---
annotations: []
description: Force Chrome UI language on Linux without changing desktop locale
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: ui-language-linux-locale
---

When **Settings > Languages** doesn’t show **“Display Google Chrome in this language”** (common on some Linux builds), Chrome’s UI language is usually driven by the **launch locale** and/or `--lang`.

## Force a one-time UI language via launch locale (recommended)
1. Confirm the locale exists:
   - `locale -a | grep -i '^ko_kr\.utf-8$'` (replace with your target locale)
2. If missing, generate/install the locale (Debian/Ubuntu-style):
   - `sudo bash -c "grep -q '^ko_KR.UTF-8 UTF-8' /etc/locale.gen || echo 'ko_KR.UTF-8 UTF-8' >> /etc/locale.gen"`
   - `sudo locale-gen ko_KR.UTF-8`
3. **Quit Chrome fully** (otherwise locale/Preferences changes may not apply):
   - Chrome menu **Exit**; if needed: `pkill -f chrome` / `pkill -f chromium`.
4. Relaunch with the target locale + `--lang` (example: Korean UI):
   - `env LANG=ko_KR.UTF-8 LANGUAGE=ko_KR:ko LC_ALL=ko_KR.UTF-8 google-chrome-stable --lang=ko-KR`
   - If you already use other Chrome flags (e.g., `--remote-debugging-port=...`), **keep them** on the same command after the binary.
5. Verify via **actual UI strings** and/or `chrome://version` (Command Line shows `--lang=…`). Don’t trust the Settings page alone.

## Optional: also set profile language fields (can help, but not sufficient alone)
Only do this **after the locale exists** and with Chrome fully closed (Chrome can overwrite these on shutdown).
1. Backup:
   - `~/.config/google-chrome/Local State`
   - `~/.config/google-chrome/Default/Preferences`
2. Edit `Local State` (JSON): set `intl.app_locale` (e.g. `"ko"`).
3. Edit `Default/Preferences` (JSON): set `intl.accept_languages` (e.g. `"ko,ko-KR,en-US,en"`).
4. Relaunch Chrome again with the locale env vars and/or `--lang=…`.

## Make it persistent (optional)
- Edit the Chrome/Chromium launcher (`.desktop`) and add `--lang=…` to the `Exec=` line, or ensure the desktop session exports the desired `LANG`/`LC_ALL` before launching Chrome.