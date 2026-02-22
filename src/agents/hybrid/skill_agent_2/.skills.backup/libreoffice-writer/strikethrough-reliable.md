---
annotations: []
description: Apply strikethrough reliably in Writer when toolbar/shortcut toggles
  don’t work
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: strikethrough-reliable
---

## Reliable strikethrough (menu path)
1. Select the exact text.
   - Whole paragraph: click in it, then **Ctrl+Shift+Down** (repeat to extend).
   - Arbitrary range: drag-select or **Shift+Arrow**.
2. Apply: **Format ▸ Text ▸ Strikethrough**.
3. Click elsewhere (or press an arrow key) to clear the selection and confirm it stuck.

## Common pitfall
- If nothing is selected, the toolbar button/shortcut can toggle strikethrough for *future typing* instead of the intended text. Reselect the text/paragraph and use the menu path above.

## If you need a specific strike style
- Use **Format ▸ Character… ▸ Font Effects** and pick the desired **Strikethrough** type (Single/Double/etc.).