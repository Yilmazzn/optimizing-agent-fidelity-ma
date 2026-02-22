---
annotations: []
description: Define print ranges and fit-to-page scaling for printing/PDF in Calc
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: define-print-range
---

## Define a print range (print/export only part of a sheet)
1. Select the cells you want included.
   - Common quick select (table starts at **A1**): **Ctrl+Home** → **Ctrl+Shift+End**.
   - Otherwise: click the table’s top-left cell → **Ctrl+Shift+End**.
2. If the selection becomes **huge** (stray formatted/used cells elsewhere):
   - From the table’s top-left cell use **Ctrl+Shift+Right** then **Ctrl+Shift+Down** (stops at first blank row/col), or
   - Type an explicit range in the **Name Box** (e.g., `A1:H200`) and press **Enter**.
3. Go to **Format > Print Ranges > Define**.
4. (Optional) Check via **File > Print Preview**.

### Edit / reset later
- **Replace**: select a new range → **Format > Print Ranges > Define**.
- **Add another block** (multiple print areas): select it → **Format > Print Ranges > Add**.
- **Clear**: **Format > Print Ranges > Remove**.

## Fit the print range to one page (print or Export as PDF)
1. (Optional) Define the print range first: **Format > Print Ranges > Define**.
2. Go to **Format > Page Style…**.
3. Open the **Sheet** tab.
4. In **Scaling mode**, choose **Fit print range(s) to width/height**.
5. Set **Width = 1** page and **Height = 1** page.
6. **OK**, then print / **File > Export As > Export as PDF…**.

### Variations
- **Fit to width only:** set **Width = 1** and leave **Height** blank/0 (or use “Automatic” if present) so it can flow to multiple pages vertically.

Note: **Page Style > Sheet > Scaling** applies to the defined print range(s), not the whole sheet.