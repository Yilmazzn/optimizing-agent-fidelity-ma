---
annotations: []
description: 'Grid-movement collision fix: spawn items on-grid (multiples of cell
  size)'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: grid-movement-spawn-alignment
---

## When exact coordinate equality collisions “never happen”
Common symptom: player/snake moves in fixed `CELL` steps (grid), but targets/food spawn at arbitrary pixels, so `if head == food_pos:` almost never matches.

## Keep everything on-grid (recommended)
1. Define one cell size (movement step), e.g. `CELL = 20`.
2. Spawn positions using a stepped random range (or choose from precomputed cells):
   ```python
   x = random.randrange(0, WIDTH, CELL)
   y = random.randrange(0, HEIGHT, CELL)
   food = (x, y)
   ```
3. Ensure `WIDTH` and `HEIGHT` are multiples of `CELL` (or clamp to the last full cell).

### Respawning without placing on occupied cells
- Retry until free:
  ```python
  while True:
      food = (random.randrange(0, WIDTH, CELL), random.randrange(0, HEIGHT, CELL))
      if food not in snake_body:
          break
  ```
- Alternative: precompute all grid cells and sample from the free set.

## If you intentionally allow off-grid positions
- Don’t use tuple equality; use area/rectangle collision (e.g., `pygame.Rect(...).colliderect(...)`).

## Pitfall
- Mixing floats (smooth movement) with integer positions makes `==` comparisons fragile; snap/round to grid before equality checks, or use area overlap.