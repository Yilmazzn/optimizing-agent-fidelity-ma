---
description: Skills for using Google Chrome settings, privacy, and browsing tools
  effectively.
name: chrome
---

## [bulk-clearing-browsing-data-and-site-data] Bulk Clearing Browsing Data and Site Data

### 🎯 When is this relevant?
Relevant when you need to remove cookies, cache, history, or site data for privacy/troubleshooting and want to avoid deleting many domains one-by-one.

### 📖 Guide
- Prefer **bulk-clear** paths when you see many related tracker/embedded-site entries.
- If a Settings page is awkward to navigate (layout/scrolling/search not finding anything), jump to the most specific **`chrome://settings/...`** URL instead of repeatedly scrolling.

**Option A: Clear browsing data (broad reset)**
1. Open **Settings → Privacy and security → Delete browsing data** (or go to `chrome://settings/clearBrowserData`).
2. Pick a **Time range** (e.g., **All time**).
3. Select what to remove:
   - **Cookies and other site data** (signs you out of many sites)
   - **Cached images and files**
   - **Browsing history** (if requested)
4. Click **Delete data**.

**Option B: Remove site data via “all site data” list (targeted bulk removal)**
1. Go to **Settings → Privacy and security → Third-party cookies → See all site data and permissions**.
   - Direct URL (often faster): `chrome://settings/content/all`
2. Use the **search** box to find a site/keyword (e.g., a brand domain) and use **Remove all shown** / trash icons to delete matching entries.
   - If Settings search says **No results**, retry with **1–2 keywords** (e.g., `cookies`, `site data`, `on close`) rather than full sentences.

**Option C: Clear only the current site (quick, narrow)**
- Click the **site controls** icon near the address bar (lock/tune icon) → **Cookies and site data** / **Site settings** → **Clear data**.

**Option D: Auto-delete site data/cookies when Chrome closes ("delete on close")**
1. Open `chrome://settings/content/siteData`.
2. Enable the option to **delete on-device site data when you close all windows**.
3. Fully close Chrome (all windows) and reopen to confirm behavior.

**Notes / pitfalls**
- Clearing cookies/site data may log you out and reset preferences.
- Be explicit about scope: **“delete on close” applies to site data/cookies**; Chrome does **not** natively auto-delete full history/cache on exit via this toggle.
- If the goal is privacy hardening (not just cleanup), consider also:
  - **Block third-party cookies**
  - Toggle off **related-site activity sharing** (if present)
  - Enable **Send a “Do Not Track” request** and confirm prompts when shown.

### 📝 Field Notes
- 2026-01-25T15:48:38.057873+00:00: 'If the user’s issue is **a specific site opening every time Chrome launches**, clearing cookies/cache usually won’t help. Prioritize checking **On start-up** (`chrome://settings/onStartup`), **Appearance/Home button**, **extensions** (`chrome://extensions`), and (on Windows) the **Chrome shortcut Target** for an appended URL.'

---

## [create-a-desktop-shortcut-for-the-current-website] Create a Desktop Shortcut for the Current Website

### 🎯 When is this relevant?
Relevant when the user wants a clickable desktop/app launcher for a specific website (e.g., creating a shortcut icon for the current tab).

### 📖 Guide
1. Open the Chrome **⋮ (three-dot) menu**.
2. Look for **Create shortcut…** (menu placement varies by Chrome version):
   - Common path in newer UIs: **Save and share → Create shortcut…**
   - Common path in older UIs: **More tools → Create shortcut…**
   - If you don’t see it under the expected group, back out and check adjacent groups before going deeper into submenus.
3. In the dialog:
   - Enter/confirm the shortcut name.
   - If available and desired, enable **Open as window** (creates a more app-like experience).
   - Click **Create**.

**Verify the shortcut was created (when the icon/file isn’t immediately visible)**
- Check the destination location:
  - On many Linux desktops this may create a `.desktop` file on `~/Desktop`.
  - On Windows/macOS it creates a desktop shortcut entry (appearance may be delayed until the desktop refreshes).
- Quick Linux check via terminal:
  ```bash
  ls -la ~/Desktop
  ```
  Look for a newly created `.desktop` (or similarly named) file.

### 📝 Field Notes
<none>

---

## [use-bookmark-manager-to-edit-bookmarks-bar] Use Bookmark Manager to Edit Bookmarks Bar

### 🎯 When is this relevant?
Relevant when you need to create or organize bookmark folders/items (especially under the Bookmarks bar) and the bar is hidden, empty, or hard to use from the current page.

