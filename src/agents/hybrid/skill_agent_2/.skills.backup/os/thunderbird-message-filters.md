---
annotations: []
description: Create Thunderbird Message Filters to move incoming mail (e.g., to Local
  Folders)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: thunderbird-message-filters
---

## Create a Local Folder destination
1. In the left folder pane, right-click **Local Folders** → **New Folder…**
2. Name the folder (e.g., `Promotions`) → **Create/OK**.

## Open the Message Filters window (entry points)
(Varies by Thunderbird version/layout)
- **Tools → Message Filters…**
- Application menu **≡ → Tools → Message Filters…**
- If present, click **Manage message filters** in the main toolbar.

## Create a filter that moves mail by subject keyword
1. In **Message Filters**, choose the target account in the top dropdown.
   - To file into Local Folders, select **Local Folders** here.
2. Click **New…**.
3. Under **Apply filter when**, enable the incoming-mail option (e.g., **Getting New Mail**).
4. Condition: **Subject** + **contains** + `<keyword>`.
5. Action: **Move Message to** → pick **Local Folders → <folder>**.
6. **OK** to save the filter; close the Message Filters window.