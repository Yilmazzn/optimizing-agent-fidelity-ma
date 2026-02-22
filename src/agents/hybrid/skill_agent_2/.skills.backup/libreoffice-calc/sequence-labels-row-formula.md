---
annotations: []
description: Create sequential IDs/labels with a prefix using ROW() (auto-adjusts
  when rows inserted)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: sequence-labels-row-formula
---

## Prefixed sequence (e.g., "No. 1", "No. 2"…)
1. In the first data row cell (example: B2), enter:
   - `="No. " & (ROW()-1)`
2. Press Enter.
3. Fill down (fill handle, or select the target range and press **Ctrl+D**).

## Avoid hardcoding the header row (safer if moved)
Use the first sequence cell as the anchor:
- In B2: `="No. " & (ROW()-ROW($B$2)+1)`
Fill down.

## Formatting variants
- Start at 0: use `...+0` instead of `+1`.
- Zero-padded numbers: `="No. " & TEXT(ROW()-ROW($B$2)+1; "000")` (e.g., No. 001).