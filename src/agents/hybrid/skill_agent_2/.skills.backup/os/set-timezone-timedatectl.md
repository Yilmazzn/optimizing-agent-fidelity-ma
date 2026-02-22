---
annotations: []
description: Set or verify Linux (systemd) time zone quickly via timedatectl (e.g.,
  UTC)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: set-timezone-timedatectl
---

## Set time zone to UTC (systemd)
1. Set:
   - `sudo timedatectl set-timezone Etc/UTC`
2. Verify:
   - `timedatectl`
   - Confirm it shows something like: `Time zone: Etc/UTC (UTC, +0000)`

## Pick a different valid time zone
1. List zones:
   - `timedatectl list-timezones | less`
2. Set the chosen zone (example):
   - `sudo timedatectl set-timezone America/New_York`

## Notes
- `timedatectl` requires systemd (common on Ubuntu). If the command is missing, you’re likely on a non-systemd system and need a different method (e.g., editing `/etc/timezone` + reconfigure `tzdata`).