---
annotations: []
description: Split a space-delimited cell into multiple columns using FIND/LEFT/MID/TRIM
  formulas
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: split-space-tokens
---

Use formulas when you need derived columns (without overwriting the original cell).

## 2 tokens ("First Last")
- **First:** `=LEFT(A2;FIND(" ";A2)-1)`
- **Last:** `=TRIM(MID(A2;FIND(" ";A2)+1;LEN(A2)))`

## 3+ tokens ("First Middle Rest...")
- **First token:** `=LEFT(A2;FIND(" ";A2)-1)`
- **Middle token (between 1st and 2nd spaces):**
  `=MID(A2;FIND(" ";A2)+1;FIND(" ";A2;FIND(" ";A2)+1)-FIND(" ";A2)-1)`
- **Remainder after 2nd space (can be multiple tokens):**
  `=TRIM(MID(A2;FIND(" ";A2;FIND(" ";A2)+1)+1;LEN(A2)))`

## If the formula errors on commas/semicolons
Calc’s function argument separator is locale-dependent. If `;` doesn’t work, try `,` (or check **Tools > Options > LibreOffice Calc > Formula > Separators**).