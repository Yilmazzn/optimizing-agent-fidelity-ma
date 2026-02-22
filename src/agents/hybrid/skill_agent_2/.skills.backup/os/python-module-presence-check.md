---
annotations: []
description: Check if Python libs (pandas/openpyxl) exist before choosing an XLSX/CSV
  output path
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 3
  times_followed: 3.0
  times_requested: 3
name: python-module-presence-check
---

When you’re tempted to script spreadsheet output, first confirm key libs exist (to avoid mid-task dependency detours).

## Check module availability (fast)
- `python3 -c "import pandas, openpyxl"`  
  (or split them if you want to know which one is missing)

If you get `ModuleNotFoundError` and you’re time-sensitive, **pick a fallback early** instead of troubleshooting installs.

## Fast fallbacks (no installs)
### Write CSV with the standard library
- Build rows as `list[list]` or `list[dict]`.
- Use `csv.writer` / `csv.DictWriter`.

Example (dict rows):
```python
import csv
rows = [{"name":"A","pass_rate":0.83},{"name":"B","pass_rate":0.5}]
with open("out.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader(); w.writerows(rows)
```

### Need an `.xlsx` deliverable
- **If LibreOffice is available**: write CSV, then convert:
  - `libreoffice --headless --convert-to xlsx --outdir . out.csv`
- **If LibreOffice isn’t available** and the output is a simple table: generate a minimal XLSX by zipping OOXML parts (Python stdlib only).

### Quick human-readable table (Markdown)
If the output just needs to be readable in chat/README, print a Markdown table:
```python
rows = [("A",0.83),("B",0.5)]
print("| Name | Pass rate |\n|---|---|")
for name, r in rows:
    print(f"| {name} | {r:.0%} |")
```

## Only install if it won’t derail the timeline
Use `python3 -m pip install ...` (or system packages) only when you’re confident it’s allowed and quick in the current environment.