---
annotations: []
description: 'Writer tab stops: Tabs dialog requires New/Set; insert tabs (keyboard,
  Ctrl+Tab, regex)'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: tab-stops-and-inserting-tabs
---

## Create a right-aligned tab stop (reliable)
1. Select the target paragraphs (**or** edit the paragraph style).
2. Go to **Format ▸ Paragraph… ▸ Tabs**.
3. In **Position**, type the tab stop location (near the right margin).
4. Under **Type**, choose **Right** (optionally set **Fill character**).
5. Click **New** (sometimes labeled **Set**) to add it to the list.
   - If you *only* type a Position and click OK, the tab stop is **not** created.
6. Click **OK**.

## Use it for “left text … right text” on one line
1. Put the cursor where the split should occur.
2. Ensure there is **no extra space** before the tab (delete it if needed).
3. Press **Tab** → the text after the tab snaps to the right-aligned tab stop.

## Fast per-line method: insert tab after the Nth word (no regex)
Use when each line has (at least) N words and you want the same split point repeatedly.

For each line (example: after the **3rd** word):
1. **Home** (go to start of line).
2. **Ctrl+Right** ×3 (caret lands at start of word 4).
3. **Backspace** (deletes the space before word 4).
   - If there are multiple spaces, press Backspace until the words touch.
4. Press **Tab**.

## Insert tabs via Find & Replace (Ctrl+H)
- Don’t press **Tab** inside the Find/Replace dialog fields: it typically moves focus.
- Use one of these instead:
  - Type **`\t`** in the Find/Replace text when **Regular expressions** is enabled (works in many LO versions for matching/inserting a tab).
  - Or insert a *literal* tab into a field with **Ctrl+Tab**.

### Example: insert a tab after the 3rd space-delimited “word” (test on a small selection)
1. **Ctrl+H** → expand options → check **Regular expressions**.
2. **Find:** `^(([^ ]+ +){3})(.*)$`
3. **Replace:** `$1\t$3`  (or `$1` then a literal tab via **Ctrl+Tab**, then `$3`)
4. Run on a selection first; then run on the full document/style range if the preview looks right.