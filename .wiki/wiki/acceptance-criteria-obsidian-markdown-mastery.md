---
concept: acceptance-criteria-obsidian-markdown-mastery
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/obsidian-markdown-mastery/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.129962+00:00
cluster: links
content_hash: 282dde200fb38007
---

# Acceptance Criteria: Obsidian Markdown Mastery

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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


## See Also

- [[acceptance-criteria-markdown-to-word-converter]]
- [[acceptance-criteria-obsidian-bases-manager]]
- [[acceptance-criteria-obsidian-canvas-architect]]
- [[acceptance-criteria-obsidian-graph-traversal]]
- [[acceptance-criteria-obsidian-init]]
- [[obsidian-markdown-mastery-protocol-129-compliant]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/obsidian-markdown-mastery/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.129962+00:00
