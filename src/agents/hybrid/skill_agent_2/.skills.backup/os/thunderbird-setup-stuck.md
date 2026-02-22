---
annotations: []
description: 'Thunderbird setup stuck on validating: Manual/Advanced config + Normal
  password workaround'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: thunderbird-setup-stuck
---

## Case 1: “Done” stuck on validating (often Outlook/Office365 OAuth2)
1. In **Set Up Your Existing Email Address**, enter **Name / Email / Password**.
2. If **Done** spins on “validating settings”, click **Configure manually**.
3. Set **Authentication method** to **Normal password** for both:
   - **Incoming** (IMAP/POP)
   - **Outgoing** (SMTP)
4. Click **Done** again to force creation of the account.

## Case 2: Wizard won’t finish but you need full Account Settings
1. In the setup wizard’s **Manual config** / server-details screen, click **Advanced config**.
2. Confirm **OK**.
3. Thunderbird opens **Account Settings** for the new account—finish configuration under:
   - **Server Settings** (incoming)
   - **Outgoing Server (SMTP)**

## After the account exists (adjust auth later)
1. **Menu ≡ → Account Settings**.
2. Incoming: **Server Settings → Authentication method**.
3. Outgoing: **Outgoing Server (SMTP) → Edit… → Authentication method**.

Note: This is a workaround to *create the account*. Connection/auth errors may still require correct server settings and credentials.