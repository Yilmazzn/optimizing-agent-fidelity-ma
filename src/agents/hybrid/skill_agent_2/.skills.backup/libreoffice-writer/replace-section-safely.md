---
annotations: []
description: Insert/paste/replace content under a Writer heading safely
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: replace-section-safely
---

## Jump to the right heading fast
- Open **Navigator**: **F5** → in **Headings**, click the target heading.
- If headings aren’t real styles: **Ctrl+F** → search the heading text → **Enter/F3** next match (**Shift+F3** previous).

## Case 1: Insert/paste under a heading without extending the heading style
1. **Don’t press Enter while the caret is inside the heading paragraph** (it can split the heading and keep heading formatting).
2. Click the **body paragraph below the heading** (or press **↓** to move to the next paragraph).
3. Verify you’re in body text: the left side of the **status bar** should show a body style (e.g., **Text Body**), not *Heading 1/2/etc.*
4. Insert/paste.

### If there is no paragraph below the heading
1. Put the caret at the end of the heading and press **Enter** to create the next paragraph.
2. If the new line is still a heading, switch it to body style: **Ctrl+0** (Text Body) or **F11** → Styles → double‑click **Text Body**.

## Case 2: Replace a whole section’s contents without deleting what follows
1. Jump to the section start (Navigator **F5** → click the heading).
2. Click **at the start of the first paragraph that belongs to the section** (often the first entry, not the heading).
3. Find the end of the section:
   - If there is another heading after it: in Navigator, click the **next heading** and set your end point **just before that heading**.
   - If the section is truly last: verify (scroll/Navigator) that nothing important follows.
4. Select the range:
   - **Shift+click** at the end point, or
   - click‑drag from the first entry down to the last entry.
5. Delete/replace the selected block, then paste the new text.

### Only use Ctrl+Shift+End after verifying nothing follows
- **Ctrl+Shift+End** selects from the caret to the **document end**.

### After paste, reapply formatting if needed
- Select the pasted block and apply paragraph formatting via **Format ▸ Paragraph…** (e.g., hanging indent, double spacing).

## If you accidentally modified the heading or selection
- **Ctrl+Z**, reposition the caret/selection, try again.