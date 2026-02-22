---
annotations: []
description: Extract/prepare speaker notes from PPTX XML or a DOCX (Slide N:)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: extract-pptx-notes-xml
---

When you need speaker/presenter notes as **plain text** (batch extraction) or you have notes in a separate **.docx** you need to paste into Impress.

## Case 1: Extract all notes from a .pptx without opening Impress/PowerPoint
`.pptx` is a ZIP; notes are in `ppt/notesSlides/notesSlideN.xml`.

1. (Optional) confirm notes exist:
   ```bash
   unzip -l deck.pptx | grep -E 'ppt/notesSlides/notesSlide[0-9]+\.xml'
   ```
2. Extract the **notes body** placeholder text (skips slide image / slide number fields):
   ```bash
   python3 - <<'PY'
import zipfile,re
from xml.etree import ElementTree as ET
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}

def note_text(xml_bytes):
    root=ET.fromstring(xml_bytes)
    out=[]
    for sp in root.findall('.//p:sp', NS):
        ph=sp.find('.//p:nvSpPr/p:nvPr/p:ph', NS)
        if ph is None or ph.get('type')!='body':
            continue
        for ap in sp.findall('.//a:p', NS):
            line=[]
            for n in ap.iter():
                tag=n.tag.rsplit('}',1)[-1]
                if tag=='fld' and n.get('type')=='slidenum':
                    line=[]; break
                if tag=='t' and n.text:
                    line.append(n.text)
                if tag=='br':
                    line.append('\n')
            s=''.join(line).strip()
            if s:
                out.append(s)
    return '\n'.join(out)

with zipfile.ZipFile('deck.pptx') as z:
    names=sorted(n for n in z.namelist() if re.match(r'ppt/notesSlides/notesSlide\d+\.xml$', n))
    for name in names:
        print(f'--- {name} ---')
        print(note_text(z.read(name)))
        print()
PY
   ```

## Case 2: Extract per-slide note blocks from a .docx that contains markers like “Slide 1:”
Useful when notes were authored externally and you want copy/paste not to drift.

```bash
python3 - <<'PY'
import re, zipfile
from xml.etree import ElementTree as ET
DOCX='notes.docx'
marker=re.compile(r'^\s*Slide\s+(\d+)\s*:\s*(.*)$', re.I)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

with zipfile.ZipFile(DOCX) as z:
    root=ET.fromstring(z.read('word/document.xml'))

blocks={}  # slide_num -> [lines]
cur=None
for p in root.findall('.//w:p', ns):
    txt=''.join(t.text or '' for t in p.findall('.//w:t', ns)).strip()
    if not txt:
        continue
    m=marker.match(txt)
    if m:
        cur=int(m.group(1))
        blocks.setdefault(cur, [])
        rest=m.group(2).strip()
        if rest:
            blocks[cur].append(rest)
    elif cur is not None:
        blocks[cur].append(txt)

for n in sorted(blocks):
    print(f'--- Slide {n} ---')
    print('\n'.join(blocks[n]).strip())
    print()
PY
```

## Case 3: Paste into Impress speaker notes accurately
1. Select slide **N** in the **Slides** pane.
2. **View ▸ Notes**.
3. Scroll/Page Down to the large **“Click to add Notes”** area (it’s typically **below the slide image** on the Notes page).
4. Double-click in the notes body → **Ctrl+A** → paste the extracted text.