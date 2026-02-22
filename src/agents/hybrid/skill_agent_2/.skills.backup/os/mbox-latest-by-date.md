---
annotations: []
description: Pick the latest N messages from an mbox by sorting on the Date header
  (not file order)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: mbox-latest-by-date
---

When you need “latest N” emails in correct chronological order (e.g., for a report), don’t trust mbox storage order.

## Procedure (Python)
1. Parse each message’s `Date` header:
   - `dt = email.utils.parsedate_to_datetime(msg.get('Date',''))`
2. If missing/unparseable, assign an old default so it won’t appear as “latest”:
   - `dt = datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)`
3. Sort **descending** by `dt` to pick the latest `N`.
4. Re-sort those `N` **ascending** by `dt` for output (earliest → most recent).

## Minimal snippet
```python
import mailbox, datetime
from email.utils import parsedate_to_datetime

EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

def msg_dt(m):
    try:
        return parsedate_to_datetime(m.get('Date','')) or EPOCH
    except Exception:
        return EPOCH

msgs = list(mailbox.mbox('Inbox'))
latest = sorted(msgs, key=msg_dt, reverse=True)[:5]
latest = sorted(latest, key=msg_dt)
```