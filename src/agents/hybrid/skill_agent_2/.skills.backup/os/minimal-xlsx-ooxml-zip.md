---
annotations: []
description: Create a minimal .xlsx without openpyxl (OOXML parts zipped, Python stdlib
  only)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: minimal-xlsx-ooxml-zip
---

Use only when you **must** output `.xlsx` but `openpyxl/pandas` aren’t available (and you can’t/don’t want LibreOffice).

## Minimal XLSX writer (simple table)
```python
import zipfile,html

def col(n):
 s=""
 while n: n,r=divmod(n-1,26); s=chr(65+r)+s
 return s

def write_xlsx(path,rows):
 def cell(ref,v):
  if isinstance(v,(int,float)) and not isinstance(v,bool):
   return f'<c r="{ref}"><v>{v}</v></c>'
  t=html.escape('' if v is None else str(v))
  return f'<c r="{ref}" t="inlineStr"><is><t>{t}</t></is></c>'
 sd=[]
 for i,row in enumerate(rows,1):
  cs=''.join(cell(f'{col(j)}{i}',v) for j,v in enumerate(row,1))
  sd.append(f'<row r="{i}">{cs}</row>')
 sheet=f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(sd)}</sheetData></worksheet>'
 ct='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'
 rels='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'
 wb='<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>'
 wbr='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
 files={'[Content_Types].xml':ct,'_rels/.rels':rels,'xl/workbook.xml':wb,'xl/_rels/workbook.xml.rels':wbr,'xl/worksheets/sheet1.xml':sheet}
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
  for p,s in files.items(): z.writestr(p,s)

# write_xlsx('report.xlsx', [['name','score'], ['A',1], ['B',2]])
```

Notes: suitable for **simple tables** only (no formatting/formulas). If Excel/LO warns about repairs, prefer CSV→XLSX via LibreOffice or install `openpyxl`.