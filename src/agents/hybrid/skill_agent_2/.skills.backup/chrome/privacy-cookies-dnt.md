---
annotations: []
description: 'Chrome privacy & security settings: site data, cookies, DNT, Safe Browsing'
metrics:
  negative_impact: 0
  neutral_impact: 1
  positive_impact: 2
  times_followed: 2.5
  times_requested: 3
name: privacy-cookies-dnt
---

## Use the “site controls” icon for per-site settings
The icon at the far-left of the address bar (padlock or tune/sliders) is the fastest way to reach **Site settings**, clear **site data**, or change **permissions** for the current site.

## Case 1: A site asks for a permission (location / camera / mic / notifications)
1. Look near the **left of the address bar** for a **permission chip/popup** (sometimes a small icon like a pin/camera).
2. Click it and choose **Allow** or **Block**.
3. If the site UI seems stuck waiting on the decision, **reload** the page.

### If you dismissed it / chose wrong / need to change later
1. Click the **site controls** icon (padlock/sliders).
2. Open **Site settings** (or the specific permission row).
3. Set the permission to **Allow / Block / Ask** → reload.

**Pitfall:** A site can show an **in-page modal** (cookies/promo) *and* a **browser permission prompt**. Dismiss whichever is currently blocking interaction.

## Case 2: Clear cookies + on-device site data for the current site (no global wipe)
1. Open the target site.
2. Click the **site controls** icon.
3. Click **Cookies and site data** → **Manage on-device site data**.
4. Remove entries (trash icon) for each relevant domain/subdomain.
5. Click **Done** → **Reload**.

Tip: Sites often use multiple domains (auth/CDN); clear each relevant entry.

## Case 3: Auto-delete cookies/site data when Chrome closes (global)
1. Open `chrome://settings/content/siteData`.
2. Under **Default behaviour**, select **Delete data sites that have been saved to your device when you close all windows**.
3. Optional: Adjust exceptions/allowlists on the same page (wording varies by version).

Note: This targets cookies/site data; auto-deleting **history/cache** typically isn’t available in standard Chrome UI. If you need history/cache cleared on exit, use an Enterprise policy such as `ClearBrowsingDataOnExitList` (verify at `chrome://policy`).

## Case 4: Block third-party cookies (global)
1. Open `chrome://settings/cookies` (or **⋮ > Settings > Privacy and security > Third-party cookies**).
2. Select **Block third-party cookies** (add site exceptions if something breaks).

## Case 5: Ads privacy toggles (ad topics / site-suggested ads / measurement)
1. Open `chrome://settings/adPrivacy` (or Settings → **Privacy and security > Ads privacy**).
2. Turn **Off**: **Ad topics**, **Site-suggested ads**, **Ad measurement**.

## Case 6: Enable “Do Not Track”
1. Open `chrome://settings/privacy`.
2. Scroll to **Send a "Do Not Track" request**.
3. Toggle it **On** and click **Confirm**.

If Settings search for **do not track** doesn’t jump directly to the toggle, open the closest result (often **Third-party cookies** / **Privacy and security**) and **scroll within that page** to find the DNT toggle.

## Case 7: Turn on Safe Browsing “Enhanced protection”
Use this when you need stronger phishing/malware/unsafe-download warnings.

1. Open: `chrome://settings/security`.
2. Under **Safe Browsing**, select **Enhanced protection**.

Menu path (if you can’t use the direct URL): **⋮ > Settings > Privacy and security > Security > Safe Browsing**.

Note: **Enhanced protection** may share more data with Google than **Standard protection**; choose per policy.