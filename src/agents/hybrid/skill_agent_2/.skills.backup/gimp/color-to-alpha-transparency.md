---
annotations: []
description: Remove a solid/near-solid background using Color to Alpha (transparent
  PNG)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: color-to-alpha-transparency
---

## Make a single-color background transparent (Color to Alpha)
1. Ensure the layer supports transparency: **Layer > Transparency > Add Alpha Channel** (if grayed out, it already has one).
2. Run **Color to Alpha…** (usually **Colors > Color to Alpha…**; in some menus also **Layer > Transparency > Color to Alpha…**).
3. In the dialog, click the **eyedropper** next to **Color**, then click the background color on the canvas to sample it.
4. Adjust settings if needed (keep **Preview** on), then click **OK**.

## Export with transparency
1. Use **File > Export As…** (shortcut **Ctrl+Shift+E**).
2. Choose a format that supports alpha (typically **.png**), then **Export** (and confirm any format options dialog).