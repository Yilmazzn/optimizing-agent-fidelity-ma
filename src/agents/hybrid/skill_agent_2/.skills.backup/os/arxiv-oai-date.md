---
annotations: []
description: 'Get arXiv papers by date: monthly /list URLs or daily via OAI-PMH API'
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: arxiv-oai-date
---

When you need arXiv listings for a specific **month** (browse/scrape) or a specific **day** (robust retrieval), use one of the methods below.

## Case 1: Monthly category listing URL (browse/scrape)
- Format: `https://arxiv.org/list/<category>/<YYYY-MM>`
  - Example: `https://arxiv.org/list/cs.CL/2023-10`
- Control entries per page: append `?show=N`
  - Example: `https://arxiv.org/list/cs.CL/2023-10?show=200`

Note: Avoid the older month-code format (e.g. `/list/cs.CL/2310`) which may 404.

## Case 2: Specific day via OAI-PMH (avoids brittle HTML /list pages)
1. Endpoint: `https://export.arxiv.org/oai2`
2. Call `ListRecords` with an inclusive date range:
   - `?verb=ListRecords&metadataPrefix=arXiv&from=YYYY-MM-DD&until=YYYY-MM-DD`
   - Optional category filter: add `&set=<setSpec>`.

Example:
`https://export.arxiv.org/oai2?verb=ListRecords&metadataPrefix=arXiv&from=2023-10-31&until=2023-10-31`

### Pagination (resumptionToken)
- If the response includes `<resumptionToken>...</resumptionToken>`, keep fetching until it’s empty.
- OAI-PMH rule: when using a resumptionToken, call **only**:
  `?verb=ListRecords&resumptionToken=TOKEN` (omit `from/until/metadataPrefix/set`).

### Which date to treat as “announced on”
- Use each record’s `header/datestamp` as the day it was exposed via OAI-PMH.
- Don’t rely on `arxiv:created` for “daily” grouping.

### Discovering category setSpecs
1. Query: `https://export.arxiv.org/oai2?verb=ListSets`.
2. Use returned `<setSpec>` values as `set=` (don’t guess/hardcode).