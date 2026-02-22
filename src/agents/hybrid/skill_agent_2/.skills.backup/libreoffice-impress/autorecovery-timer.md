---
annotations: []
description: Set AutoRecovery interval in LibreOffice Impress (Tools > Options)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: autorecovery-timer
---

When you want LibreOffice to periodically write crash-recovery data (not a normal Save).

## Enable / change the AutoRecovery interval
1. In Impress open **Tools ▸ Options…**
2. In the left tree, expand **Load/Save ▸ General**.
3. Enable **Save AutoRecovery information every:**.
4. Edit the minutes value.
   - Prefer **clicking elsewhere / Tab** to leave the field, then proceed.
   - **Avoid relying on Enter** here: it may trigger the dialog’s default **OK** button and close the dialog.
5. Click **OK** (or **Apply** if present).

If you accidentally pressed **Enter** and the dialog closed: the change was likely applied; reopen **Tools ▸ Options…** and confirm the minutes value persisted.

Notes:
- This is the built-in “autosave-like” feature; it creates recovery info so LibreOffice can restore after a crash. Still save normally for guaranteed disk writes.
- The setting is in global Options (it typically affects all LibreOffice components, not just the current file).