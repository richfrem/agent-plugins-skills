---
description: Search the vector database for semantically relevant code and documentation
argument-hint: "\"search query\" [--profile knowledge] [--limit N]"
---

# /vector-db:query

Semantic (meaning-based) search against the ChromaDB vector store.

> **For constraints and Source Transparency rules, see skill:** [`vector-db-search`](../skills/vector-db-search/SKILL.md)

## Quick Reference

```bash
# Semantic search
python ./scripts/query.py \
  "your natural language question" --profile wiki --limit 5

# Increase result count
python ./scripts/query.py "your question" --profile wiki --limit 10
```

Results are ranked by cosine similarity and include file path, chunk content, and score.
If results are poor or empty, run `/vector-db:ingest` to rebuild the index.
