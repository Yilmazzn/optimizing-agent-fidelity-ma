---
annotations: []
description: Download a file by URL and save it with an exact filename/path (wget
  -O / curl -o)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: download-url-exact-filename
---

## Save to an exact filename/location
1. `cd` into the target folder (or use an absolute output path).
2. Download while forcing the output name:
   - **wget:** `wget -O paper01.pdf 'https://example.com/file.pdf'`
   - **curl (follow redirects):** `curl -L -o paper01.pdf 'https://example.com/file.pdf'`

## Verify you got the real file (not an HTML error page)
- `ls -l paper01.pdf`
- `file paper01.pdf` (should say `PDF document` for PDFs)

## Common direct-PDF pattern (arXiv)
- PDF endpoint: `https://arxiv.org/pdf/<id>.pdf` (optionally with version, e.g. `<id>v2`)
- If you have an abstract URL like `https://arxiv.org/abs/<id>`, replace `/abs/` with `/pdf/` and append `.pdf`.