---
annotations: []
description: Paste a Calc cell range into Writer as a formatted table (Paste Special
  → HTML)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: paste-calc-range-as-table
---

## Paste a Calc range as a real Writer table
Use this when plain **Ctrl+V** from Calc gives messy/unpredictable formatting.

1. In **Calc**, select the cell range (include headers if needed) and press **Ctrl+C**.
2. In **Writer**, place the text cursor where the table should be inserted.
3. Press **Ctrl+Shift+V** (**Edit ▸ Paste Special ▸ Paste Special…**).
4. In the format list, choose **HyperText Markup Language (HTML)** (sometimes shown as **HTML Format**), then **OK**.

### Notes / pitfalls
- This inserts a normal **Writer table** in the document body (not an embedded spreadsheet object).
- If you need different behavior (e.g., linked/embedded spreadsheet), pick a different Paste Special format instead of HTML.