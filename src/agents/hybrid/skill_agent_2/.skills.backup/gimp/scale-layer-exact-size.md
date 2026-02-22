---
annotations: []
description: Scale a single GIMP layer to an exact pixel size (Layer > Scale Layer),
  with/without aspect lock
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: scale-layer-exact-size
---

## Scale one layer to an exact size (preserve aspect ratio)
1. In the **Layers** dock, click the target layer so it’s **active** (highlighted).
2. Open **Layer → Scale Layer…** (not **Image → Scale Image…**).
3. In the dialog, make sure units are **px**.
4. Ensure the **chain/link icon** between **Width** and **Height** is **linked** (aspect ratio locked).
5. Click the field you want to control (e.g., **Height**), type the exact value (e.g., `512`).
6. **Click `Scale`** to apply (don’t rely on Enter alone if it doesn’t submit the dialog).

## If the chain/link isn’t locked (manual aspect preservation)
1. Note the original size (shown in the dialog).
2. Compute the missing dimension:
   - `new_width = round(old_width * new_height / old_height)` (or the inverse)
3. Enter **both** Width and Height, then click **Scale**.

### Pitfall
If you accidentally hit **Cancel**/close the dialog, no scaling is applied—reopen **Layer → Scale Layer…** and confirm with **Scale**.