---
annotations: []
description: 'Fix common first-run conda issues: enable conda in bash + non-interactive
  shells + Anaconda TOS blocks'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: conda-init-noninteractive-bash
---

## When this skill applies
Use this when conda seems “broken” right after install:
- `conda: command not found` / conda not on PATH
- `bash -lc` / CI can’t find conda (non-interactive shells)
- `conda install`/`conda create` is blocked by **Anaconda Terms of Service**

## Case 1: `conda` isn’t installed (fast local Miniconda install)
```bash
bash Miniconda3-latest-Linux-*.sh -b -p ~/miniconda3
~/miniconda3/bin/conda init bash
source ~/.bashrc    # or: source ~/miniconda3/etc/profile.d/conda.sh
conda --version
```

## Case 2: `conda` installed, but not available in *current* terminal
1. Run init (one-time per shell): `conda init bash` (or `~/miniconda3/bin/conda init bash`)
2. Reload init immediately:
   - `source ~/.bashrc`, or
   - `source ~/miniconda3/etc/profile.d/conda.sh`
3. Verify: `conda --version`

## Case 3: Use `conda` in non-interactive commands (`bash -lc`, CI/scripts)
Source conda explicitly inside the command:
```bash
bash -lc 'source ~/miniconda3/etc/profile.d/conda.sh && conda --version'
```
Or, if `conda` is already on PATH:
```bash
bash -lc 'eval "$(conda shell.bash hook)" && conda --version'
```

**Pitfall:** `bash -lc` reads login files (`~/.bash_profile`, `~/.profile`) but not `~/.bashrc` unless those files source it.

## Case 4: `conda install` blocked by Anaconda Terms of Service
If conda prompts for TOS acceptance (or fails/stalls until it’s accepted) and you’re using the default Anaconda channels, accept TOS for them, then retry:
```bash
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

## Quick verification tip
Check that an interactive bash sees it:
```bash
bash -ic 'conda --version'
```