### 📖 Guide
- Prefer **Bookmark Manager** for a deterministic workflow instead of relying on whether the Bookmarks bar is visible.

**Open Bookmark Manager**
- Press **Ctrl+Shift+O** (Windows/Linux), or open `chrome://bookmarks/`.

**Create a folder under the Bookmarks bar**
1. In the left sidebar, select **Bookmarks bar** (this sets the target container).
2. Create the folder:
   - Click the **⋮ (More)** menu (top right) → **Add new folder**, or
   - Right-click in the main list area → **Add new folder**.
3. Enter the folder name and **Save**.
4. Verify the folder appears under **Bookmarks bar** in the manager list.

**Notes / quick checks**
- To show/hide the bar in the main UI: **Ctrl+Shift+B** (Windows/Linux). After toggling, **confirm the bar is visible** before trying to drag/drop items.
- If you don’t see the left sidebar in Bookmark Manager, expand the window or look for the sidebar/navigation toggle.

### 📝 Field Notes
<none>

---

## [manage-experimental-features-in-chromeflags] Manage experimental features in chrome://flags

### 🎯 When is this relevant?
Relevant when the user needs to enable/disable Chrome experimental features (flags), such as UI refresh options, and relaunch Chrome to apply changes.

### 📖 Guide
- In the address bar, open `chrome://flags` and press **Enter**.
- Use the **Search flags** box to find the feature by keyword (e.g., type `refresh` or `2023`).
- For each matching flag, open its dropdown and choose **Enabled**, **Disabled**, or **Default**.
- Click **Relaunch** (bottom of the page) to restart Chrome and apply changes.

**Safety / recovery**
- Flags can cause instability. If Chrome behaves oddly after changes, return to `chrome://flags` and click **Reset all** (top of page), then **Relaunch**.
- If a flag name isn’t present, try alternative keywords; flag names can change between Chrome versions.

### 📝 Field Notes
- 2026-01-25T15:14:56.850803+00:00: 'If troubleshooting unexpectedly dark/inverted website colors, search flags for **force dark** (e.g., “Force/Auto Dark Mode for Web Contents”, often `#enable-force-dark`), set it to **Default/Disabled**, then **Relaunch**.'

---

## [adjust-default-font-size-and-minimum-font-size] Adjust default font size (and minimum font size)

### 🎯 When is this relevant?
Relevant when the user wants Chrome’s default text to appear larger/smaller across websites (accessibility), rather than zooming a single page.

### 📖 Guide
**Fast path (direct URL)**
1. Focus the address bar: **Ctrl+L**.
2. Go to: `chrome://settings/fonts`.
3. Adjust:
   - **Font size**: drag the slider (e.g., to the far right for **Huge**).
   - **Minimum font size** (optional): set a floor so small text can’t render below a certain size.

**Menu path (if direct URL is blocked)**
1. Open **⋮ → Settings**.
2. Use the **Search settings** box and search for **font**.
3. Open **Customize fonts** / **Font size** settings and adjust **Font size** (and **Minimum font size** if present).

**Notes / pitfalls**
- **Font size** changes default font rendering; some sites may still control sizing via their CSS.
- If the request is to enlarge *everything* on a specific site (images/layout too), use **page zoom** instead (Ctrl+Plus/Ctrl+Minus) or manage per-site zoom at `chrome://settings/content/zoomLevels`.

### 📝 Field Notes
<none>

---

## [chrome-ui-language-on-linux] Chrome UI language on Linux

### 🎯 When is this relevant?
Relevant when a user wants Chrome’s menus/UI in a specific language (or when the “Display Google Chrome in this language” option is missing in Language settings).

### 📖 Guide
1. Open Chrome Language settings:
   - Type `chrome://settings/languages` in the address bar and press **Enter**.

2. Distinguish the two common language controls:
   - **Preferred languages** mainly affects **translation prompts** and **spell check**.
   - **Chrome UI language** (menus/buttons) can be switchable **only on some platforms/builds**.

3. Check whether an in-app UI language switch is supported:
   - Next to the target language, open the language’s **⋮** menu.
   - If you see **“Display Google Chrome in this language”**:
     - Enable it, then click **Relaunch** when prompted.
   - If the menu only shows options like **Move to top / Remove** (common on **Linux**):
     - Assume Chrome UI language is controlled by the **system locale**, not by this page.

