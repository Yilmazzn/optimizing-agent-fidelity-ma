---
annotations: []
description: 'Hide #N/A or placeholder text via Find All formatting or conditional
  formatting'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: hide-placeholders
---

## Option 1 (one-time): Hide currently visible matches (Find All + batch formatting)
1. Press **Ctrl+F** to open the **Find** bar.
2. Type what you want to hide (e.g., `#N/A`).
3. Open **Find options** and enable **Formatted display** (helps when the cell *displays* an error like `#N/A`).
4. Click **Find All** to select every match.
5. Right‑click any selected cell → **Format Cells…** → **Font Effects** → set **Font color** to match the background (use **Custom Color…** for exact Hex/RGB).

Notes:
- This only affects the cells found *right now*; new `#N/A` values later won’t be hidden.

## Option 2 (future-proof): Automatically hide future #N/A (Conditional Formatting)
Use this when more rows will be added/updated and you want new `#N/A` to stay hidden.

1. Select the whole range/table where `#N/A` may appear.
2. Go to **Format → Conditional → Condition…**
3. Set **Condition** to **Formula is** and enter (use the top-left cell of your selected range):
   - `ISNA(A1)`
   - (If you want to hide *any* error, use `ISERROR(A1)` instead.)
4. Choose/apply a **Cell Style** where the **font color matches the background** (create one if needed in **Styles** sidebar / **F11**).
5. **OK**.

Notes:
- This hides the display but the underlying value/formula remains (you may still see it in the input line/formula bar).
- If your range has multiple background colors (e.g., zebra striping), a single “white text” style may not blend everywhere.