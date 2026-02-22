---
annotations: []
description: Install a VS Code extension via Extensions view (Ctrl+Shift+X) and verify
  publisher
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 1
  times_followed: 1.0
  times_requested: 1
name: vscode-install-extension
---

## Install an extension (Marketplace)
1. In VS Code, open the **Extensions** view: **Ctrl+Shift+X**.
2. In **Search Extensions in Marketplace**, type the extension name (e.g., `Python`).
3. Select the result and **verify the publisher** in the details pane (e.g., **Microsoft**) before installing.
4. Click **Install**.
   - The button may appear **in the list item** and/or **in the extension’s details pane**. If selecting the list item doesn’t start install, click **Install** in the details pane.
5. Wait for the state to change to **Installed** / **Disable** (installation can take a moment).