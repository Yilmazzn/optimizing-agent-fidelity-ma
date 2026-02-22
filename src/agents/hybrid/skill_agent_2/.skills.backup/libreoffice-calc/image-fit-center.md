---
annotations: []
description: Fit an image to page height/width without stretching via Sidebar > Properties
  > Position and Size
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: image-fit-center
---

## Resize to fill page height/width (no stretching)
1. Select the image.
2. Open the Sidebar (**View > Sidebar**) and switch to **Properties**.
3. Expand **Position and Size**.
4. Enable **Keep ratio**.
5. Set **Height** (or **Width**) to the target page size you want to fill.
   - Tip: press **Enter** after typing to commit the value.

## Center / align via X/Y
1. In **Position and Size**, set **Position Y** (e.g., `0` for top-aligned).
2. Adjust **Position X** until centered.
   - If the scaled image is wider than the page, centering may require a **negative X**.
   - If you know page width: `X = (page_width - image_width) / 2`.