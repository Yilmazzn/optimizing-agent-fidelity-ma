---
annotations: []
description: Export (even unsaved) Impress slides to PNG via File > Export
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: export-slides-to-png
---

## Export slides to PNG
1. In Impress, go to **File > Export…** (not *Save As*).
2. Choose the destination folder.
3. Enter a base **File name** (optionally include `.png`).
4. In **File type/Format** (bottom dropdown), select **PNG - Portable Network Graphics (.png)**.
5. Click **Save**.
6. In the follow-up **PNG Options** dialog, set options (or keep defaults) and click **OK**.

Notes:
- If you only type a `.png` extension but don’t change **File type**, it may export in the wrong format.
- With multiple slides, Impress typically exports **one PNG per slide** (files get numbered) into the chosen folder.

## If the presentation is unsaved / "Untitled"
- You can still export from the open document using **File > Export…**; you don’t need an `.odp/.pptx` saved on disk first.
- If you planned to do a *headless* conversion (CLI) or were searching for a file to convert, save the deck first (**File > Save As…**) or export to images instead.