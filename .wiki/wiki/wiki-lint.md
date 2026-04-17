---
concept: wiki-lint
source: plugin-code
source_file: obsidian-wiki-engine/commands/wiki-lint.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.640743+00:00
cluster: semantic
content_hash: 5a8ae263fb0f66c1
---

# /wiki-lint

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: "Run a semantic health check over the LLM wiki. Finds inconsistencies, missing concepts, stale articles, connection candidates, and new article suggestions. Writes meta/lint-report.md."
argument-hint: "[--sample N] [--engine copilot|claude|gemini] [--dry-run]"
---

# /wiki-lint

Semantic health check for the Obsidian LLM wiki. Uses the cheapest available LLM
to analyze wiki quality and surface improvement opportunities.

## Quick Reference

```bash
# Default (auto-detect engine, sample 15 pages)
/wiki-lint

# Sample more pages for larger wikis
/wiki-lint --sample 30

# Force engine
/wiki-lint --engine claude

# Dry run (print prompt without calling LLM)
/wiki-lint --dry-run
```

## What It Checks

| Category | What It Finds |
|:---------|:--------------|
| Inconsistencies | Contradicting claims between articles |
| Missing Concepts | Topics implied but not yet written |
| Stale Articles | Thin or outdated content needing refresh |
| Connection Candidates | Wikilink pairs that should exist |
| New Article Suggestions | Topics the wiki should cover |

## Output

Report written to `{wiki-root}/meta/lint-report.md`.

## When to Run

- After the wiki reaches ~20+ concept nodes
- Weekly maintenance step before a major query session
- After `/wiki-rebuild` to catch any quality drift
- When you notice inconsistencies or gaps in query results

> For **structural** checks (orphans, missing summaries, broken links),
> use `/wiki-audit` instead. `lint` handles semantic quality only.

See `skills/obsidian-wiki-linter/SKILL.md` for the full execution protocol.


## See Also

- [[obsidian-wiki-engine-plugin]]
- [[wiki-audit]]
- [[wiki-build]]
- [[wiki-distill]]
- [[wiki-ingest]]
- [[wiki-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/commands/wiki-lint.md`
- **Indexed:** 2026-04-17T06:42:09.640743+00:00
