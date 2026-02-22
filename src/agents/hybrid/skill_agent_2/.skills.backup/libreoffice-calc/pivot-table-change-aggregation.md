---
annotations: []
description: 'Edit Pivot Table Layout: remove fields and change aggregation (Sum/Count/etc.)'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 2
name: pivot-table-change-aggregation
---

## Open the Pivot Table Layout dialog
- Existing pivot: click inside it → **Data > Pivot Table > Edit…**
- New pivot: **Data > Pivot Table > Insert or Edit…**

## Change a data field’s aggregation (e.g., Sum → Count)
1. In **Pivot Table Layout**, under **Data Fields**, find the entry (often like **“Sum - <field>”**).
2. **Double-click** the Data Field entry.
3. In **Data Field** dialog, set **Function** (e.g., **Count**, **Sum**, **Average**).
4. Click **OK**, then **OK** again to refresh.

## Remove an unwanted field (Row/Column/Data)
1. In **Pivot Table Layout**, locate the unwanted item under **Row Fields**, **Column Fields**, or **Data Fields** (a stray placeholder like **“Data”** can appear).
2. **Drag** the item back into **Available Fields** (right-side list) to remove it.
   - If drag-and-drop is finicky, drag by the label and pause briefly over the target list before releasing.
3. Click **OK** (and **OK** again if prompted) to refresh.