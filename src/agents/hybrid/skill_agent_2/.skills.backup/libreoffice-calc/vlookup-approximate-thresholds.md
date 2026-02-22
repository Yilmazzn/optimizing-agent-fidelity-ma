---
annotations: []
description: Map numbers to labels via threshold table (VLOOKUP approximate match)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vlookup-approximate-thresholds
---

Use this when you have a numeric value (score, price, tax bracket) and a separate threshold table mapping ranges -> label.

## Setup the scale/threshold table
1. Put thresholds in the **first column** of the scale table (e.g., 0, 60, 70, 80, 90).
2. **Sort this first column ascending** (required for approximate match).
3. Put the label/grade in the next column.

## Formula (approximate match)
1. In the first row to grade, enter:
   - Locale using semicolons: `=VLOOKUP(A2; $D$2:$E$7; 2; TRUE)`
   - Locale using commas: `=VLOOKUP(A2, $D$2:$E$7, 2, TRUE)`
   Where `A2` is the score cell, and `$D$2:$E$7` is the fixed scale range.
2. Keep the **4th argument TRUE** (approximate match) to return the label for the largest threshold `<=` the score.
3. Fill down (fill handle or `Ctrl+D`).

**Common pitfall:** if thresholds aren't sorted ascending, approximate match can return wrong labels.