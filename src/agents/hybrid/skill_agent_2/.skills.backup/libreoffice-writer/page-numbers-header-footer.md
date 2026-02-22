---
annotations: []
description: Make page numbers repeat on every page (header/footer Page Styles)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: page-numbers-header-footer
---

In Writer, page numbers repeat only if the *field* is placed in a repeating area (header/footer) of the relevant **Page Style**.

## Add page numbers to all pages (common case)
1. Enable the repeating area for the style you’re using: **Insert > Header and Footer > Footer >** *[Page Style]* (often **Default Page Style**).
2. Click inside the footer area.
3. Insert the field at the cursor:
   - **Insert > Page Number** (some versions), or
   - **Insert > Field > Page Number**.

## Quick verification (avoid “only on First Page style” mistakes)
1. Jump between pages: press **Ctrl+G** (Go to Page), type a page number, press **Enter/OK**.
   - If Ctrl+G doesn’t open Go to Page, open the **Navigator** with **F5** and use its page jump controls.
2. Check the footer/header on several pages (e.g., page 1, 2, 10).

## If some pages don’t show the number
- Those pages likely use a *different Page Style* (e.g., **First Page**, **Left Page/Right Page**). You must enable the footer and insert the page number field for each style.

### How to see which Page Style a page uses
- Look at the **status bar** for the current Page Style name, or
- Open **Sidebar > Styles** (or press **F11**) > **Page Styles** and see which style is selected.

### Fix
- Enable footer for that style: **Insert > Header and Footer > Footer >** *[that style]*, then insert the page number field.
- Or open the style: **Format > Page Style… > Footer** tab and enable it.

## Alignment/position tweaks
- Click in the footer paragraph and set alignment via **Format > Paragraph… > Alignment** (or toolbar alignment buttons).