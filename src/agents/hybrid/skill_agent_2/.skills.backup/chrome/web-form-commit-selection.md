---
annotations: []
description: Web forms where inputs require commit/confirm (autocomplete, date pickers,
  optional blank steps)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: web-form-commit-selection
---

Some web widgets don’t commit your click/typing until you *confirm* (pick a suggestion, press Enter, or click Done/Apply). If a wizard seems “stuck”, look for an explicit commit action.

## Case 1: Autocomplete/typeahead fields (From/To, city, address)
1. Click the field and clear it (**Ctrl+A → Backspace**).
2. Type and wait for the suggestion dropdown.
3. **Commit** by selecting a suggestion:
   - Click the exact dropdown item, or
   - Press **↓** to highlight → **Enter**.
4. Click elsewhere and verify the committed value remains (some UIs show a “pill/tag”).

If **Enter** submits the form instead of selecting, use **↓ then Enter**, or click the suggestion.

## Case 2: Calendar/date pickers
1. Click the date field to open the calendar.
2. Click the day (for ranges: pick **start** then **end**).
3. Look for a commit control such as **Done**, **Apply**, **OK**, **Set dates** and click it.
4. Verify the date(s) appear in the input before clicking **Search/Submit**.

If the date didn’t stick, reopen the picker—if your selection isn’t highlighted, you likely missed **Done/Apply**.

## Case 3: Optional text field should stay blank, but the step won’t advance
1. Click into the optional field (even if you want it empty).
2. Leave it empty.
3. Use the UI’s **Next/→** control for that field/step, or press **Enter** (sometimes **Tab** works) to *commit the empty value* and advance.

If Enter triggers submit, prefer the on-screen Next/→ control.