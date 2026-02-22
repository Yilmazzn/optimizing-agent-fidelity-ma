---
annotations: []
description: Apply Impress character formatting reliably (font color/strikethrough/underline;
  incl. tables)
metrics:
  negative_impact: 2
  neutral_impact: 0
  positive_impact: 0
  times_followed: 1.0
  times_requested: 2
name: change-text-color-sidebar
---

## Prerequisite: ensure you’re editing text (not the shape)
- **Double‑click** the text box or press **F2** and confirm the **caret** is visible.
- Select the intended range (while editing: **Ctrl+A** selects text *within that text box*).

## Case 1: Quick font color/underline/strike (may be flaky)
1. Enter text-edit mode (**F2**) and select text.
2. Use either:
   - **Sidebar**: **View ▸ Sidebar ▸ Properties ▸ Character** (e.g., **Font Color**), or
   - The **top Formatting toolbar** character controls (location varies by UI/layout).
3. If it “does nothing”, re-enter text edit mode (**F2**), reselect text, and try again.

## Case 2: Most reliable path (works when Sidebar/toolbar doesn’t)
1. Enter text-edit mode (**F2**) and select text.
2. Go to **Format ▸ Character…**.
3. Open **Font Effects**.
4. Set what you need:
   - **Font color**
   - **Text Decoration ▸ Strikethrough** (e.g., *Single*)
   - (Other decorations like underline are also here)
5. Click **OK**.

## Case 3: Apply formatting to all text in an Impress table (avoid per-cell changes)
1. Click the **table border** to select the table object.
2. If the caret is inside a cell, press **Esc** to exit cell edit mode.
3. Select all cells: **Table ▸ Select ▸ Table** (or **Right‑click ▸ Select ▸ Table**).
4. Apply formatting using **Case 1** (quick) or **Case 2** (reliable).

Tip: If shortcuts/control changes seem to apply to the *table object* instead of the text, you’re not in the “all cells selected” state—re-run **Table ▸ Select ▸ Table**.