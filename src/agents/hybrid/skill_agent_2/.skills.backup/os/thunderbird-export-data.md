---
annotations: []
description: 'Export Thunderbird data: contacts, locate mbox, convert to .eml'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: thunderbird-export-data
---

## Export contacts from one Address Book (GUI)
1. Open **Thunderbird → Address Book** (often **Ctrl+Shift+B**).
2. In the left sidebar, click the address book you want (e.g., **Personal Address Book**).
3. **Right-click the address book name** → **Export…**.
4. Choose **Save as type/Format** (CSV/vCard/LDIF; varies by version) → pick folder + filename → **Save**.

## Locate Thunderbird mbox files (Linux)
### A) Find the active profile directory
- **GUI:** **Help → Troubleshooting Information → Profile Folder → Open Folder**.
- **File (reliable with multiple profiles):** open `~/.thunderbird/profiles.ini`.
  1. If there is an `[Install<hash>]` section with `Locked=1`, treat its `Default=<path>` as the active profile directory.
     - If `<path>` is relative (doesn’t start with `/`), resolve it under `~/.thunderbird/`.
  2. Otherwise, fall back to the `Profile*` section with `Default=1`.
     - If `IsRelative=1`, profile dir is `~/.thunderbird/<Path>/`.
     - If `IsRelative=0`, profile dir is `<Path>`.
  3. **Sanity-check:** the chosen profile should contain `Mail/` (Local Folders) and/or `ImapMail/` (IMAP).

### B) Where mail is stored
- **Local folders:** `~/.thunderbird/<profile>/Mail/Local Folders/`
- **IMAP accounts:** `~/.thunderbird/<profile>/ImapMail/<server>/`
  - The IMAP inbox is often an mbox file named **`INBOX`** (no extension).
- Mail folders are typically **mbox files with no extension**.
- Index files are `*.msf` (skip for backups/parsing).

### Common gotchas
- Subfolders are usually stored in a sibling directory named `<Folder>.sbd/`.

## Export messages from an mbox to per-message `.eml` (safe, CLI/Python)
1. Locate the mbox file you want (e.g., `.../ImapMail/<server>/INBOX` or `.../Mail/Local Folders/<folder>`). Ignore `*.msf`.
2. **Copy the mbox** to a working folder *before reading it* (avoids corruption/partial reads if Thunderbird is running and modifying it):
   - `cp -a /path/to/INBOX ./INBOX.copy`
3. Iterate the copy and write each message as raw RFC822 bytes:

```python
import mailbox, email.policy, re
from pathlib import Path

src = Path('INBOX.copy')
out = Path('eml_out'); out.mkdir(exist_ok=True)

mb = mailbox.mbox(src)
for i, msg in enumerate(mb, 1):
    subj = (msg.get('subject') or '')
    subj = re.sub(r'[^A-Za-z0-9._-]+', '_', subj).strip('_')[:80]
    fn = out / f"{i:06d}_{subj or 'no_subject'}.eml"
    fn.write_bytes(msg.as_bytes(policy=email.policy.default))
```

Optional: also write a manifest (e.g., `i, date, message-id, subject`) if you need traceability/deduping later.