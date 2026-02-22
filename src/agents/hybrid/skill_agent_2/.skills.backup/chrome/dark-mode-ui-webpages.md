---
annotations: []
description: 'Fix Chrome dark mode: UI theme setting vs auto-darkened web pages'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: dark-mode-ui-webpages
---

## Set Chrome UI theme (toolbars/menus)
1. Open `chrome://settings/appearance` (or **⋮ > Settings > Appearance**).
2. Under **Mode** (or **Theme**), pick **Device**, **Light**, or **Dark**.

## If web pages are dark but Chrome UI is light
This is usually **Auto Dark Mode for Web Contents** (a flag) or a dark-mode extension.
1. Check `chrome://extensions` for dark-mode extensions (e.g., Dark Reader) and disable to test.
2. Open `chrome://flags/#enable-force-dark`.
3. Set **Auto Dark Mode for Web Contents** to **Disabled**.
4. Click **Relaunch**.