4. If the goal is Chrome UI language on Linux, use one of these approaches:
   - **System-wide (most reliable):** Change the OS language/region locale (GNOME: **Settings → Region & Language**), then **log out/in** (or reboot) and relaunch Chrome.
   - **Per-app (advanced, if changing OS language is undesired):** Launch Chrome with a locale override (command varies by install), for example:
     ```bash
     LANG=ko_KR.UTF-8 google-chrome-stable
     ```
     If it works, make it persistent by creating/editing a desktop launcher that sets `LANG` for Chrome.

5. If an OS language change triggers downloads/installs (language packs):
   - Open **Details/Progress** early in the installer/apply-changes dialog to confirm it’s actively downloading.
   - Tell the user it may take several minutes; avoid repeated blind waiting if a progress view is available.

**Quick verification**
- Fully restart Chrome (close all windows) and reopen.
- Confirm the UI language changed (e.g., Settings page labels).

### 📝 Field Notes
<none>

---

## [chrome-password-manager-find-saved-passwords] Chrome Password Manager: find saved passwords

### 🎯 When is this relevant?
Relevant when you need to view, search, or manage saved usernames/passwords in Chrome (Google Password Manager).

### 📖 Guide
**Fast path (direct URL)**
1. Focus the address bar: **Ctrl+L**.
2. Open one of these (Chrome version varies):
   - `chrome://password-manager/passwords` (often the most direct)
   - `chrome://settings/passwords` (older Settings-based page)
3. Press **Enter** and wait for the Password Manager page to load.

**Menu path (if you prefer UI navigation)**
- Go to **⋮ → Passwords and autofill → Google Password Manager** (wording/placement varies), then open **Passwords**.

**Search for a specific site/account**
1. Click the **Search passwords** (or **Search**) field.
2. Type a keyword such as the domain or site name (e.g., `etsy`).
3. Select the matching entry to view details (site, username, notes).

**Security / safety notes**
- Do **not** reveal or copy password values unless the user explicitly requests it.
- Revealing/copying a password may require OS authentication (PIN/password/biometric). If prompted, pause and ask the user to complete the verification.
- If the internal page redirects to a web UI, you may be taken to `https://passwords.google.com/` (Google Password Manager). The same search-and-select workflow applies.

### 📝 Field Notes
<none>

---

## [load-an-unpacked-extension-developer-mode] Load an unpacked extension (Developer mode)

### 🎯 When is this relevant?
Relevant when you need to install/test a local Chrome extension from a folder on disk (unpacked), such as during development or when the user has a downloaded extension directory.

### 📖 Guide
1. Open `chrome://extensions`.
2. Turn on **Developer mode** (toggle in the top-right).
3. Click **Load unpacked**.
4. In the file picker, select the **extension’s folder** (the directory that directly contains `manifest.json`) and click **Select/Open**.

**Efficiency tip**
- If the extension folder already exists on disk, go straight to **Load unpacked**. Only inspect `manifest.json` (or the folder layout) **if Chrome shows an error**.

**Common pitfalls / quick diagnostics (when load fails)**
- You selected the wrong level of folder: Chrome needs the folder that directly contains `manifest.json` (not a parent folder, and not the `manifest.json` file itself).
- If Chrome reports manifest errors, open `manifest.json` and verify:
  - It is valid JSON.
  - `manifest_version` is supported (MV3 is current; MV2 is deprecated/blocked in many builds).
  - Required fields like `name` and `version` exist.
- If the extension loads but behaves oddly, use **Errors** / **service worker** links on the extension card in `chrome://extensions` to view logs.

### 📝 Field Notes
<none>

---

## [turn-off-dark-mode-in-chrome-appearance-mode] Turn off dark mode in Chrome (Appearance Mode)

### 🎯 When is this relevant?
Relevant when Chrome is using a dark theme (often because Mode is set to “Device”) and the user wants Chrome’s UI to stay light regardless of the OS theme.

### 📖 Guide
**Use Chrome’s Appearance setting (preferred)**
1. Open **⋮ → Settings**.
2. Open **Appearance**.
3. Find **Mode** and change it to **Light** (instead of **Device** or **Dark**).
4. Close the Settings tab (restart Chrome only if the change doesn’t apply immediately).

**Fast path (direct URL)**
- Open `chrome://settings/appearance` and set **Mode → Light**.

**If pages are still being forced dark (UI is light but websites look inverted/dark)**
- Check `chrome://flags` for **“Force/Auto Dark Mode for Web Contents”** (often `enable-force-dark`). Set it to **Default** or **Disabled**, then click **Relaunch**.
- Also check for extensions that modify colors (e.g., dark-mode readers) and disable them temporarily to test.

