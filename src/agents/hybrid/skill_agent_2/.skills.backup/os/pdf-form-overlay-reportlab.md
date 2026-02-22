---
annotations: []
description: 'Overlay/fill static PDF templates: rasterize + pixel→pt coords (reportlab)'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: pdf-form-overlay-reportlab
---

When a PDF is hard to edit/fill (no form fields, pdftk/qpdf missing, LibreOffice import unreliable), a robust fallback is: **rasterize the template to a fixed-DPI image** and generate a new PDF by drawing that image as the background + placing text/checkmarks at known coordinates.

## Prereqs (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils python3-reportlab fonts-dejavu-core
```
Useful checks:
```bash
command -v pdftk qpdf pdftocairo pdfinfo
```

## 1) Rasterize the template at a known DPI
Use a stable DPI (e.g., 300) so your coordinate math stays consistent:
```bash
dpi=300
pdftocairo -png -r "$dpi" template.pdf /tmp/template
# outputs: /tmp/template-1.png, /tmp/template-2.png, ...
```
Tip: `pdfinfo template.pdf | grep -i 'Page size'` helps sanity-check expected page size.

## 2) Convert PNG pixel coordinates to PDF points (reportlab)
Reportlab uses **points** (72 per inch) with origin at **bottom-left**.
If you measure positions on the PNG in **pixels from top-left**, convert like:
- `x_pt = x_px * 72 / dpi`
- `y_pt = (img_h_px - y_px) * 72 / dpi`

## 3) Overlay text/checkmarks with reportlab (single-page minimal)
```python
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

DPI = 300
bg_png = "/tmp/template-1.png"
out_pdf = "filled.pdf"

# Unicode-capable font (for symbols like ✓)
pdfmetrics.registerFont(TTFont(
    "DejaVuSans",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
))

img_w_px, img_h_px = Image.open(bg_png).size
page_w = img_w_px * 72.0 / DPI
page_h = img_h_px * 72.0 / DPI

c = canvas.Canvas(out_pdf, pagesize=(page_w, page_h))
c.drawImage(bg_png, 0, 0, width=page_w, height=page_h)

c.setFont("DejaVuSans", 10)
# Example: place text at (x_px, y_px) measured on the PNG from top-left
x_px, y_px = 850, 420
x_pt = x_px * 72.0 / DPI
y_pt = (img_h_px - y_px) * 72.0 / DPI
c.drawString(x_pt, y_pt, "John Smith")

c.save()
```

## 4) Auto-find table/grid cell centers (when you don't have coordinates)
If the template has clear table/grid lines, you can estimate line positions by counting “dark” pixels per row/column and clustering contiguous hits.

```python
import numpy as np
from PIL import Image

img = Image.open(bg_png).convert("L")
a = np.array(img)
mask = a < 40  # tune threshold for "black"

row_counts = mask.sum(axis=1)  # per y
col_counts = mask.sum(axis=0)  # per x

# indices likely to be part of a long line (tune ratios for your form)
h_idx = np.where(row_counts > mask.shape[1] * 0.6)[0]  # horizontal lines
v_idx = np.where(col_counts > mask.shape[0] * 0.6)[0]  # vertical lines

def cluster_centers(idxs, gap=2):
    if len(idxs) == 0:
        return []
    idxs = np.sort(idxs)
    groups = []
    start = prev = int(idxs[0])
    for i in idxs[1:]:
        i = int(i)
        if i - prev > gap:
            groups.append((start, prev))
            start = i
        prev = i
    groups.append((start, prev))
    return [ (lo + hi) // 2 for lo, hi in groups ]

h_lines = cluster_centers(h_idx)
v_lines = cluster_centers(v_idx)

# Example: cell center (row r, col c) between adjacent lines
r, c = 0, 0
x_px = (v_lines[c] + v_lines[c+1]) // 2
y_px = (h_lines[r] + h_lines[r+1]) // 2
```
Then use the same pixel→point conversion from section (2).

Notes:
- If you get too many/too few lines, adjust `DPI`, `mask` threshold, and the `0.6` coverage ratios.
- This works best when lines span most of the row/column (tables); it’s not robust for arbitrary shapes.

## 5) Quick alignment sanity-check
Rasterize the output PDF and visually inspect a couple pages:
```bash
pdftocairo -png -r 150 filled.pdf /tmp/filled_check
xdg-open /tmp/filled_check-1.png
```