---
annotations: []
description: Quick GIMP color tweaks + export a renamed copy (e.g., to Desktop)
metrics:
  negative_impact: 0
  neutral_impact: 1
  positive_impact: 0
  times_followed: 0.5
  times_requested: 1
name: brightness-export-copy
---

## Tip: fine-tune slider dialogs quickly
- Drag the slider for a rough setting.
- For precise values, click the **numeric value box once**, then use **↑/↓** to nudge (or type a number) and press **Enter**.
- Avoid repeatedly clicking the value box unless it lost focus.

## Quick brightness/contrast tweak
1. Go to **Colors > Brightness-Contrast…**
2. Adjust **Brightness**/**Contrast** (drag slider, or use the numeric box + **↑/↓**, or type a number + **Enter**).
3. Click **OK**.

## Quick “more vibrant” tweak (saturation)
1. Go to **Colors > Hue-Saturation…**
2. Ensure **Master** is selected.
3. Raise **Saturation** (drag slider, then fine-tune in the numeric box; keep **Preview** on to avoid overdoing it).
4. Click **OK**.

## Save vs Export (XCF vs PNG/JPG)
- **File > Save / Save As…** saves the editable project as **.xcf**.
- To write a viewable image like **.png/.jpg**, use **File > Export As…** (**Ctrl+Shift+E**).

## Export a separate copy with a new name/location (don’t overwrite)
1. Use **File > Export As…** (shortcut **Ctrl+Shift+E**).
2. In the export dialog:
   - Pick the target folder (e.g., **Desktop** in the left sidebar). If you don’t see it, browse to **Home** → **Desktop**.
   - Enter the **exact new filename**, including extension (e.g., `export.png` or `export.jpg`) to force the format.
3. Click **Export**.
4. If a format options dialog appears (e.g., **“Export Image as JPEG/PNG”**), click **Export** again to confirm.

### If you need transparency
- Export as **PNG** (JPEG can’t preserve transparency).
- If transparency exports as a solid background, ensure the layer has an alpha channel: **Layer > Transparency > Add Alpha Channel** (grayed out = already has one).

Tip: In many Linux file chooser dialogs you can press **Ctrl+L** to type a path like `~/Desktop` directly.