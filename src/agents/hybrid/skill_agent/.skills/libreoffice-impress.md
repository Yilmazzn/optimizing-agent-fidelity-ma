---
description: Skills for using LibreOffice Impress (especially Calc) efficiently and
  effectively
name: libreoffice-impress
---

## [safe-sidebar-numeric-edits-impressdraw] Safe sidebar numeric edits (Impress/Draw)

### 🎯 When is this relevant?
Relevant when editing an object’s Position/Size numerically in LibreOffice Impress (or Draw) and you need to avoid changing the wrong object or accidentally typing onto the slide.

### 📖 Guide
- **Confirm the correct object is selected before changing numbers:**
  - Click the object once and look for **selection handles** around it.
  - Check the **Status Bar** (bottom) for the selected object type (e.g., Image/Bitmap/Shape). If the wrong thing is selected, click on an empty area, then re-click the intended object.
  - If multiple objects overlap, use **Tab / Shift+Tab** to cycle selection until the right object is highlighted.

- **Ensure the numeric field has focus before typing:**
  1. In the **Sidebar → Properties → Position and Size**, **click inside** the specific field (X, Y, Width, Height) until you see a text caret.
  2. Press **Ctrl+A** to select the existing value, type the new number, then press **Enter** to commit.

- **Fast recovery when focus/selection was wrong:**
  - If the wrong object changes size/position: press **Ctrl+Z** immediately, then reselect the correct object and retry.
  - If a stray character/text box appears on the slide because focus was on the canvas: press **Esc** to exit text editing, then **Ctrl+Z** to undo the stray insertion.

### 📝 Field Notes
- 2026-01-25T06:02:40.124917+00:00: 'Scope note: this skill is for **numeric Position/Size edits of objects**. For **text styling/formatting** (bold/underline/strikethrough, etc.), use a text-formatting skill (e.g., apply via Sidebar → Properties → Character and verify the toggle state).'

---

## [make-an-image-cover-the-slide-keep-aspect-ratio] Make an image cover the slide (keep aspect ratio)

### 🎯 When is this relevant?
Relevant when you want an image to fill the entire slide like a banner/background while preserving aspect ratio (no stretching).

### 📖 Guide
1. **Get slide dimensions** (so you know the target width/height): use **Slide → Properties…** and note the slide **Width** and **Height**.
2. **Select the image**, then open **Sidebar → Properties → Position and Size**.
3. Enable **Keep ratio** (aspect ratio lock).
4. Pick one dimension to match the slide:
   - Common “cover” method: set **Height = slide height**.
   - (Alternative) Set **Width = slide width** if you prefer filling left/right first.
5. **Align and center with Position X/Y**:
   - Often set **Position Y = 0** to align to the top edge.
   - Center horizontally with **Position X = (slide width − image width) / 2**.
     - If the image becomes wider than the slide, **X will be negative**; that’s OK and simply crops equally on both sides.
6. (Optional) If the image should be behind everything: right‑click the image → **Arrange → Send to Back**.

### 📝 Field Notes
<none>

---

## [text-formatting-toggles-verify-fallback] Text formatting toggles (verify + fallback)

### 🎯 When is this relevant?
Relevant when you need to apply or remove a text formatting toggle (bold/italic/underline/strikethrough) on specific words/lines in Impress and want a reliable method plus quick verification/fallback if a keyboard shortcut doesn’t appear to work.

### 📖 Guide
- **Enter text edit mode**: double‑click the text box (or press **F2**) until you see a caret in the text.
- **Select exactly what should change**:
  - Drag to highlight the words/lines, or use **Shift+Arrow** to extend selection.
  - For bullet lists, ensure only the intended bullet text is highlighted (don’t just select the whole text box unless that’s intended).
- **Apply the formatting** (either route works):
  - **Keyboard shortcut first** (fast): e.g., **Ctrl+B** bold, **Ctrl+I** italic, **Ctrl+U** underline, strikethrough (often **Ctrl+Shift+X**, depending on setup).
  - **Reliable UI toggle (recommended when precision matters):** open **Sidebar → Properties → Character** (or the Formatting toolbar) and click the relevant toggle (e.g., **Strikethrough**).
- **Immediately verify it actually applied**:
  - Look for the visible change on the selected text, **and/or** confirm the **toolbar/sidebar button appears pressed** while the selection is active.
- **If nothing changes** (common causes: wrong focus/selection):
  - Click back into the text, reselect the target text, then use the **Sidebar/toolbar toggle**.
  - If you may not be in text edit mode, press **Esc** to exit, then re‑enter with a double‑click/F2 and retry.
- **Recovery:** if formatting applied to the wrong text, use **Ctrl+Z** and reapply with a more precise selection.

### 📝 Field Notes
<none>