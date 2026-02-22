---
annotations: []
description: Open Thunderbird Account Settings reliably and set an identity signature
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: thunderbird-identity-signature
---

When an “Account Settings” link in Thunderbird’s content pane doesn’t respond (or isn’t present), use the app menu path instead.

## Open Account Settings (reliable)
1. Click **Menu ≡** (top-right).
2. Click **Account Settings**.
   - Some versions: **Tools → Account Settings** (menubar).

## Set signature for the correct identity
1. In the left sidebar, pick the target **account**.
2. Select the right **identity** under it (often **Default Identity**).
3. In the right pane, edit **Signature text:** (plain-text; use newlines for multiple lines).
4. Close the Account Settings tab/window — changes apply immediately (no Save button).