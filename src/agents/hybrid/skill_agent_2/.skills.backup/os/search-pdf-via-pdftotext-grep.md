---
annotations: []
description: Inspect/search PDF text via pdftotext+grep; extract title/authors; OCR
  if empty
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: search-pdf-via-pdftotext-grep
---

## Install (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr imagemagick
```
- `poppler-utils`: `pdftotext`, `pdftoppm`.
- ImageMagick may use `magick ...` instead of `convert ...`.

## Case -1: You have the PDF somewhere on disk but forgot the path
```bash
find ~/ -maxdepth 5 -type f -iname '*.pdf' 2>/dev/null
```
Tip: narrow it down if you remember a keyword:
```bash
find ~/ -maxdepth 6 -type f -iname '*bert*.pdf' 2>/dev/null
```

## Case 0: Quickly identify what a PDF is (paper title/authors are usually on page 1)
```bash
pdftotext -f 1 -l 1 "file.pdf" - | head -n 60
```
- Increase `head` or page through: `... | less`.
- Use extracted author names/title keywords to search the web.

## Case 1: Quick “does this PDF mention X?”
```bash
pdftotext paper.pdf - | grep -nEi '1810\.04805|Devlin|BERT' | head
```
(Write to a `.txt` file first if you’ll re-run multiple greps.)

## Case 2: Preserve rough columns (statements/invoices)
```bash
work=~/Desktop/pdftext; mkdir -p "$work"
pdftotext -layout "Bank Statement.pdf" "$work/bank.txt"
grep -nE 'ACME|3,180\.00|8480\.00' "$work/bank.txt" | head
```
Tips:
- Limit pages: `pdftotext -f 15 -l 30 in.pdf - | grep -nEi 'pattern'`
- Some PDFs space out letters (e.g., `T o t a l`), so `grep -i 'Total'` can miss.
  - POSIX ERE: `grep -nEi '^T[[:space:]]*o[[:space:]]*t[[:space:]]*a[[:space:]]*l\b' bank.txt`
  - PCRE: `grep -nPi '^T\s*o\s*t\s*a\s*l\b' bank.txt`

## Case 3: `pdftotext` outputs nothing → OCR a scanned/image-only PDF
1. Rasterize pages at ~300 DPI:
   ```bash
   pdftoppm -png -r 300 receipt.pdf /tmp/receipt_page
   # /tmp/receipt_page-1.png, /tmp/receipt_page-2.png, ...
   ```
2. OCR pages:
   ```bash
   for img in /tmp/receipt_page-*.png; do
     echo "\n--- $img ---"
     tesseract "$img" stdout -l eng --psm 6
   done
   ```
- If layout is weird, try `--psm 4`, `--psm 6`, `--psm 11`.

## Case 4: OCR a receipt image (JPG/PNG)
```bash
convert input.jpg -colorspace Gray -resize 200% \
  -contrast-stretch 0x10% -sharpen 0x1 /tmp/prep.png
tesseract /tmp/prep.png stdout -l eng --psm 6
```