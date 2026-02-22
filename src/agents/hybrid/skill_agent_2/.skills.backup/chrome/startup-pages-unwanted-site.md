---
annotations: []
description: Stop Chrome opening an unwanted site on launch (keeps coming back/locked)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: startup-pages-unwanted-site
---

When Chrome keeps opening a specific site on launch, it’s usually controlled by **Settings → On startup** (not cache).

## Remove an unwanted startup page
1. Focus the address bar (**Ctrl+L** / **Cmd+L**).
2. Open: `chrome://settings/onStartup`.
3. Under **On startup**:
   - If **Open a specific page or set of pages** is selected: find the unwanted URL → click **⋮** → **Remove**.
   - Or switch to **Open the New Tab page**.

## If it reappears or the startup option is missing/locked (extension or policy)
1. **Check extensions:** open `chrome://extensions` → disable/remove suspicious ones (especially things named like **“New Tab”**, **“Search”**, **“Coupon”**, **“Security”**, or anything from an unknown publisher).
2. **Check policies:** open `chrome://policy` (enterprise/"managed" policies can enforce startup pages).
3. **Reset Chrome (last resort):** `chrome://settings/reset` → **Restore settings to their original defaults** (often clears hijacked settings).