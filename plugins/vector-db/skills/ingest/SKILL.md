---
description: Ingest repository files into the local ChromaDB vector store for semantic search
argument-hint: "[--profile knowledge] [--full] [--since N]"
---

# /vector-db:ingest

Build or update the vector index by chunking files and embedding them into ChromaDB.

> **For detailed execution protocol, see agent:** [`vdb-ingest`](../agents/vdb-ingest.md)

## Quick Reference

```bash
# Full rebuild (first time or major changes)
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py --profile knowledge --full

# Incremental update (files changed in last 24 hours)
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py --profile knowledge --since 24

# Code files with AST parsing
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py --profile knowledge --full --code
```

**Requires ChromaDB server running.** See `/vector-db:launch` if not up.
ChromaDB is single-writer -- do not run two ingestions simultaneously.
