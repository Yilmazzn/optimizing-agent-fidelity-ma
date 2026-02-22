---
annotations: []
description: Parse fixed-layout PDF tables from pdftotext -layout (totals, spaced
  labels, repeated column blocks)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: pdftotext-table-parse
---

## Convert PDF → text (keep layout)
Use `-layout` when column spacing matters:
```bash
pdftotext -layout file.pdf -
```

## Case 1: Match labels with optional inter-letter spaces
Some PDFs insert spaces between letters (e.g., `T o t a l`). Match with `\s*` between characters:
```python
re.search(r'^T\s*o\s*t\s*a\s*l\b', line.strip(), flags=re.I)
```
Helper to build a spaced pattern from a word:
```python
pat = r'^' + r'\s*'.join(map(re.escape, "Total")) + r'\b'
```

## Case 2: If rows might wrap, join a small window
If the target row can wrap, join it with the next few lines before extracting numbers:
```python
window = " ".join(lines[i:i+4])  # current + next 3
```

## Case 3: Wide single-page summary tables (e.g., A3 Annex tables)
Goal: quickly extract the grand-total row without heavy table libraries.

1. Sanity-check structure (pages + size):
   ```bash
   pdfinfo file.pdf | egrep -i 'Pages|Page size'
   ```
2. Peek the end of the extracted text (totals often near bottom):
   ```bash
   pdftotext -layout file.pdf - | tail -n 80
   ```
3. Find the grand-total row and extract its numeric token sequence.

### Token-by-position extraction (repeated column blocks)
If the total row is a repeated block like `(AppNo, AppAmt, SuppNo, SuppAmt)` per institution, treat the extracted numeric tokens as a flat list and slice by stride:
```python
nums = re.findall(r'\d[\d,]*(?:\.\d+)?', window)
vals = [float(n.replace(',', '')) for n in nums]  # or int(...) if no decimals

app_no  = vals[0::4]
app_amt = vals[1::4]
supp_no = vals[2::4]
supp_amt= vals[3::4]
```
(Adjust the stride/offsets to match the table’s column ordering.)

## Extract numeric tokens (generic)
Integers with thousands separators:
```python
nums = re.findall(r'\d[\d,]*', window)
vals = [int(n.replace(',', '')) for n in nums]
```
If amounts can contain decimals, use `(?:\.\d+)?` as above.