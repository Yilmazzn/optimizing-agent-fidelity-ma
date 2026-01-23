---
description: Use when you must jump to a specific cell/range in LibreOffice Calc (e.g.,
  type into B12) and avoid mis-typing due to ambiguous focus. Covers Name Box / Go
  To (Ctrl+G/F5) navigation, focus verification, and recovery when a range like A1:C1
  is selected instead of the target cell.
last_updated: '2026-01-23 01:03:16'
name: libreoffice-calc-go-to-cell

---
# LibreOffice Calc: reliably jump to a cell and enter text

## When to use
- You need to enter/edit a value in an exact cell (e.g., **B12**) and don’t want focus errors.
- The UI shows an unexpected multi-cell selection (e.g., **A1:C1**) after trying to navigate.

## Preferred workflow (least clicky): Go To Cell
1. Press **Ctrl+G** (Go To Cell).  
   - If Ctrl+G doesn’t open anything in this environment, use **F5** (Navigator) and look for the **Name** / **cell reference** field.
2. Type the cell reference (e.g., `B12`) and press **Enter**.
3. **Verify navigation succeeded** (see “Verification” below).
4. Type the desired value (e.g., `Hello World`) and press **Enter**.

## Name Box workflow (when you must use the Name Box)
1. **Click once** inside the **Name Box** (the small field that usually displays `A1`, left of the formula bar). Avoid combining click+type in one action.
2. Press **Ctrl+A** to select all text in the Name Box.
3. Type the reference (e.g., `B12`) and press **Enter**.
4. **Verify** you landed on B12.
5. Type your value and press **Enter**.

## Verification (do this immediately after pressing Enter)
Confirm at least one of:
- The **Name Box now displays `B12`** (not a range like `A1:C1`).
- A **single-cell highlight border** is visible on **column B, row 12**.
- Row/column headers for **B** and **12** indicate the active cell.

If verification fails, do not proceed to typing the value—retry navigation.

## Recovery patterns
- **Accidentally selected a range (e.g., A1:C1):**
  1. Press **Esc** (to cancel/clear an in-progress selection mode).
  2. Repeat navigation using **Ctrl+G** (preferred) or the Name Box steps.
- **Name Box contains leftover text/range:** always **Ctrl+A** before typing.
- **Focus ambiguity (typing goes to the grid or another field):**
  - Re-click the intended field, then type (separate actions), then re-verify.

## Micro-script (robust, low-error)
1. Ctrl+G → type `B12` → Enter
2. Check Name Box shows `B12`
3. Type `Hello World` → Enter
