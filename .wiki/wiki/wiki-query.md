---
concept: wiki-query
source: plugin-code
source_file: obsidian-wiki-engine/commands/wiki-query.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.641047+00:00
cluster: progressive
content_hash: ca62640056ccbde8
---

# /wiki-query

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: "Progressive-disclosure query against the Obsidian LLM wiki. Returns RLM summary by default, expands to bullets or full node on request."
argument-hint: "<search term> [--level summary|bullets|full|raw] [--source <name>] [--json] [--list]"
allowed-tools: Bash, Read, Write
---

# /wiki-query

Progressive-disclosure query against the LLM wiki knowledge graph.

## Usage

```bash
# Quick summary (default)
/wiki-query "authentication flow"

# Bullet-level detail
/wiki-query "authentication flow" --level bullets

# Full wiki node
/wiki-query "api design" --level full

# List all indexed concepts
/wiki-query --list

# Search within one source only
/wiki-query "Oracle Forms" --source arch-docs

# Machine-readable JSON output
/wiki-query "Oracle Forms" --json
```

## Progressive Disclosure Levels

| Level | Content | Approximate Tokens |
|:------|:--------|:-------------------|
| `summary` | 1-5 sentence distilled answer (default) | ~50 |
| `bullets` | 6-10 key idea bullets | ~150 |
| `full` | Complete wiki node + wikilinks | ~800 |
| `raw` | Original source file content | variable |

## Search Strategy

1. Exact concept name match in `wiki/_index.md`
2. Fuzzy label match across all concept nodes
3. Full-text keyword scan of `wiki/*.md` summaries
4. Falls back to `rlm/` summary layer if wiki node is missing

## Under the Hood

```bash
python ./scripts/query_wiki.py --wiki-root {wiki_root} [options] "<term>"
```


## See Also

- [[obsidian-wiki-engine-plugin]]
- [[wiki-audit]]
- [[wiki-build]]
- [[wiki-distill]]
- [[wiki-ingest]]
- [[wiki-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/commands/wiki-query.md`
- **Indexed:** 2026-04-17T06:42:09.641047+00:00
