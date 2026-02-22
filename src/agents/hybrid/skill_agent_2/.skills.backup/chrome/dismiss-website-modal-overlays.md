---
annotations: []
description: Dismiss modal overlays blocking clicks in Chrome (web pages, Settings,
  promo bubbles)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 2
name: dismiss-website-modal-overlays
---

## Identify the blocker
- Page looks dimmed/greyed out and clicks/typing don’t reach the underlying content.
- There’s a centered box/overlay on a website **or** a modal dialog on top of `chrome://settings`.
- A **Chrome UI bubble/tooltip** (“Try this feature”, “Make Chrome faster”, etc.) is covering part of the toolbar/page and the tiny **X** is hard to click.

## Case 1: In-page website overlays (cookies/locale/newsletter/promo)
1. In the overlay, click the action that unlocks the site (e.g., **Choose region/language**, **Accept/Reject cookies**, **Continue**).
2. If optional, close via **X / Close / Not now**.
3. Try **Esc** (common for modals).
4. If buttons are off-screen: scroll **inside the dialog** or zoom out (**Ctrl+-**) to reveal bottom actions.

**Pitfalls**
- Don’t keep clicking the underlying page; it won’t work until the overlay is gone and can cause mis-clicks once it closes.
- Some sites stack multiple overlays; clear the **top-most** one first.
- If the blocker is a **Chrome permission chip** near the address bar (location/camera/mic/etc.), handle it via the chip/site controls instead of the page overlay.

## Case 2: Modal dialogs inside `chrome://settings` (e.g., Clear browsing data)
1. Complete the dialog action (or click **Cancel/Close**) before trying to click elsewhere in Settings.
2. Only after the dialog closes, continue navigating Settings sections.

Reopen **Clear browsing data** directly:
- `chrome://settings/clearBrowserData`

## Case 3: Chrome in-product promo bubbles / coachmarks (UI tooltips)
1. Press **Esc**.
2. If it doesn’t dismiss, click an **empty area** of the page (to move focus away) and press **Esc** again.
3. If you can’t click anywhere, try **Tab** a few times, then **Esc**.