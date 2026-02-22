---
annotations: []
description: Count attachments in raw RFC822 email by walking MIME parts (Python)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: email-attachment-count
---

When deriving a `number_of_attachments` from a raw email, don’t rely on a single header—real mail varies.

## Procedure (Python `email`)
1. Parse message to a `Message/EmailMessage`.
2. If multipart, iterate parts with `msg.walk()`.
3. Skip container parts: `if part.is_multipart(): continue`.
4. Count a part as an attachment if **either**:
   - `part.get_content_disposition() == 'attachment'`, **or**
   - `part.get_filename() is not None` (catches many real-world attachments).

```python
count = 0
for part in msg.walk():
    if part.is_multipart():
        continue
    if part.get_content_disposition() == 'attachment' or part.get_filename() is not None:
        count += 1
```

Note: This may also count some “inline” parts that still have a filename; tighten the condition if you explicitly want to exclude inline images/signatures.