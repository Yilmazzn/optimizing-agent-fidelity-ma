---
annotations: []
description: 'LibreOffice sidebar numeric fields: Enter commits, Esc cancels (Position/Size
  etc.)'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: commit-sidebar-numeric-fields
---

## When a typed value “doesn’t apply” in a sidebar/inspector field
Common in **LibreOffice Impress/Draw** (and can also occur when editing object properties in other LibreOffice apps): numeric inputs like **Position and Size** (X/Y/Width/Height) often require an explicit commit.

1. Click into the numeric field.
2. (Optional) Press **Ctrl+A** to replace the whole value.
3. Type the new number.
4. **Commit** the edit:
   - Press **Enter**, or
   - Click outside the field / move focus.
5. Avoid **Esc** unless you intend to **cancel/abandon** the edit (it reverts the field to the previous value).