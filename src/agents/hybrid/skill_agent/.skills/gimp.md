---
description: Skills for using GIMP to edit and export images efficiently and safely.
name: gimp
---

## [precise-numeric-entry-in-edit-dialogs] Precise Numeric Entry in Edit Dialogs

### 🎯 When is this relevant?
Relevant when adjusting values in GIMP dialogs that have both sliders and numeric input boxes (e.g., Brightness-Contrast) and you need to avoid accidental large jumps from scrolling or mis-clicks.

### 📖 Guide
- Prefer typing exact values instead of dragging when precision matters.
- Click the **numeric value** box, then press **Ctrl+A** (select all) and type the intended number (e.g., `-20`).
- **Avoid clicking the slider track** (the bar). In many dialogs a click can jump the value to where you clicked. If you must use the slider, drag the **handle/knob** carefully (small movements), or use arrow keys in the numeric field.
- Press **Enter** to commit the value (some dialogs won’t apply typed values until you confirm).
- Avoid hovering a numeric field while scrolling: the mouse wheel can increment/decrement values and cause large unintended changes.
- If you overshoot: use **Ctrl+Z** to undo the last change, or retype the correct value using **Ctrl+A**.
- Before confirming, sanity-check the **preview** (toggle preview on/off if available) to ensure the image isn’t clipped/washed out.

### 📝 Field Notes
<none>

---

## [gimp-shortcut-not-working-focus-and-menu-fallback] GIMP Shortcut Not Working: Focus and Menu Fallback

### 🎯 When is this relevant?
Relevant when a GIMP keyboard shortcut (e.g., opening a filter/dialog) doesn’t do anything or appears to be ignored.

### 📖 Guide
- **First, confirm focus is in the image UI (not a text box):**
  - Click once on the **image canvas** (or the Layers/Toolbox area) to ensure GIMP is the active window.
  - If you might be typing in a numeric/text field, press **Esc** to exit text-entry focus, then try the shortcut again.
- **Don’t wait:** if nothing appears within ~1 second, switch to the menu path.
  - Use the relevant top-menu category (commonly **Colors**, **Filters**, **Image**, **Layer**, **Select**, **Tools**) and pick the command.
- If the dialog opens, proceed using the dialog’s controls (and prefer numeric entry when precision matters).

### 📝 Field Notes
<none>