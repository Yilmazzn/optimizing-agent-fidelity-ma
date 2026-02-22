---
annotations: []
description: 'Change fonts in Impress: quick per-textbox setting vs global via Styles
  (F11)'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: standardize-fonts-via-styles
---

## Case 1: Change the font for one text box (fast)
1. Enter text edit mode and select the text.
   - Tip: with the caret inside the text box, **Ctrl+A** selects all text *in that box*.
2. Open the Sidebar if needed: **View ▸ Sidebar** → **Properties**.
3. In the text formatting area, click the **Font Name** dropdown.
4. **Type** the font name (e.g., `Microsoft JhengHei`) and press **Enter**.

Note: If **Ctrl+A** selects slide objects instead of text, you weren’t in text edit mode (caret not visible).

## Case 2: Standardize fonts across the whole deck (preferred)
1. Press **F11** to open **Styles**.
2. Check both style families (depending on what your deck uses):
   - **Presentation Styles** (placeholders/layout text: **Title**, **Subtitle**, **Outline 1/2/…**)
   - **Drawing Styles** (manual text boxes/shapes; often **Text** → **A0/A1/A2/A3/A4**)
3. For each relevant style: **right‑click ▸ Modify… ▸ Font** tab.
4. Set **Family** (you can click the field and **type** the font name) → **OK**.

### If some text doesn’t change
- It’s using a **different style** or has **direct formatting**.
- Click into the text (caret visible) and **double‑click** the intended style in Styles to apply it, then re-check the style’s font.