### 📝 Field Notes
<none>

---

## [fix-website-settings-not-saving-cookies] Fix Website Settings Not Saving (Cookies)

### 🎯 When is this relevant?
Relevant when a website’s preference changes don’t persist (or the site warns that cookies are disabled/blocked), and you need a fast, reliable way to diagnose feature removal vs cookie/storage permissions vs verification gaps.

### 📖 Guide
1. **Confirm the setting/feature still exists (avoid deep thrash when UIs change)**
   - Look for the control in the current UI.
   - Use **Ctrl+F** for likely keywords.
   - If the control is absent after reasonable search, assume it may be **removed/limited/rollout-dependent** and pivot to supported alternatives (or report infeasibility).

2. **Check persistence prerequisites early (cookies/site data allowed)**
   - On the site, click the **site controls** icon near the address bar (lock/tune) → **Cookies and site data** / **Site settings**.
   - Ensure the site is not set to **Block cookies**.
   - Open `chrome://settings/cookies` (or Settings → Privacy and security → Third-party cookies) and verify:
     - **Cookies are allowed** (not globally blocked).
     - Any relevant **site exception** is set to **Allow**.
     - If the site relies on cross-site sign-in/embeds, test with **third-party cookies allowed** (temporarily) or add an exception.

3. **Reset only the affected site (if behavior is inconsistent)**
   - Go to `chrome://settings/content/all` → search the domain → remove site data.
   - Reload the site, re-accept consent prompts if shown, then retry saving the preference.

4. **Verify success with an observable behavior (don’t end on an unverified settings page)**
   - Refresh/reopen the settings page and confirm the value persists.
   - Validate via **behavioral evidence** (changed default, layout, pagination size, etc.).
   - For paginated results, a quick check is to click **Next** and confirm the page offset/URL reflects the expected page size (rather than relying only on visuals).

5. **If still failing, capture the reason and stop**
   - Record whether the blocker is **feature not present**, **cookies blocked**, **signed-out state**, or **no observable effect**.
   - Report what you tried and what evidence indicates it did/did not persist.

### 📝 Field Notes
<none>

---

## [verify-url-to-pick-correct-search-result] Verify URL to pick correct search result

### 🎯 When is this relevant?
Relevant when navigating from search results or help centers where multiple pages have similar titles and it’s easy to land on the wrong article (or get redirected).

### 📖 Guide
- After clicking a search result, **confirm you’re on the intended page before reading/acting**:
  - Glance at the **address bar URL** (domain + path/slug). If the slug/topic doesn’t match, treat it as the wrong destination.
  - Use **Back** once (Alt+Left on Windows/Linux) to return to results and **choose deliberately** (don’t repeatedly re-click the same ambiguous result).

- To reduce mis-clicks when results look similar:
  - **Hover** a result to preview its URL in the status bar (or right-click → copy link address) before opening.
  - Open the top candidates in **new tabs** (Ctrl+Click), then keep the one whose URL/title matches.

- If you suspect a legacy URL is redirecting:
  - After navigation (or manual URL entry), watch for the **final URL** changing. If it consistently ends at the same destination, assume that destination is the **canonical/updated page**.
  - Avoid thrashing between Back and re-clicks when the redirect is consistent; proceed using the canonical page (and note that older “FAQ” slugs may map to “Information” pages).

### 📝 Field Notes
<none>

---

## [stop-an-unwanted-website-opening-on-chrome-startup] Stop an unwanted website opening on Chrome startup

### 🎯 When is this relevant?
Relevant when Chrome keeps opening a specific website on launch (e.g., after adware, a mis-set startup page, or a modified shortcut), and you need a systematic checklist to remove it.

### 📖 Guide
**1) Fix the “On start-up” setting (most common)**
- Open `chrome://settings/onStartup`.
- Select **Open the New Tab page** (or **Continue where you left off**).
- If **Open a specific page or set of pages** is selected, **remove** the unwanted URL(s) from the list.

**2) Restart Chrome the right way (to verify)**
- Close **all** Chrome windows (on Windows, confirm it’s fully exited; if unsure, use Task Manager to end Chrome).
- Reopen Chrome and confirm the unwanted site no longer appears.

**3) Check Home button / Homepage-related settings (can look like a “startup” issue)**
- Open `chrome://settings/appearance`.
- If **Show Home button** is on, confirm its setting is **New Tab page** or a desired URL (not the unwanted site).

