---
annotations: []
description: Move a text/layer over an image without accidentally selecting the background
  layer
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: move-active-layer
---

## Reposition a top layer when clicks keep selecting the wrong layer
1. In the **Layers** panel, click the layer you intend to move (e.g., the **text** layer) so it’s the **active** layer.
2. Press **M** to switch to the **Move** tool.
3. In **Tool Options**, set **Move** to **Move the active layer** (avoid **Pick a layer or guide**).
4. Drag on the canvas to reposition the layer.

## If you still keep “grabbing” the wrong thing
- Temporarily **hide** the underlying image layer (eye icon) while positioning.
- Or **lock** the underlying layer’s **position/size** (Layers dock lock icons) so it can’t be moved.

Note: **Pick a layer or guide** changes the active layer based on the topmost visible pixel under the cursor, which is why background/image layers get selected unexpectedly.