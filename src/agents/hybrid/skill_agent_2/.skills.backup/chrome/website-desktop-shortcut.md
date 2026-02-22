---
annotations: []
description: Create a desktop shortcut/launcher for a website (Create shortcut / open
  as window)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: website-desktop-shortcut
---

## Create a desktop launcher for the current website
1. Open the target website/tab in Chrome.
2. Open the **⋮** (three-dots) menu.
3. Go to **Save and share → Create shortcut…**
   - If you don’t see **Save and share**, look for **More tools → Create shortcut…** (older Chrome UI).
4. Edit the name if needed.
5. (Optional) Enable **Open as window** to launch the site in a standalone app-like window.
6. Click **Create**.

## Linux notes (desktop environments)
- Chrome typically creates a standard `*.desktop` launcher file in `~/Desktop`.
- If the icon appears but won’t launch, right-click it and choose **Allow Launching** / **Mark as Trusted** (GNOME/Ubuntu behavior for desktop files).