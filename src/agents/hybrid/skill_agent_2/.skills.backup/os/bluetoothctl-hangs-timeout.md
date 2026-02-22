---
annotations: []
description: 'When bluetoothctl show/list hangs: use timeout and check BlueZ service'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: bluetoothctl-hangs-timeout
---

When BlueZ/D-Bus isn’t responding (no controller, service stuck), `bluetoothctl` commands like `show`/`list` can block.

## Quick non-blocking diagnostics
1. Wrap commands with a short timeout:
   - `timeout 5 bluetoothctl show`
   - `timeout 5 bluetoothctl list`
2. If it times out, check BlueZ service state:
   - `systemctl is-active bluetooth`  
   - (optional) `systemctl status bluetooth`
3. Restart/start the service:
   - `sudo systemctl restart bluetooth`  
   - or `sudo systemctl start bluetooth`

## If it still times out
- Check logs for errors:
  - `journalctl -u bluetooth -b --no-pager | tail -n 200`