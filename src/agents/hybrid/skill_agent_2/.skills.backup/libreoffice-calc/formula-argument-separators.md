---
annotations: []
description: Fix Calc formula errors caused by comma vs semicolon argument separators
  (locale)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 3
name: formula-argument-separators
---

## Symptom
A formula looks correct but Calc shows a syntax/argument error (often after copy/paste from another locale). The issue may be the **function argument separator**.

## Quick fix (most common)
- If you used commas: `=SUMIF(range,criteria,sum_range)` → try semicolons: `=SUMIF(range;criteria;sum_range)`
- Or the reverse (copy/pasted formulas from another locale).

Example (semicolon locale):
- `=LEFT(A2;FIND(" ";A2)-1)`

## How to confirm which separator your Calc expects
- **Insert > Function…** and look at the function signature shown in the wizard (it displays the correct separator).
- If you type/edit in the **Formula Bar**, watch whether Calc accepts the separator you’re using; if a comma version errors, switch to semicolons.

## Where to check/change the separator
1. **Tools > Options…**
2. **LibreOffice Calc > Formula**
3. In **Separators**, check **Function** (this is the argument separator used inside functions).