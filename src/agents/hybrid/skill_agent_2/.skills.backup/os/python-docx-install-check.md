---
annotations: []
description: 'Fix ModuleNotFoundError: No module named ''docx'' (python-docx) on fresh
  machines'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: python-docx-install-check
---

## Symptom
- Python script fails with `ModuleNotFoundError: No module named 'docx'` while trying to create/edit `.docx` files.

## Key detail (non-obvious)
- The PyPI package name is **`python-docx`**, but you import it as **`import docx`**.

## Verify quickly
```bash
python3 -c "import docx"
```

## Install (pick the right mode)
### If you’re in a virtual environment
```bash
python3 -m pip install python-docx
python3 -c "import docx"
```

### If you’re using system Python and can’t/won’t use sudo
```bash
python3 -m pip install --user python-docx
python3 -c "import docx"
```

## If it still can’t import
- Ensure you installed into the same interpreter you run (prefer `python3 -m pip ...`, not `pip ...`).
- Sanity-check installation:
  ```bash
  python3 -m pip show python-docx
  ```
- If `--user` installs aren’t being picked up, check where user site-packages live:
  ```bash
  python3 -c "import site; print(site.getusersitepackages())"
  ```
  (See also: pip user install/PATH troubleshooting.)