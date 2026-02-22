---
annotations: []
description: Extract values from nested JSON when schema/key paths vary (recursive
  key search)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: json-recursive-key-search
---

## When to use
You need to pull specific fields (e.g., a model’s output like `GEMINI`) from JSON files where the key may appear at different nesting levels (not reliably at a fixed top-level path).

## Python: recursive walk over dict/list
```python
import json
from pathlib import Path

def find_key(obj, target_key_upper):
    out = []
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(k, str) and k.upper() == target_key_upper and isinstance(v, str):
                    out.append(v)
                walk(v)
        elif isinstance(x, list):
            for it in x:
                walk(it)
    walk(obj)
    return out

data = json.loads(Path("input.json").read_text(encoding="utf-8"))
vals = find_key(data, "GEMINI")
print(f"found {len(vals)}")
for i, s in enumerate(vals, 1):
    print(f"--- {i} ---\n{s}\n")
```

### Notes / pitfalls
- Don’t assume a fixed path like `data['declare_ans']`; datasets often nest under sections like `Multi_Hop -> declare_ans`.
- Filter by value type (e.g., `isinstance(v, str)`) to avoid collecting nested dicts/lists under the same key.
- If you need provenance, modify the walker to also track and return the key path (list of keys/indices).