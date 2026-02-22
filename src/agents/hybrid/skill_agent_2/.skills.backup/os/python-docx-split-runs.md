---
annotations: []
description: 'python-docx: format matched substrings (highlight/bold/color) by splitting
  paragraph into runs'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: python-docx-split-runs
---

python-docx can’t apply character-level formatting to a substring *inside an existing run*; to format only matched spans you must rebuild the paragraph as multiple runs.

## Case: Highlight (or bold/color) regex matches within a paragraph
1. Compile a regex for the target (often use `re.IGNORECASE` and/or word boundaries like `r"\bword\b"`).
2. For each paragraph, rebuild its runs by slicing the paragraph text around each match:
   - normal run for text before the match
   - formatted run for the match
   - repeat; then add a final normal run for the remainder
3. Apply formatting only to the match run (e.g., `run.font.highlight_color = WD_COLOR_INDEX.YELLOW`, `run.bold = True`, `run.font.color.rgb = RGBColor(...)`).

```python
import re
from docx.enum.text import WD_COLOR_INDEX

pat = re.compile(r"\btarget\b", re.IGNORECASE)

for p in doc.paragraphs:
    text = p.text
    if not pat.search(text):
        continue

    # Remove existing runs (no public API; this is a common workaround)
    for r in p.runs:
        r._r.getparent().remove(r._r)

    i = 0
    for m in pat.finditer(text):
        if m.start() > i:
            p.add_run(text[i:m.start()])
        hit = p.add_run(text[m.start():m.end()])
        hit.font.highlight_color = WD_COLOR_INDEX.YELLOW
        i = m.end()
    if i < len(text):
        p.add_run(text[i:])
```

### Pitfalls / notes
- Rebuilding runs can discard mixed formatting that existed inside the paragraph. If you need to preserve styling, you must carry over properties from the original runs (or only rebuild when you control the formatting).
- Matches can span runs in the original document; operating on `p.text` + rebuild avoids missing those.