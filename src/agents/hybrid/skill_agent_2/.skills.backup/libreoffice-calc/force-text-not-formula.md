---
annotations: []
description: When Calc treats a header as a formula / opens Function Wizard, force
  plain-text entry
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 3
name: force-text-not-formula
---

## Cancel the interruption
- If **Function Wizard** pops up unexpectedly, press **Esc** or click **Cancel** to return to the sheet.

## Force plain text (headers/labels)
1. Click the target cell.
2. Type an apostrophe **'** first, then your text (e.g., **'CA changes**) and press **Enter**.
   - The apostrophe is not displayed in the cell; it only forces *text*.

## Fix a cell that became a formula by accident
1. Select the cell.
2. Type the intended label **without a leading '='** and press **Enter** (this overwrites the formula).

Tip: If you keep triggering formula entry, double-check the first character you typed—an accidental **=** will switch Calc into formula mode.