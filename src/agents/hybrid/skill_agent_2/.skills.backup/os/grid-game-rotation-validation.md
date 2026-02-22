---
annotations: []
description: Validate falling-block rotations (wall kicks) + bounds-safe freeze/lock
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: grid-game-rotation-validation
---

## Rotation input: keep state valid
1. Save the old pose before changing anything (at least `rotation`; often `x,y` too).
2. Apply the rotation.
3. Validate with the same collision/bounds check you use for movement.
4. If invalid:
   - **Revert** to the old pose, **or**
   - Try simple **wall kicks** (common minimal set): `dx = [0, -1, +1, -2, +2]` and accept the first pose that passes validation.

### Pseudocode
```python
old_rot, old_x, old_y = rot, x, y
rot = (rot + 1) % 4
for dx in (0, -1, 1, -2, 2):
    x = old_x + dx
    if not intersect(x, y, rot):
        break
else:
    rot, x, y = old_rot, old_x, old_y
```

## Safety net: make lock/freeze bounds-safe
Even if `intersect()` is bounds-safe via short-circuit logic, later code that writes into the board may assume indices are valid.

When freezing a piece into the board, guard the write:
```python
for (px, py) in cells_of_piece(x, y, rot):
    if 0 <= px < W and 0 <= py < H:
        board[py][px] = color
```

## Pitfall
Allowing an out-of-bounds/intersecting rotation can lurk until the next “lock” step, where an `IndexError`/crash occurs.