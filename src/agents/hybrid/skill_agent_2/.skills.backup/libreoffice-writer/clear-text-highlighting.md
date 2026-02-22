---
annotations: []
description: Find/modify text by formatting (Attributes… + Find All), e.g., clear
  highlights
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: clear-text-highlighting
---

## Find text by formatting (not words)
Use this when you *don’t know the exact text*, but you know a formatting property (highlight/background/bold/etc.).

1. Open **Find & Replace**: **Ctrl+H**.
2. Expand options if needed: **More Options / Other options**.
3. Click **Attributes…** and choose the formatting attribute you want to match (varies by version), e.g.:
   - **Character background** / **Character highlighting**
   - other character/paragraph attributes available in the list
4. Click **Find All** (selects every match in the document).
5. Apply the desired change to the selection:
   - Use **Format ▸ Character…** (or **Format ▸ Paragraph…**) and set the attribute to **None / No Fill / default**, or apply new formatting.
6. (Important) Click **No Format** in the Find & Replace dialog to clear the attribute constraints before doing other searches.

## Common case: clear “stuck” highlighting/background
If the toolbar highlighter (**Character Highlighting Color → No Fill**) doesn’t clear it, it’s often **character background/highlighting formatting**.

1. **Ctrl+H** → **Attributes…** → check **Character background** (and/or **Character highlighting**) → **OK**.
2. **Find All**.
3. **Format ▸ Character…** → **Highlighting/Background** tab → set to **None / No Fill** → **OK**.

## Notes / gotchas
- **Find All** selects multiple ranges; a single formatting change applies to all of them.
- If you need to *replace* formatting (not just clear it), set the new formatting via **Format…**/**Attributes…** in the Replace section (version-dependent), or use **Find All** then apply formatting manually.