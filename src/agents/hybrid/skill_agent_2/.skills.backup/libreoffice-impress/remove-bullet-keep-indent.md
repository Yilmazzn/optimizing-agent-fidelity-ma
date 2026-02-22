---
annotations: []
description: Remove a bullet/number from one line but keep the same indent in Impress
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: remove-bullet-keep-indent
---

## Remove marker without changing alignment
1. Click into the target paragraph so you only have a **caret** (no multi-line selection). Avoid **Ctrl+A** unless you intend to change the whole text box / multiple paragraphs.
2. Go to **Format > Bullets and Numbering…**
3. Remove the marker:
   - If you see **Type**: set it to **None**, **or**
   - In the **Bullets**/**Numbering** tab, pick the **None** style.
4. In the same dialog, open the **Position** tab and match the list level’s alignment:
   - Adjust **Indent / Width** (left indent) and **Spacing to text** until the text lines up with the other items.
5. If it’s still slightly off, fine-tune with the **top ruler** while the caret is in that paragraph (left-indent + first-line indent markers).

### Pitfalls / when NOT to use quick toggles
- Toolbar/Sidebar **Bullets On/Off** and **Numbering On/Off** (and shortcuts like **F12 / Shift+F12**, depending on your setup) can be hard to control: they may affect *all selected paragraphs*, switch list modes/levels, or change indents.
- If a toggle changed more than intended, immediately use **Edit > Undo** and re-try with only the target line active.