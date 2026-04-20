---
concept: vector-dbingest
source: plugin-code
source_file: vector-db/commands/ingest.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.424076+00:00
cluster: chromadb
content_hash: 026d7673aa8e7a33
---

# /vector-db:ingest

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: Ingest repository files into the local ChromaDB vector store for semantic search
argument-hint: "[--profile knowledge] [--full] [--since N]"
---

# /vector-db:ingest

Build or update the vector index by chunking files and embedding them into ChromaDB.

> **For detailed execution protocol, see agent:** `vector-db-ingest`

## Quick Reference

```bash
# Full rebuild (first time or major changes)
python ./scripts/ingest.py --profile wiki--full

# Incremental update (files changed in last 24 hours)
python ./scripts/ingest.py --profile wiki--since 24

# Code files with AST parsing
python ./scripts/ingest.py --profile wiki--full --code
```

**Requires ChromaDB server running.** See `/vector-db:launch` if not up.
ChromaDB is single-writer -- do not run two ingestions simultaneously.


## See Also

- [[vector-consistency-stabilizer]]
- [[code-file-vector-consistency-checkpy]]
- [[vector-consistency-stabilizer]]
- [[code-file-vector-consistency-checkpy]]
- [[vector-db-initialization]]
- [[acceptance-criteria-vector-db-init]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/commands/ingest.md`
- **Indexed:** 2026-04-17T06:42:10.424076+00:00