**4) Disable suspicious extensions**
- Open `chrome://extensions`.
- Toggle off (or Remove) anything unfamiliar, “new tab”, “search”, “coupon”, or recently installed.
- Restart Chrome and re-test.

**5) Windows/Surface Pro: confirm the Chrome shortcut Target wasn’t hijacked**
- Right-click the Chrome icon you use to launch Chrome (Desktop/Start/Taskbar).
- Open **Properties** → find **Target**.
- The Target should end with `chrome.exe` and **not** have a URL after it.
  - Bad: `...\chrome.exe https://example.com`
  - Good: `"C:\Program Files\Google\Chrome\Application\chrome.exe"`
- If you fix a pinned Taskbar shortcut, **unpin and re-pin** Chrome to ensure the corrected shortcut is used.

**6) Sync / policies (if settings “come back”)**
- If you’re signed into Chrome, Sync can restore startup settings across devices. Consider temporarily turning off Sync while testing: **Settings → You and Google → Sync and Google services**.
- Check `chrome://policy`. If Chrome is “Managed by your organization” or policies force startup pages, the user may need an administrator to change them.

**7) Last resort: reset Chrome settings**
- Open `chrome://settings/reset` → **Restore settings to their original defaults**.
- Use this when the unwanted behavior persists after startup + shortcut + extensions checks.

### 📝 Field Notes
<none>

---

## [select-from-dropdown-reliably] Select from dropdown reliably

### 🎯 When is this relevant?
Relevant when filling a website field that uses an autocomplete/dropdown (airports/cities, addresses, products, filters) where you must pick a suggestion, and typing into the visible field/placeholder doesn’t register until the picker is actively open.

### 📖 Guide
- First ensure you are typing into the widget’s **active input** (not a static placeholder/label):
  1. Click the field (or its dropdown trigger) until you see a text caret and/or a suggestion list.
  2. Type 2–4 characters and confirm the suggestions/filtering updates.
  3. If typing has no effect, click outside to close, reopen the picker, and try again.

- Prefer deterministic selection methods:
  - Keyboard: type a few characters to narrow matches, use **↓/↑** to highlight the desired option, then **Enter**.
  - Mouse: click the option’s **main text/full row** (largest hit target), not a small sub-element (icon, secondary label).

If the choice doesn’t “stick” (menu stays open, old value remains)
1. Select the same option again, directly on its text/full row.
2. Verify success before proceeding:
   - The dropdown/menu closes, and
   - The control label/field value updates.
3. If still failing, click outside to close the menu, reopen it, then select via **↓/↑** + **Enter**.

If the field shows a validation error (e.g., “Please enter a valid …”) after typing
1. Click the field, press **Ctrl+A**, then type only the minimum characters needed.
2. Pick a suggestion via **↓/↑** + **Enter** (or click the suggestion).
3. Press **Tab** (or click another field) to blur the input and confirm the error is gone.

If an autocomplete dropdown shows no matches
1. Press **Ctrl+A** and retype using an ASCII spelling (remove diacritics) or a shorter fragment.
2. Use **↓/↑** + **Enter** to pick the exact suggestion.

### 📝 Field Notes
<none>

---

## [conditional-waits-for-page-loads] Conditional waits for page loads

### 🎯 When is this relevant?
Relevant when you submit a form or start a search and must wait for a new page/state (results list, confirmation, etc.) to finish loading before continuing.

### 📖 Guide
- Avoid a single long fixed wait (e.g., “sleep 10s”). It can be **too long on fast loads** and **too short on slow loads**.

Preferred approach: wait for a specific ready signal
1. After clicking **Search/Submit/Apply**, identify 1–2 observable “ready” signals:
   - **URL change** to a results route (address bar differs from the form page).
   - A **results container** appears (list/table/cards) or the **first result row/card** is visible.
   - A **loading spinner/skeleton** disappears.
   - A **filter/sort header** becomes visible (often stable on results pages).
2. Use **short repeated waits** (polling) until the signal is true (or a max timeout is reached).
3. After the signal appears, do a quick **stability check** (optional): scroll a little or open a filter to confirm the page is responsive.

Fallback when the expected UI change doesn’t happen
1. Do a quick state check instead of waiting: did a panel open, did a chip appear, did the URL change, did the button show an active/pressed state?
2. If nothing changed, immediately try an alternate interaction:
   - Click the **text label / larger hit target** (not a tiny icon).
   - Scroll a bit to ensure the control is in view, then click again.
   - Dismiss blockers: press **Esc** and close any overlays/popups that may be intercepting clicks.
