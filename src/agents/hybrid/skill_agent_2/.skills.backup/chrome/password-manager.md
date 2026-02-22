---
annotations: []
description: Open and search Chrome Password Manager (chrome://password-manager)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: password-manager
---

## Go directly to saved passwords
1. Focus the address bar (**Ctrl+L** / **Cmd+L**).
2. Open: `chrome://password-manager/passwords` and press **Enter**.
   - If this URL doesn’t work in your build, try `chrome://password-manager/` and open **Passwords** (or **Settings > Autofill and passwords > Google Password Manager**).

## Find a specific login fast
1. Don’t scroll through the list—click the **Search passwords** field at the top.
2. Type the site name or username to filter.

## UI pitfalls
- If an info/promo card (e.g., **“Get here quicker”**) obscures the list, click the card’s **X** (top-right) to dismiss.

## Notes / safety
- Viewing/copying a password typically requires OS authentication (PIN/biometrics/password).
- If you only need to confirm an entry exists, stop after locating it (avoid clicking **View password** / eye icons unless required).