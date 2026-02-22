---
annotations: []
description: Generate APA (or other styles) citations from a DOI via curl Accept header
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: doi-content-negotiation
---

## Case 1: One DOI → APA citation (terminal)
Use DOI “content negotiation” against `https://doi.org/<DOI>`.

```bash
curl -sL -H "Accept: text/x-bibliography; style=apa; locale=en-US" \
  "https://doi.org/10.xxxx/xxxxx"
```

Notes:
- `-L` matters (doi.org redirects to the resolver target).
- Change `style=` to any CSL style name (e.g., `harvard1`, `chicago-author-date`).

## Case 2: Bulk-check a list of DOIs
```bash
while read -r doi; do
  [ -z "$doi" ] && continue
  printf "\n%s\n" "$doi"
  curl -sL -H "Accept: text/x-bibliography; style=apa; locale=en-US" "https://doi.org/$doi"
done < dois.txt
```

## Case 3: Prefer structured metadata (programmatic)
```bash
curl -sL -H "Accept: application/vnd.citationstyles.csl+json" "https://doi.org/10.xxxx/xxxxx"
```

Use the returned citation/metadata as a baseline to compare against your document (author list, year, title capitalization, journal, volume/issue/pages, DOI).