# Obsidian Wiki Query Guide

## Contents
- [Progressive Disclosure Levels](#progressive-disclosure-levels)
- [3-Phase Search Strategy](#3-phase-search-strategy)
- [Output Filing Loop (--save-as)](#output-filing-loop---save-as)
- [Command Options & Profiles](#command-options--profiles)

---

## Progressive Disclosure Levels

| Level | Content | Target Cost |
|:------|:--------|:------------|
| `summary` | 1-5 sentence distilled answer | ~50 tokens |
| `bullets` | 6-10 key idea bullets | ~150 tokens |
| `full` | Complete wiki node + wikilinks | ~800 tokens |
| `raw` | Original source file content | Variable |

---

## 3-Phase Search Strategy

1. **Phase 1 — Slug & Token Match (O(1), Always Active):**
   - Exact concept slug matching.
   - Substring and prefix resolution on concept titles.
   - Word token overlap matching (e.g. `auth` matches `authentication-flow`).

2. **Phase 2 — Vector DB Semantic Search (O(log N)):**
   - Invokes `vector-db` query engine subprocess when available.
   - Resolves profiles via `.agent/learning/vector_profiles.json` (default: `wiki`).
   - Maps semantic embeddings back to concept slugs via `meta/agent-memory.json`.

3. **Phase 3 — Full-Text Keyword Scan (O(N), Fallback):**
   - Scans markdown node contents in `wiki/*.md` for matching terms.

---

## Output Filing Loop (--save-as)

Karpathy's observation: *"Outputs always add back into the wiki."*

Using `--save-as <slug>` writes the query result as a new concept node:
- Adds YAML frontmatter with `query_derived: true` and `derived_from` attribution.
- Retains query output at requested disclosure level.
- Automatically inserts `## See Also` backlink to source concepts.

---

## Command Options & Profiles

```bash
# Query with specific level
python ./scripts/query_wiki.py --wiki-root <path> "concept" --level bullets

# Save query back into wiki
python ./scripts/query_wiki.py --wiki-root <path> "topic" --level full --save-as derived-topic

# Query with custom vector profile
python ./scripts/query_wiki.py --wiki-root <path> "query" --vdb-profile research

# Machine-readable JSON output
python ./scripts/query_wiki.py --wiki-root <path> "query" --json
```
