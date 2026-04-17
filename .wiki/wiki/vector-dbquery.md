---
concept: vector-dbquery
source: plugin-code
source_file: vector-db/commands/query.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.425507+00:00
cluster: search
content_hash: ab7dcd681539442f
---

# /vector-db:query

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Search the vector database for semantically relevant code and documentation
argument-hint: "\"search query\" [--profile knowledge] [--limit N] [--stats]"
---

# /vector-db:query

Semantic (meaning-based) search against the ChromaDB vector store.

> **For constraints and Source Transparency rules, see skill:** [`vector-db-search`](../skills/vector-db-search/SKILL.md)

## Quick Reference

```bash
# Semantic search
python3 ./scripts/query.py \
  "your natural language question" --profile wiki--limit 5

# Check DB stats / health
python3 ./scripts/query.py --profile wiki--stats
```

Results are ranked by cosine similarity and include file path, chunk content, and score.
If results are poor or empty, run `/vector-db:ingest` to rebuild the index.


## See Also

- [[vector-consistency-stabilizer]]
- [[code-file-vector-consistency-checkpy]]
- [[vector-consistency-stabilizer]]
- [[code-file-vector-consistency-checkpy]]
- [[vector-db-initialization]]
- [[acceptance-criteria-vector-db-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/commands/query.md`
- **Indexed:** 2026-04-17T06:42:10.425507+00:00
