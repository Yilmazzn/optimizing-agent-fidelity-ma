---
annotations: []
description: 'Run sudo/apt-get in non-interactive shells (no TTY): -S, -n, multi-command
  patterns'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: sudo-noninteractive
---

## Detect non-interactive sudo failures
If `sudo` errors like `a terminal is required to read the password` / hangs waiting for a prompt, you’re in a non-interactive runner (no TTY).

## Preferred for automation: avoid password prompts
- If the environment should already have sudo access: use **non-interactive mode** to fail fast:
  ```bash
  sudo -n true   # exits nonzero if a password would be required
  ```
- Best fix: configure passwordless sudo for the automation user (sudoers) or run as root/container.

## If you *must* supply a password via stdin
1. Use `-S` (read password from stdin). Include a newline:
   ```bash
   printf '%s\n' "$SUDO_PASSWORD" | sudo -S <command>
   ```
2. For multiple commands, avoid re-supplying the password by running one root shell:
   ```bash
   printf '%s\n' "$SUDO_PASSWORD" | sudo -S bash -lc 'apt-get update && apt-get install -y <pkgs>'
   ```
   (Add `-p ''` to suppress the password prompt text if it pollutes logs.)

**Security note:** don’t hardcode passwords in command history; prefer an env var/secret store.

## APT in automation: avoid interactive prompts
Use `-y` and (if needed) noninteractive frontend:
```bash
sudo -n apt-get install -y <pkgs>
# or
DEBIAN_FRONTEND=noninteractive sudo -n apt-get install -y <pkgs>
```

## When `apt-get update` warns about a broken third-party repo/key
A failing external repo (e.g., `NO_PUBKEY` for Chrome) may not block installing packages from Ubuntu repos, but **check**:
- If `apt-get install` can fetch the required packages, proceed.
- If installs fail, temporarily disable/fix the offending repo in `/etc/apt/sources.list.d/*.list` (comment it out) and re-run `apt-get update`.