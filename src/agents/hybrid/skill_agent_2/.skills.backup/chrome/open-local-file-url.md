---
annotations: []
description: Open a local file in Chrome by typing a file:// URL (file:///path/to/file)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: open-local-file-url
---

## Open a local file via the omnibox (faster than File > Open)
1. Press **Ctrl+L** (or **Alt+D**) to focus the address bar.
2. Type or paste a `file:///...` URL to the local file.
   - Linux example: `file:///home/user/Desktop/report.html`
   - Windows example: `file:///C:/Users/User/Desktop/report.html`
3. Press **Enter**.

Notes:
- If you paste a normal filesystem path, add the `file:///` prefix (Chrome will URL-encode spaces as needed).
- Alternative: **Ctrl+O** opens the file picker, but typing/pasting the URL is often faster/more deterministic.