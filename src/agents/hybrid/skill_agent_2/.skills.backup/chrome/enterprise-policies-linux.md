---
annotations: []
description: Set Chrome enterprise policies via JSON on Linux (verify in chrome://policy)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: enterprise-policies-linux
---

## Install/apply a policy via JSON (Linux)
1. **Choose folder** (system-wide):
   - **Managed (enforced)**: `/etc/opt/chrome/policies/managed/`
   - **Recommended (user can override)**: `/etc/opt/chrome/policies/recommended/`
   - (If using **Chromium**: typically `/etc/chromium/policies/{managed,recommended}/`.)
2. Create the directory if needed, then create any `*.json` file in it (root permissions required).
3. **Restart Chrome fully** (close all windows; for reliability disable background mode at `chrome://settings/system` → turn off **Continue running background apps when Google Chrome is closed**).
4. Verify: open `chrome://policy` → **Reload policies** (if shown) → confirm the policy appears and is **Status: OK**.

## Example: clear multiple browsing data types on exit
Create (as root): `/etc/opt/chrome/policies/managed/clear_browsing_data_on_exit.json`
```json
{
  "ClearBrowsingDataOnExitList": [
    "browsing_history",
    "download_history",
    "cookies_and_other_site_data",
    "cached_images_and_files"
  ]
}
```
Notes:
- This is often the only reliable way to auto-clear **history/cache** on exit; the standard Settings UI mainly supports auto-deleting **cookies/site data**.
- The list entries must match Chrome’s policy spec for `ClearBrowsingDataOnExitList`.