3. If repeated attempts show no visible progress, pivot (use another navigation path, refresh/back, or change query) instead of stacking longer waits.

Fallback when no clear signal exists
- Use progressive backoff (e.g., a few 0.5–1s waits, then 2s). After each wait, re-check for:
  - an error banner (e.g., “No results found”, “Try again”),
  - a “loading” indicator still present,
  - or the expected results elements.

Rule of thumb
- Prefer “wait until X is visible/absent” over “wait N seconds”, and cap total wait time with a clear next step (refresh/retry/back/report).

### 📝 Field Notes
<none>

---

## [chrome-settings-search-fallback] Chrome Settings search fallback

### 🎯 When is this relevant?
Relevant when you can’t find a Chrome toggle/option via the Settings search box (or the results are too generic), and you need a reliable fallback to locate the control.

### 📖 Guide
- Treat **Settings search** as a hint, not a source of truth: some toggles won’t appear for obvious keywords, or may be nested under a different category label.

**Reliable fallback workflow**
1. If you know (or can guess) the internal Settings route, try a **direct URL** in the address bar (often fastest):
   - `chrome://settings/privacy`
   - `chrome://settings/security`
   - `chrome://settings/cookies`
   - `chrome://settings/content` and subpages
2. If search results are missing/unclear, open the **most relevant parent category** and drill down:
   - **Settings → Privacy and security** is the usual starting point for tracking/cookies/requests.
   - Open likely subpages (e.g., **Third-party cookies**, **Site settings**, **Security**).
3. Once on the likely page, use **Ctrl+F** (find in page) for 1–2 short keywords (e.g., `track`, `request`, `cookie`, `privacy`) and scan nearby sections.
4. Try **synonyms** and adjacent terms rather than repeating the same query:
   - “Do Not Track” might be indexed under wording like **tracking**, **request**, or **privacy**.
5. Verify you found the correct control by toggling it and watching for a **confirmation dialog** or an immediate state change.

**Example (orientation only; UI wording varies by version)**
- A toggle such as **“Send a ‘Do Not Track’ request…”** may be located under **Privacy and security → Third-party cookies** even if searching for “do not track” doesn’t surface it directly.

### 📝 Field Notes
<none>

---

## [prefer-on-site-navigation-before-external-search] Prefer on-site navigation before external search

### 🎯 When is this relevant?
When you are already on a relevant organization/product site and need a related destination page (appointments, forms, downloads, help), but you are tempted to use an external search engine to find the link.

### 📖 Guide
1. Scan the current page for direct links/buttons that match the goal (e.g., “Book”, “Appointments”, “Schedule”, “Apply”).
2. Use fast on-page discovery before leaving the site:
   - **Ctrl+F** for keywords.
   - Use the site’s header/footer navigation and any built-in site search.
3. Only use external search if:
   - The site has no discoverable path after reasonable scanning, or
   - The site navigation is broken/blocked, or
   - You need a very specific document/page that is hard to locate internally.
4. If you do use external search, validate you landed on the correct official destination:
   - Confirm the domain in the address bar before entering personal information.

### 📝 Field Notes
<none>

---

## [resolve-ambiguous-date-constraints] Resolve ambiguous date constraints

### 🎯 When is this relevant?
When you must choose a date/time on a website but the requirement text is ambiguous (e.g., “first Monday eight months later”) and picking the wrong interpretation would waste navigation or cause rework.

### 📖 Guide
1. Restate the requirement in 1 line and identify the likely anchor date (today vs a provided date).
2. List the 2–3 plausible interpretations:
   - “First <weekday> of the month that is N months after the anchor month.”
   - “First <weekday> on/after the exact date N months after the anchor date.”
3. Compute the candidate date(s) quickly (mentally if simple; otherwise use a quick calendar/date tool in another tab).
4. In the scheduling UI, once you reach the target month, check which candidate dates are selectable/available before proceeding.
5. If multiple interpretations remain plausible, prefer the earliest date that satisfies the literal constraint, and note the assumption.

### 📝 Field Notes
<none>

---

## [navigate-multi-month-date-pickers] Navigate multi-month date pickers

### 🎯 When is this relevant?
When a web calendar/date picker is many months away from the current month and you must use previous/next controls (or similar UI) to reach a target month/year without misclicking or backtracking.

