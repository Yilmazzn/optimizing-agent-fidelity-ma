---
annotations: []
description: Move charts to new sheet; set Pivot Table source + destination in Calc
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 3
  times_followed: 3.0
  times_requested: 3
name: pivot-table-destination
---

## Case 1: Put a chart on a new sheet (keep source data range intact)
1. Create the chart from the data: select the range (incl. headers) → **Insert > Chart…** → finish the wizard.
2. Select the **whole chart object**:
   - Click the chart’s **border/edge** until you see **resize handles** (not just an element inside the plot).
   - If you enter chart edit mode, press **Esc** and click the border again.
3. Copy the chart object: **Ctrl+C**. (Use **Ctrl+X** only to move the *chart object*; don’t cut the data range.)
4. Create a destination sheet: right-click a sheet tab → **Insert Sheet…** → **OK**, then switch to it.
5. Paste: **Ctrl+V** and resize/reposition.

**Pitfall:** Avoid **Ctrl+X** on the **data cells** when you only intend to move the chart—charts reference ranges, so moving/removing the source range can break/change the chart.

## Case 2: Pick the Pivot Table source range (avoid whole-sheet Ctrl+A)
1. Click inside the dataset (ideally the **top-left header cell**).
2. Select the used block:
   - If the table starts at **A1**: **Ctrl+Home** → **Ctrl+Shift+End**.
   - Otherwise: click the table’s top-left cell → **Ctrl+Shift+End**.
3. Sanity-check the selection in the **Name Box** (left of the formula bar). If it looks huge, don’t proceed.

### If Ctrl+Shift+End selects “too much”
This usually means the sheet has some used/formatted cell far away.
- From the table’s top-left cell: **Ctrl+Shift+Right** then **Ctrl+Shift+Down** (stops at the first blank row/column), or
- Type an explicit range in the **Name Box** (e.g., `A1:H500`) and press **Enter**.

## Case 3: Control Pivot Table output location (new sheet vs exact position)
1. Start: **Data > Pivot Table > Insert or Edit…** to open **Pivot Table Layout**.
2. Expand **Source and Destination** by clicking the **tiny disclosure triangle** next to the label (the text itself often isn’t a reliable click target).
3. Under **Destination**, choose:
   - **New sheet**, or
   - **Selection** to place the pivot starting at a specific cell.

### Place multiple pivot tables on the same report sheet (type destination)
1. In **Destination**, select **Selection**.
2. Click into the destination input box and **type** a reference like:
   - `$ReportSheet.$A$1` (or `$ReportSheet.$D$1`, etc.)
   - If the sheet name contains spaces: `$'Report Sheet'.$A$1`
3. Click **OK** to generate the pivot at that exact location.

### If you can’t find/expand it quickly
Proceed with **OK**: Calc typically outputs to a newly created pivot sheet by default.

### Rename the auto-created Pivot Table sheet
1. Find the new pivot sheet tab (often named like **“Pivot table_<sheet>_<n>”**).
2. **Right-click tab > Rename Sheet…**
3. Enter the required name → **OK**.