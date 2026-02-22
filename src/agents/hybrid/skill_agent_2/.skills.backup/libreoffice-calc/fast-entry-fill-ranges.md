---
annotations: []
description: Fast fill/copy/select ranges in Calc (Ctrl+D/R; paste blocks; duplicate
  formatted cells)
metrics:
  negative_impact: 0
  neutral_impact: 1
  positive_impact: 6
  times_followed: 6.5
  times_requested: 7
name: fast-entry-fill-ranges
---

## Paste delimited text to fill cells fast

### Fill down: newline-separated list
1. Click the **starting cell** (make sure only **one cell** is selected and you are **not** in edit mode).
2. Paste or type text with **one item per line** (line breaks/newlines between items).
3. Calc splits it into successive rows **down the same column**, starting at that cell.

### Fill across: one row of tab-separated values (TSV)
1. Click the first destination cell (e.g., **A2**), **not** in edit mode.
2. Paste a single line where **Tab** separates fields (e.g., `Name\tAddress\tPhone\tWebsite`).
3. Calc distributes the fields into consecutive columns in that row.

Notes:
- If the pasted text contains **tabs**, Calc will split into **multiple columns**.
- If you accidentally start in the wrong cell, **Ctrl+Z** and paste again.
- If it pastes as a single wrapped cell, try **Ctrl+Shift+V** (Paste Special) and choose **Unformatted text**.

### Paste a whole table block (tabs + newlines)
Use this to create small tables quickly (headers + values + formulas) without cell-by-cell entry.

1. Click the top-left destination cell (e.g., **A1**), **not** in edit mode.
2. Paste a block where:
   - **Tab** separates columns
   - **Enter/Newline** separates rows
3. You can include **formulas** in the pasted block (cells starting with `=` will be placed as formulas in their target cells).

## Duplicate a formatted cell/block (calendar/timetable “event block”)
Use this when the **visual formatting** (fill, borders, alignment) matters more than the text.

1. Click an existing formatted cell (or select the whole multi-cell block).
2. **Ctrl+C**.
3. Click the destination (for multi-cell blocks, click the **top-left** destination; ensure the destination range is free).
4. **Ctrl+V**.
5. Edit only the text: press **F2** → **Ctrl+A** (selects cell text *in edit mode*) → type → **Enter**.

### If you want only the formatting (not the old text)
- **Ctrl+C** source → destination → **Ctrl+Shift+V** (**Paste Special**) → **Formats only**.

### Paint the same format onto many cells
- Use **Clone Formatting** (paintbrush): click the formatted cell → click **Clone Formatting** → click destination cells. (Double-click the icon to apply to multiple destinations.)

## Append multiple rows, then extend an adjacent formula column (ledger/running balance)
Common pattern: paste new transactions into columns **A:D**, then extend the balance formula in **E**.

1. Click the first empty cell of the new block (e.g., **A9**) and paste the tab+newline-delimited rows.
2. Extend the balance/formula column:
   - **Fastest (often):** click the **last existing formula cell** (e.g., **E8**) and **double-click the fill handle** (bottom-right corner). Calc will autofill down to match the length of the **adjacent contiguous data** (e.g., column D).
   - **Manual range:** select a range that includes the starter formula at the top (e.g., **E8:E12**) and press **Ctrl+D**.
   - **Copy/paste:** **Ctrl+C** on **E8**, select **E9:E12**, **Ctrl+V**.

## Jump to a specific cell quickly (Name Box)
Useful in large sheets when scrolling is slow/error-prone.

1. Click the **Name Box** (left of the formula bar; shows the current cell like `K46`).
2. Type a cell reference (e.g., `B6`) and press **Enter** to jump/select it.
3. Use **Ctrl+C** to copy the cell (or start editing with **F2**).

## Fast keyboard data entry (row-by-row)
1. Click the first cell (e.g., **A1**).
2. Type the value/formula.
3. Press **Tab** to commit and move right.
4. After the last cell in the row, press **Enter** to commit and move to the next row.

Tip: **Shift+Tab** moves left.

## Fill right / fill down (Ctrl+R / Ctrl+D)
Calc copies from a specific edge of the selection; if the source formula cell isn’t on that edge (or the active cell is blank), fill may do nothing.

1. Enter the formula in the first cell you want to replicate and confirm.
2. Select a range that **includes that formula cell** and extends over the target blank cells.
   - **Fill right (Ctrl+R):** the formula cell must be the **leftmost** cell in the selection.
   - **Fill down (Ctrl+D):** the formula cell must be the **topmost** cell in the selection.

Selection shortcuts:
- Extend by one: **Shift+Arrow**
- Extend to end of a contiguous block: **Ctrl+Shift+Arrow** (e.g., **Ctrl+Shift+Down**)

3. Press **Ctrl+R** (right) or **Ctrl+D** (down).

Note: Use **relative references** (no `$`) in the starter formula if you want references to shift as it fills.

## Fill down fast with the fill handle (double-click)
Often faster than selecting a big range + **Ctrl+D**.

1. Enter the formula in the first row (e.g., **B2**) and confirm.
2. Re-select that cell if needed so its border/handles are visible.
3. Hover the cell’s **bottom-right corner** (the small square “fill handle”) until the cursor becomes a small cross.
4. **Double-click** the fill handle to auto-fill **down** to match the length of the **adjacent column’s contiguous data** (often the column immediately to the left; if that’s empty, Calc may use the other side).

If there are blanks/gaps in that adjacent column, the auto-fill may stop early.

Tip: After autofill, scroll near the bottom to sanity-check the last few rows; **Ctrl+Z** to undo if it filled too far/short.

## Copy a single column’s contiguous data to a new sheet (incl header)
1. Click the **header cell** at the top of the column.
2. Select the contiguous filled range: **Ctrl+Shift+Down** (stops at the **first blank**).
   - If there are gaps, type an explicit range in the **Name Box** (left of the formula bar), e.g. `A1:A500`, then press **Enter**.
3. Copy: **Ctrl+C**.
4. Create the destination sheet: **Sheet > Insert Sheet…** > **OK**.
5. In the new sheet, click **A1** (or your target cell) and paste: **Ctrl+V**.

Optional: rename via **right-click sheet tab > Rename Sheet…**.

## Select the full dataset quickly (common before Pivot Tables/charts)
1. Click the first header cell (often **A1**).
2. Press **Ctrl+Shift+End** to select from that cell to the sheet’s **last used cell**.
3. Glance at the **Name Box** to confirm the selected range looks right (no need to click it unless you’re typing a range).

### If Ctrl+Shift+End selects “too much”
This usually means the sheet has some other used/formatted cell far away.
- From **A1**, use **Ctrl+Shift+Right** then **Ctrl+Shift+Down** (stops at the first blank row/column).
- Or type an exact range in the **Name Box** (e.g., `A1:H500`) and press **Enter**.

## Fill/paste to a large typed range (Name Box)
Useful when you don’t want to scroll (or the destination is far off-screen).

1. Copy the source formula/value cell (**Ctrl+C**).
2. Click the **Name Box** (left of the formula bar), type a range like `J3:J10`, press **Enter** to select it.
3. Paste (**Ctrl+V**) to fill the whole selection.

If you get an overwrite warning, only confirm if you intend to replace all contents in that range.