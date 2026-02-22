---
annotations: []
description: Convert a GIMP image to palette-based (Indexed) color mode (GIF/limited
  colors)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: indexed-color-mode
---

## Convert to palette-based (Indexed)
1. Go to **Image > Mode > Indexed…**
2. In **Indexed Color Conversion**:
   - Choose **Generate optimum palette** (common default) and set **Maximum number of colors** as needed, **or** select a specific/custom palette.
   - Adjust **Dithering** options if banding is visible.
3. Click **Convert**.

## Switch back to full color
- Go to **Image > Mode > RGB**.