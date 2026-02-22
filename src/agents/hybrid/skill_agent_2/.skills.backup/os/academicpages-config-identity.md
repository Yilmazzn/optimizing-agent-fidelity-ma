---
annotations: []
description: Update academicpages/Jekyll identity fields in _config.yml (title, YAML
  &name, author)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: academicpages-config-identity
---

When changing the displayed name/email in the **academicpages** Jekyll template, `_config.yml` typically defines identity in *multiple places*.

## Update the top-level site settings (YAML anchor)
1. Open `_config.yml`.
2. In “Basic Site Settings”, update both:
   - `title: "..."`
   - `name: &name "..."`
3. **Keep `&name` intact** (it’s a YAML anchor referenced elsewhere). Only change the quoted value.

## Update the sidebar/contact info (author block)
1. Find the `author:` section.
2. Update:
   - `author.name` (line usually `  name: "..."` under `author:`)
   - `author.email`

## Quick verification (avoid partial edits)
```bash
grep -nE '^(title|name)\s*:|^author:|^  (name|email)\s*:' _config.yml
```
Review matches for old values before committing/pushing.