---
annotations: []
description: Sort a Calc dataset by one column (avoid partial sorts; find min/max
  rows)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: sort-table-by-column
---

## Quick sort (Calc auto-detects the table)
1. Click **one data cell** in the column you want to sort by (avoid the header row).
2. Use **Data > Sort Ascending** / **Sort Descending** (or the A→Z / Z→A toolbar buttons).
3. If Calc prompts **"Extend/Expand selection?"**, choose **Expand selection / sort the whole range** (so entire rows move together).
4. Sanity-check that **entire rows moved together** (no “column-only” shuffle).

## Fast way to find the min/max row
- Sort **Ascending** to bring the **smallest** values to the top; the **first data row below the header** is the minimum.
- Sort **Descending** to bring the **largest** values to the top.
- Read the corresponding cells in that row (e.g., Title/Name) after the sort.

## If the sort didn’t move the whole table
1. **Undo**: **Ctrl+Z**.
2. Select the entire table range (the contiguous block, including headers).
3. Use **Data > Sort…** and set:
   - **Sort by**: the target column
   - **Range contains column labels**: enabled (if you have a header row)
4. Click **OK**.

## Common cause
Quick sort works best when the dataset is a **contiguous block** (no completely blank rows/columns splitting the table).