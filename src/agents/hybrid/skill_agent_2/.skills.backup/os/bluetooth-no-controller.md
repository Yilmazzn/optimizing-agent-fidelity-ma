---
annotations: []
description: Bluetooth drivers loaded but no controller / “No default controller available”
  (BlueZ + HCI check)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: bluetooth-no-controller
---

## Check BlueZ daemon (service)
1. Check state:
   - `systemctl status bluetooth --no-pager`
   - or `systemctl is-active bluetooth`
2. If inactive, start it:
   - `sudo systemctl start bluetooth`
   - (optional, persist across reboots) `sudo systemctl enable --now bluetooth`

## Confirm an HCI controller actually exists (not just modules)
1. List controllers via BlueZ:
   - `bluetoothctl list`
   - `bluetoothctl show`
2. Also check sysfs:
   - `ls -l /sys/class/bluetooth` (should show `hci0`, etc.)
3. If `bluetoothctl` reports **`No default controller available`** and `/sys/class/bluetooth` is empty, BlueZ is running but **no adapter is detected/usable**.

### Interpreting the “modules loaded” trap
- Kernel modules like `btusb`/`bluetooth` can be loaded even when **no physical controller** is present.
- If you only see `/dev/vhci` (and still no `hci0`), you likely have no attached controller.

## Hardware blocked / missing
1. Check for a Bluetooth USB device:
   - `lsusb | grep -i bluetooth`
2. Check whether it’s soft/hard blocked:
   - `rfkill list`
   - (if blocked) `sudo rfkill unblock bluetooth`

## Common VM gotcha
If you’re in a VM/container, you may simply have **no Bluetooth hardware passed through**. Attach a USB Bluetooth adapter to the VM (USB passthrough) or Bluetooth cannot be enabled.