### 📖 Guide
1. Look for a month/year jump control first (click the month/year label; check for month/year dropdowns).
2. If using arrows, after every click:
   - Verify the month/year label changed in the intended direction.
3. If the label changed the wrong way, correct immediately (click the opposite arrow once) and re-verify.
4. Before selecting a day, confirm the month/year label one last time.
5. If the picker closes/resets, reopen it and re-verify the month/year before continuing.

### 📝 Field Notes
<none>

---

## [close-stubborn-popovers-esc-click-outside] Close stubborn popovers (Esc / click outside)

### 🎯 When is this relevant?
Relevant when a website dropdown/panel/modal (passenger selector, date picker, filters) does not close after clicking its visible **Done/Close/X** control, or the click target seems unreliable.

### 📖 Guide
1. Try the universal close key: press **Esc**.
2. If it stays open, click a neutral area **outside** the panel to dismiss it.
3. If the panel should commit a value (passenger count, selected date), verify the underlying field/summary updated.
4. Only then retry the in-panel **Done/Apply** control (aim for the button’s main rectangle, not just the text).
5. If dismissal fails repeatedly, reopen the panel and complete the selection via keyboard where possible (type → **↓/↑** → **Enter**), then **Esc** to close.

### 📝 Field Notes
<none>

---

## [verify-constraints-before-partner-click-through] Verify constraints before partner click-through

### 🎯 When is this relevant?
When you are on an aggregator/marketplace site (travel booking, shopping, tickets) and a listing has an external “View deal/Book” link, but you mainly need to confirm constraints like dates, guest count, price, or cancellation terms.

### 📖 Guide
1. Confirm constraints on the primary site first: selected dates, guest/quantity, filters (refundable, breakfast, etc.), and any **Price details** / **Policies** sections.
2. Only open an external partner link if a required detail is not available on the primary site.
3. If you must open it, use **Ctrl+Click** (new tab) so you can quickly return. Immediately verify the partner page reflects the expected constraints; if it doesn’t, stop and use another source instead of repeatedly trying multiple partners.

### 📝 Field Notes
<none>

---

## [stop-at-captcha-bot-check-pages] Stop at CAPTCHA / bot-check pages

### 🎯 When is this relevant?
When an external site blocks access with a CAPTCHA/bot-check and you need information to complete a browsing task.

### 📖 Guide
1. Do not attempt to solve or bypass CAPTCHAs/bot-checks.
2. Use **Back** (or close the tab) and continue using information available on the current/primary site.
3. If verification is still required, use an alternate source (another partner link, the official site, or a different reputable listing).
4. Report the blocker explicitly: “External site required CAPTCHA, so details could not be independently verified there,” and cite what you could verify on-site (price, dates, guests, etc.).

### 📝 Field Notes
<none>

---

## [efficient-navigation-via-the-address-bar-omnibox] Efficient navigation via the address bar (omnibox)

### 🎯 When is this relevant?
When you need to navigate to a URL or search query and the address bar is already focused/highlighted, or you want the fastest reliable way to start navigation without extra clicks.

### 📖 Guide
1. If the address bar text is already highlighted (caret in the bar, existing URL selected), do not click elsewhere.
2. Type/paste the destination URL (or search terms) and immediately submit with **Enter**.
3. If the address bar is not focused, press **Ctrl+L** to focus/select it, then type/paste and press **Enter**.
4. Verify you landed on the intended domain/page before continuing (especially after redirects).

### 📝 Field Notes
<none>

---

## [use-coarse-filters-with-sorting-numeric] Use coarse filters with sorting (numeric)

### 🎯 When is this relevant?
When a website’s filters only offer broad ranges (price, size, rating) but the task requires a stricter numeric threshold (e.g., “>$60”).

### 📖 Guide
1. Check the available filter options and confirm whether an exact threshold can be set.
2. If not, explicitly choose the closest filter that does not exclude valid items (e.g., select **$50+** when the task is **>$60**).
3. Use **Sort** to reduce scanning work (e.g., **Price: High–Low** when you need items above a minimum).
4. While scanning results, keep the requirement strict: verify each item’s displayed value meets the threshold, and skip out-of-scope items that slipped in.
5. If list-view prices/values aren’t visible, open an item page only when needed to confirm, and stop once you have enough in-scope candidates.

### 📝 Field Notes
<none>

---

## [dismiss-cookielocation-popups-early] Dismiss cookie/location popups early

