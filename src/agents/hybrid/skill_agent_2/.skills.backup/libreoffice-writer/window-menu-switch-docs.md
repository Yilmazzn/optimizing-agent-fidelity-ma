---
annotations: []
description: Switch between multiple open Writer documents via Window menu (deterministic)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: window-menu-switch-docs
---

When Alt+Tab is unreliable (file dialogs, multiple LibreOffice windows), switch documents from inside Writer.

## Switch to a specific open document
1. In the target Writer window, open **Window** on the top menu.
2. Click the exact document entry by title (e.g., **“Answer.docx — LibreOffice Writer”**).
3. Repeat **Window ▸ <document>** to jump between source/target documents.

## Notes / pitfalls
- The **Window** menu lists documents open in the *current LibreOffice window/instance*; if you opened separate instances, use the Window menu in the instance that owns the document.