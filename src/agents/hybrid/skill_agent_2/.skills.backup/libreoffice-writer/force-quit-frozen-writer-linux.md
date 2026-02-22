---
annotations: []
description: Force-quit a frozen LibreOffice Writer via terminal (pgrep/kill escalation)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: force-quit-frozen-writer-linux
---

When Writer/LibreOffice is frozen and won’t close from the GUI on Linux/Unix, terminate it in escalation steps (TERM → KILL) to reduce corruption risk.

## Find the right process(es)
- Preferred: `pgrep -af 'soffice|libreoffice'`  
  (shows PID + full command; often includes `soffice` / `soffice.bin`)
- Fallback: `ps aux | grep -i soffice`

## Graceful stop first (SIGTERM)
1. `kill <pid>`
2. Wait + verify:
   - `sleep 2; pgrep -af 'soffice|libreoffice'`

## Escalate only if needed (SIGKILL)
1. If still running: `kill -9 <pid>`
2. Re-check with `pgrep -af ...`

## Notes
- LibreOffice may spawn multiple related processes; repeat for each PID that remains.
- SIGKILL can drop unsaved work; prefer SIGTERM + a short wait before using `-9`.