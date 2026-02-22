---
annotations: []
description: Install PyTorch (torch) CPU-only via pip using the official wheel index
  URL
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: pytorch-cpu-pip-index
---

## CPU-only install (no venv)
1. (Optional but helps) Upgrade pip:
   - `python3 -m pip install --user -U pip`
2. Install from PyTorch’s CPU wheel index (fast; avoids source builds / wrong wheels):
   - `python3 -m pip install --user -U --index-url https://download.pytorch.org/whl/cpu torch`
   - (Often installed together) `python3 -m pip install --user -U --index-url https://download.pytorch.org/whl/cpu torchvision torchaudio`
3. Verify:
   - `python3 -c "import torch; print(torch.__version__); print('cuda?', torch.cuda.is_available())"`
4. Then install the rest of your project requirements (so torch is already satisfied).