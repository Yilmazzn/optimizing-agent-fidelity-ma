---
annotations: []
description: 'Writer paragraph formatting: align, spacing, hanging indent (APA refs)'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: paragraph-alignment-shortcuts
---

## Select full paragraph(s) precisely (keyboard)
1. Click inside the paragraph.
2. Select to paragraph end: **Ctrl+Shift+Down**.
   - Repeat **Ctrl+Shift+Down** to extend to more paragraphs.
3. If you need an exact selection starting at the paragraph start: **Ctrl+Shift+Up** (to start) then **Ctrl+Shift+Down**.

Whole document: **Ctrl+A**.

## Alignment shortcuts
Place the caret in the paragraph (or select multiple) then:
- Left: **Ctrl+L**
- Center: **Ctrl+E**
- Right: **Ctrl+R**
- Justify: **Ctrl+J**

Menu fallback: **Format ▸ Paragraph… ▸ Alignment**.

## Line spacing (reliable)
1. Select the paragraphs (or **Ctrl+A**).
2. **Format ▸ Paragraph… ▸ Indents & Spacing**.
3. Set **Line spacing** (e.g., **Double**) → **OK**.

Shortcut pitfall: **Ctrl+2** applies only to the current paragraph/selection; if selection is wrong/empty, results are unexpected—use the Paragraph dialog when you need a dependable setting.

## Hanging indent (e.g., APA References list)
1. Select **only the reference paragraphs** (exclude the “References” heading).
2. **Format ▸ Paragraph… ▸ Indents & Spacing**.
3. Set:
   - **Before text**: `0.5 in` (`1.27 cm`)
   - **First line**: `-0.5 in` (`-1.27 cm`)
   - (You can type `0.5in` even if your doc uses cm; Writer converts.)
4. If needed, set **Line spacing** to **Double**.
5. If required, set **Spacing** **Above** = `0` and **Below** = `0` to avoid extra gaps.

**Pitfall:** Don’t use **Page Style** for this—hanging indent is paragraph-level (Indent & Spacing).