---
annotations: []
description: Extract plain text from a .docx via unzip + XML (no Writer/Word)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: extract-docx-text-via-zip-xml
---

When you need to quickly *read* a DOCX (e.g., requirements/instructions) without opening Word/Writer, remember: **`.docx` is a ZIP of XML**.

## Quick peek (raw XML)
```sh
unzip -p "/path/file.docx" word/document.xml | less
```

## Readable text (quick-and-dirty)
### Option A (recommended): `perl` one-liner (reliable newlines)
```sh
unzip -p "/path/file.docx" word/document.xml \
| perl -0777 -pe 's#</w:p>#\n#g; s#<[^>]*>##g; s/[\t ]+/ /g; s/\n{2,}/\n/g' \
| sed '/^[[:space:]]*$/d' \
| less
```

### Option B: `sed` (only if you can insert *real* newlines)
Many `sed` variants don’t treat `\n` in the replacement as a newline. In bash, ANSI-C quoting usually works:
```sh
unzip -p "/path/file.docx" word/document.xml \
| sed $'s#</w:p>#\n#g' \
| sed 's#<[^>]*>##g' \
| sed '/^[[:space:]]*$/d' \
| less
```

## Notes / common gotchas
- Main body text: `word/document.xml`.
- Headers/footers: `word/header*.xml`, `word/footer*.xml`.
- Tag-stripping won’t preserve tables/layout perfectly; use it when you only need readable, line-based text.