---
annotations: []
description: Extract emails from homepage URLs via curl+grep (mailto, plain, [at]/[dot]
  obfuscation)
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: scrape-emails-from-webpages
---

## Case 1: Grab `mailto:` links
```bash
curl -Ls "URL" | grep -Eoi 'mailto:[^"\x27 >]+'
```

## Case 2: Find plain emails in page text/HTML
```bash
curl -Ls "URL" | grep -Eoi '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}'
```

## Case 3: Find common obfuscations like `[AT]` / `(at)` / ` at ` and `[dot]` / `(dot)`
```bash
curl -Ls "URL" | grep -Eoi '[A-Z0-9._%+-]+\s*(\[at\]|\(at\)| at )\s*[A-Z0-9.-]+\s*(\[dot\]|\(dot\)|\.)\s*[A-Z]{2,}'
```
Then manually normalize, e.g. `name [AT] domain [dot] edu` → `name@domain.edu`.

## Notes / pitfalls
- Use `-L` to follow redirects; `-s` to keep output clean.
- If a site renders the email via JavaScript, the HTML fetch may not contain it; try viewing page source in browser or use a headless browser tool instead.