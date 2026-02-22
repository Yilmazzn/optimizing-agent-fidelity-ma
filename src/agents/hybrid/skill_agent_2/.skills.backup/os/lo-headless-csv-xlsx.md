---
annotations:
- 'Skill not followed [chose_alternative]: Python libs were missing, but instead of
  converting via headless LibreOffice, I opened the XLSX directly in LibreOffice Calc
  and copied the relevant GPT-4 row into Writer. Faster and avoided file-conversion
  steps.'
- 'Skill not followed [chose_alternative]: LibreOffice headless conversion would have
  worked as the intended fallback (CSV → XLSX), but I instead generated a minimal
  XLSX directly (OOXML zipped package) to avoid depending on LibreOffice availability/behavior
  and to keep the deliverable as a single step once the counts were extracted.'
description: Convert documents (PDF/DOCX/XLSX/CSV) via LibreOffice headless CLI (batch
  + isolated profile)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 3
  times_followed: 3.0
  times_requested: 5
name: lo-headless-csv-xlsx
---

## Template (recommended): headless convert with an isolated profile
Use this when LibreOffice GUI might already be running (or you see profile/lock errors).

```bash
OUTDIR="$PWD"
PROFILE_DIR="$(mktemp -d /tmp/lo-profile-XXXXXX)"
LO_BIN="$(command -v soffice || command -v libreoffice)"

"$LO_BIN" --headless --nologo --nofirststartwizard --nolockcheck --norestore \
  -env:UserInstallation="file://$PROFILE_DIR" \
  --convert-to <FORMAT> --outdir "$OUTDIR" "<INPUT_FILE>"

rm -rf "$PROFILE_DIR"
```

Notes:
- Some distros use `libreoffice` instead of `soffice` (or vice versa).
- Output filename is usually the same basename with the new extension.

## Case: Generate a DOCX from a plain-text file (no GUI)
Useful for quick, automated deliverables when you don’t need rich formatting.

1. Create the source text:
```bash
cat > ans.txt <<'EOF'
Your report text here...
EOF
```

2. Convert to DOCX:
```bash
libreoffice --headless --nologo --nofirststartwizard \
  --convert-to docx --outdir "$HOME" \
  ans.txt
```

3. Verify output:
```bash
ls -l "$HOME/ans.docx"
file "$HOME/ans.docx"
```

Notes:
- `.txt` imports as plain text; for consistent headings/tables, generate an `.odt` first (then convert `.odt -> .docx`).

## Case: `Warning: failed to launch javaldx` during conversion
1. **Don’t assume failure from the warning.** First verify the outputs were created (e.g., `ls -1 "$OUTDIR"/*.pdf`) and open/inspect one.
2. Only troubleshoot Java if **outputs are missing/corrupt** or the documents rely on **Java-dependent features** (macros, some extensions).

## Case: batch convert Word `.doc` -> PDF (Linux)
### Simple (one command, outputs to Desktop)
Run from the directory containing the files:

```bash
libreoffice --headless --nologo --nofirststartwizard \
  --convert-to pdf --outdir "$HOME/Desktop" \
  *.doc
```

### Safer globbing (`.doc` and `.DOC`, and no-match-safe)
Avoids errors when there are no matches, and handles uppercase extensions:

```bash
shopt -s nullglob
files=(./*.doc ./*.DOC)

OUTDIR="$HOME/Desktop"
PROFILE_DIR="$(mktemp -d /tmp/lo-profile-XXXXXX)"

for f in "${files[@]}"; do
  soffice --headless --nologo --nofirststartwizard --nolockcheck --norestore \
    -env:UserInstallation="file://$PROFILE_DIR" \
    --convert-to pdf --outdir "$OUTDIR" "$f"
done

rm -rf "$PROFILE_DIR"
```

Verify output:
```bash
ls -1 "$HOME/Desktop"/*.pdf
```

## Case: CSV -> XLSX (useful fallback when Python `openpyxl/pandas` aren’t available)
- If you care about column names, ensure the CSV has a **header row**.

### Simple (works if LibreOffice isn’t already running)
```bash
libreoffice --headless --nologo --nofirststartwizard \
  --convert-to xlsx --outdir "$HOME/Desktop" \
  "$HOME/Desktop/report.csv"

ls -l "$HOME/Desktop"/report*.xlsx
```

### More robust (isolated profile + auto-detect binary)
```bash
OUTDIR="$PWD"
PROFILE_DIR="$(mktemp -d /tmp/lo-profile-XXXXXX)"
LO_BIN="$(command -v soffice || command -v libreoffice)"

"$LO_BIN" --headless --nologo --nofirststartwizard --nolockcheck --norestore \
  -env:UserInstallation="file://$PROFILE_DIR" \
  --convert-to xlsx --outdir "$OUTDIR" "report.csv"

rm -rf "$PROFILE_DIR"
```

If you get an output like `report.csv.xlsx`, rename it to `report.xlsx`.

If `libreoffice/soffice` isn’t installed (or you don’t want to depend on it), another fallback is generating a minimal XLSX directly by writing OOXML parts into a ZIP (Python stdlib-only).

## Case: ODS -> CSV
```bash
OUTDIR="$PWD"
PROFILE_DIR="$(mktemp -d /tmp/lo-profile-XXXXXX)"

soffice --headless --nologo \
  -env:UserInstallation="file://$PROFILE_DIR" \
  --convert-to csv --outdir "$OUTDIR" "yourfile.ods"
```