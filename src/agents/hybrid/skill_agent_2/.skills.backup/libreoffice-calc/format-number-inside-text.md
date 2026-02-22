---
annotations: []
description: Force fixed number formatting (decimals, separators, zero-padding) via
  TEXT()
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 2
  times_followed: 2.0
  times_requested: 2
name: format-number-inside-text
---

## Case 1: Concatenate a number into text with fixed formatting
Calc may ignore the source cell’s displayed number format when you concatenate a numeric cell into text. Wrap the number with `TEXT()` to force the format.

1. Click the target cell.
2. Enter a formula like:
   ```
   ="The price is " & TEXT(C1; "0.00") & " euros."
   ```
   - If your locale uses comma separators for functions, use:
     ```
     ="The price is " & TEXT(C1, "0.00") & " euros."
     ```
3. Press **Enter**.

### Common format codes
- `"0.00"` → always 2 decimals
- `"0.000"` → always 3 decimals
- `"#,##0.00"` → thousands separator + 2 decimals (subject to locale settings)

## Case 2: Fixed-length IDs with leading zeros (zero padding)
To turn a variable-length numeric ID into a fixed-width text ID (e.g., 7 digits):

``` 
=TEXT(C2; "0000000")
```
(Comma-locale variant: `=TEXT(C2, "0000000")`.)

This returns **text**, so leading zeros won’t be dropped on copy/paste or CSV export.

Tip: If the source ID is stored as text, convert first (e.g., `TEXT(VALUE(A2); "0000000")`).

## Case 3: Build a compound key / ID from multiple cells (force integer digits)
When concatenating computed numbers (e.g., measures that may have decimals), wrap with `INT()` (truncate) or `ROUND()` first, then `TEXT()`.

Example (uses cross-sheet references + an underscore separator):
```
=TEXT(Sheet1.A2;"0") & "_" & TEXT(INT(Sheet1.J2);"0")
```

To populate down a column quickly: enter the formula once, select that cell plus the rows below, then **Ctrl+D** (Fill Down).