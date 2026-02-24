---
description: "Ingest repository files into the local ChromaDB vector store for semantic search"
---

# /vector-db:ingest

Build or update the semantic memory by chunking files, injecting RLM context, and embedding into ChromaDB.

## Prerequisites
- ChromaDB and sentence-transformers installed (`pip install -r requirements.txt`)
- Optional: RLM cache (`rlm_summary_cache.json`) for Super-RAG context injection

## Usage

### Full Rebuild (First time or major changes)
```bash
python3 plugins/vector-db/scripts/ingest.py --full
```

### Incremental Update (Last 24 hours)
```bash
python3 plugins/vector-db/scripts/ingest.py --since 24
```

## Steps
1. Verify Python deps are installed.
2. Check if `.env` has `VECTOR_DB_PATH` configured.
3. Run the ingest command.
4. Verify with `python3 plugins/vector-db/scripts/query.py --stats`.

## Notes
- Full rebuild can take 5+ minutes on large repos.
- Chroma is single-writer — do NOT run two ingestions simultaneously.
