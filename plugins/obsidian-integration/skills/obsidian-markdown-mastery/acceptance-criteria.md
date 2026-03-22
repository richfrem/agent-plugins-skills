# Acceptance Criteria: Obsidian Markdown Mastery

## 1. Link Formatting
- [ ] Intra-vault links use `[[Note Name]]` syntax, never standard markdown `[text](path)`.
- [ ] Embeds use `![[Note Name]]` (with leading `!`), categorized separately from semantic links.
- [ ] Aliased links use `[[Note Name|Display Text]]` format.

## 2. Deterministic Parsing
- [ ] All link/embed extraction uses `parser.py` — no ad-hoc regex.
- [ ] Parser correctly distinguishes: standard links, heading links (`#`), block links (`#^`), embeds.

## 3. Callout Compliance
- [ ] Callouts use only supported types: `info`, `warning`, `error`, `success`, `note`.
- [ ] Unsupported types are flagged, not silently coerced.
