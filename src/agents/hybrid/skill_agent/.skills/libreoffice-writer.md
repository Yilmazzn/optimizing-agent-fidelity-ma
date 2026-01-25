---
description: Skills for using LibreOffice Writer to format documents reliably (alignment,
  tabs, styles, and dialogs).
name: libreoffice-writer
---

## [right-aligned-tab-stop-for-one-line-split] Right-aligned tab stop for one-line split

### 🎯 When is this relevant?
Relevant when you need text to start on the left and end on the right on the same line (e.g., title on the left, date or page info aligned to the right) using a right-aligned tab stop in LibreOffice Writer.

### 📖 Guide
1. Click in the target paragraph (or select the paragraph).
2. Open the tab-stop settings:
   - **Format → Paragraph… → Tabs**.
3. Create the right-aligned tab stop:
   - In **Position**, click the field, press **Ctrl+A** (select all), then type the desired position (e.g., `17 cm`).
   - Set **Alignment** to **Right**.
   - Click **New** / **Set** to add it to the list, then click **OK**.
4. Insert the tab at the split point:
   - Put the caret where the left text should end.
   - If there is already a separator space, replace it cleanly so words don’t merge:
     - **Select the single space** and press **Tab**, **or** place the caret **before** the space and press **Delete**, then press **Tab**.
5. Verify: the text after the tab should jump to the right and be right-aligned at the tab position.

**Pitfalls / recovery**
- If you accidentally append into a numeric/unit field and get a value like `0.00 17 cm`, click the field, press **Ctrl+A**, retype, and press **Enter** if needed.
- If you used **Backspace** and briefly merged words, press **Ctrl+Z** and redo using **Delete** or space-selection replacement.

### 📝 Field Notes
<none>