### 🎯 When is this relevant?
When a website shows cookie consent, location prompts, newsletter modals, or other overlays that block clicks/scrolling while you are trying to use search, sort, or filters.

### 📖 Guide
1. Handle overlays immediately before other interactions (scrolling, filtering, sorting).
2. Prefer the most reliable dismiss action:
   - Click the modal’s **X** / **Close** icon (if present).
   - Click an explicit button such as **Reject**, **Accept**, **No thanks**, or **Continue**.
   - Press **Esc** if it behaves like a modal.
3. If the same prompt reappears after navigation/filtering, dismiss it again before proceeding.
4. Verify the page is interactable (you can scroll; filter panel opens; clicks register).

### 📝 Field Notes
<none>

---

## [verify-active-filters-match-numeric-bounds] Verify active filters match numeric bounds

### 🎯 When is this relevant?
When you set a numeric range filter (e.g., min/max price) on a results page and must ensure BOTH bounds are actually applied before collecting items.

### 📖 Guide
1. Open the filter UI and enter both bounds (min and max). If there is an **Apply/Done** button, click it.
2. Immediately verify the filter is active using an observable indicator (don’t trust the typed fields alone):
   - A filter **chip/badge** shows the full range (e.g., “€25–€60”), or
   - Two chips/badges exist (e.g., “From €25” and “Under €60”), or
   - The results summary reflects the constraint.
3. If only one bound appears (or the indicator disappears after closing the panel): reopen the filter and reapply.
   - Clear the fields first (or use **Reset/Clear**) to avoid partial/stale values.
4. Sanity-check quickly before item collection:
   - Sort **Price: Low→High** to confirm the first few results respect the minimum.
   - Sort **Price: High→Low** to confirm the first few results respect the maximum (if needed).

### 📝 Field Notes
<none>

---

## [refine-query-when-facet-is-missing] Refine query when facet is missing

### 🎯 When is this relevant?
When you need an attribute constraint (e.g., color/finish/material) but the site’s filter facets are hidden, unavailable, or the filter panel won’t open reliably.

### 📖 Guide
1. Timebox facet hunting. If you can’t find/apply the facet quickly, stop digging through menus.
2. Refine the query instead:
   - Add the attribute keyword(s) (e.g., “black”, “matte black”, “black stainless”).
   - Optionally add a negative keyword to reduce obvious mismatches (e.g., “-white”).
3. Submit the refined query (often fastest via **Ctrl+L** → type → **Enter**).
4. Re-apply the most reliable structured filters (price range, sale/availability), then verify a few top results match the attribute before collecting items.

### 📝 Field Notes
<none>

---

## [resolve-currency-mismatch-in-shopping-uis] Resolve currency mismatch in shopping UIs

### 🎯 When is this relevant?
When a task requires prices in a specific currency (or a strict numeric range) but the shopping/search UI displays a different currency due to region/locale settings.

### 📖 Guide
1. Confirm the displayed currency in the results/listing UI.
2. Prefer making the UI match the task:
   - Look for a **Country/Region/Currency/Location** setting (often in a settings menu or page footer) and switch to the required locale/currency.
3. If you cannot switch currency/region:
   - Report prices in the **displayed currency**.
   - If a conversion is required, label it as **approximate**, include the **rate source and date/time**, and keep the original currency alongside the converted value.
4. If the task has a strict numeric range, state clearly whether the range was enforced in the displayed currency or only via approximation.

### 📝 Field Notes
<none>

---

## [find-hidden-facets-in-filter-sidebars] Find hidden facets in filter sidebars

### 🎯 When is this relevant?
Relevant when you are on a shopping/search results page with a long left sidebar of filters and you need a specific facet/value that isn’t immediately visible.

### 📖 Guide
1. Before scrolling far, scan the sidebar for **section headers/accordions** (collapsed categories).
2. Expand the most likely category first (e.g., powertrain/performance for fuel/engine; exterior/interior for color/trim).
3. If many sections are open, **collapse** irrelevant ones to shorten the list.
4. Try **Ctrl+F** and search for the facet label/value (e.g., "fuel", "electric"). If a match is found, jump to it and expand its section if needed.
5. Only then do controlled scrolling:
   - Scroll with the pointer over the sidebar (so you scroll the filter panel, not the results list).
   - Use smaller steps (mouse wheel / **Page Down**) and re-scan headers as you go.
6. If you overshoot, return quickly (drag the scrollbar thumb up, or use **Home/Page Up** where supported), then re-scan headers near the top.

### 📝 Field Notes
<none>