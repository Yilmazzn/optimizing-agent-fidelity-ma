---
annotations: []
description: Fix local Python imports failing due to wrong working directory (ModuleNotFoundError)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: python-import-cwd
---

When running ad-hoc Python snippets/tests against a **non-installed local project**, import resolution often depends on the current working directory (cwd).

## Preferred: run from the project root
Tools/commands may default to `$HOME`; make the `cd` part of the same command:
```bash
cd /path/to/project && python3 - <<'PY'
import tetris, block
PY
```

## If you can’t control cwd: add the project dir to `sys.path`
```python
import sys
sys.path.insert(0, "/path/to/project")  # first so it wins over site-packages
```

## Alternative: set `PYTHONPATH`
```bash
PYTHONPATH=/path/to/project python3 your_test.py
```

**Symptom:** `ModuleNotFoundError` for modules that exist as files in the repo (e.g., `tetris.py`).