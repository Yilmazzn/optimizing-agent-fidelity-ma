---
annotations: []
description: Focus Chrome omnibox (Ctrl+L) to paste a URL or search clipboard text
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 2
  times_followed: 2.0
  times_requested: 2
name: focus-omnibox-before-url
---

When keyboard focus is inside a webpage (search box, form field), typing/pasting won’t affect navigation. Use the omnibox (address bar) instead.

**Shortcuts:**
- **Ctrl+L** (or **Alt+D**) = focus omnibox and select current text (most reliable)
- **Ctrl+K** / **Ctrl+E** = focus omnibox in “search” mode

## Case 1: Navigate to a URL / `chrome://...`
1. Press **Ctrl+L**.
2. Type/paste the URL (e.g., `chrome://settings/search`).
3. Press **Enter**.

## Case 2: Web-search whatever is on your clipboard (no need to click a site search box)
1. Press **Ctrl+L**.
2. Press **Ctrl+V** to paste.
3. Press **Enter** to search (uses your default search engine).

Tip: **Alt+Enter** opens the search/results in a **new tab** (keeps the current page).