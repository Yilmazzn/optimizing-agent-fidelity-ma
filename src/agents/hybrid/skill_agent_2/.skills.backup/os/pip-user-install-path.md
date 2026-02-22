---
annotations: []
description: pip install without sudo; fix ~/.local/bin PATH; avoid timeouts by splitting
  installs
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: pip-user-install-path
---

## Decide install mode (venv vs system)
- **In a venv**: use `python3 -m pip install ...` (no `--user`).
- **System Python, no sudo**: add `--user` to each pip command.

## If installed CLI commands aren’t found (~/.local/bin not on PATH)
1. Add to `~/.bashrc` (interactive bash):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```
   (For login shells, you may prefer `~/.profile`.)
2. Reload:
   ```bash
   source ~/.bashrc
   ```

## Confirm user install locations (debugging)
```bash
python3 -c "import site; print(site.getusersitepackages())"
python3 -c "import site; print(site.getuserbase())"  # scripts usually in ~/.local/bin
```

## Avoid timeouts: split a long pip install into restartable chunks
When `pip install -r requirements.txt` is huge/slow (big wheels like PyTorch), do:
1. Upgrade pip tooling (often speeds resolution):
   ```bash
   python3 -m pip install -U pip setuptools wheel
   ```
2. Install the heaviest dependency first (example):
   ```bash
   python3 -m pip install torch
   ```
3. Install the rest:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
4. If needed:
   ```bash
   python3 -m pip install -e .
   ```

Notes:
- If you’re in **system Python without sudo**, add `--user` to each of the above.
- If a step times out, re-run **only that step**; pip installs are usually re-runnable.
- After each big step, do a quick import check (e.g., `python3 -c "import torch"`).