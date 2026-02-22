---
annotations:
- 'Skill not followed [chose_alternative]: Used CLI inspection of ~/.thunderbird/profiles.ini
  and filesystem search instead of opening Thunderbird UI/about:profiles. This was
  faster for a pure file-export task.'
description: Open Thunderbird profile manager (about:profiles) from within the app
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 1
name: thunderbird-about-profiles
---

When you need to manage Thunderbird profiles (create/rename/set default/open folder) without using the startup profile chooser.

1. In Thunderbird, open **Menu ≡** (or the **Help** menu on the menubar).
2. Go to **Help → Troubleshooting Information**.
3. On the **Troubleshooting Information** tab, find the **Profiles** section/row.
4. Click **about:profiles** to open the internal **Profile Management** tab.

Notes:
- This opens Thunderbird’s internal `about:profiles` page inside the running app.
- From there you can typically **open the profile folder**, **set a profile as default**, and **create a new profile** (exact buttons vary by version).