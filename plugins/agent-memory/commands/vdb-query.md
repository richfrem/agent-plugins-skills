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
python ./scripts/query.py \
  "your natural language question" --profile wiki--limit 5

# Check DB stats / health
python ./scripts/query.py --profile wiki--stats
```

Results are ranked by cosine similarity and include file path, chunk content, and score.
If results are poor or empty, run `/vector-db:ingest` to rebuild the index.
