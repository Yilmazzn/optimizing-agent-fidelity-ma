---
annotations: []
description: Open/import CSVs (Text Import) and export sheets back to CSV in Calc
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: csv-import-export
---

## Import/open a CSV (Text Import dialog)
1. Open the `.csv` (double-click in file manager, or run `libreoffice --calc "/path/file.csv" &`).
2. In **Text Import**:
   - Set the correct delimiter (often **Separated by: Comma**).
   - Click **OK**.

### If the Text Import dialog is hidden
- It can appear behind other windows → **Alt+Tab** to bring it forward.

## Convert CSV to XLSX/ODS (so it behaves like a normal spreadsheet)
1. **File > Save As…** (**Ctrl+Shift+S**).
2. Choose **Excel 2007–365 (.xlsx)** or **ODF Spreadsheet (.ods)** → **Save**.

## Export to CSV (Text CSV)
1. **Select the sheet you want exported** (CSV outputs the *current/active sheet* only).
2. **File > Save As…** (**Ctrl+Shift+S**).
3. In **File type**, choose **Text CSV (.csv)**.
4. Ensure the filename ends in **.csv** → **Save**.
5. If prompted, choose **Use Text CSV Format** (not ODF).
6. In **Export Text File** (CSV options), click **OK** (or set delimiter/quotes as needed).

## Optional: Export to HTML
1. **File > Save As…** → choose **HTML Document (Calc) (.html)** → **Save**.
2. If an **HTML Export** dialog appears, choose **current sheet** vs **entire document**.

## If you must avoid the Text Import dialog entirely
- Convert headlessly first, then open the converted file (see `os/lo-headless-csv-xlsx`).