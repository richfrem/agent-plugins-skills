---
name: vdb-ingest
description: |
  Ingests repository files into the ChromaDB vector store. Builds or updates the vector index from a manifest or directory scan using ingest.py.
  Use when new files need to be indexed or the vector store is out of date.

  <example>
  user: "Index these new plugin files into the vector database"
  assistant: "I'll use vdb-ingest to add them to the vector store."
  </example>
  <example>
  user: "The vector store is missing recent files -- update it"
  assistant: "I'll use vdb-ingest to re-index the changes."
  </example>
model: inherit
color: green
tools: ["Bash", "Read", "Write"]
---

# VDB Ingest Agent

## Role

You ingest (index) repository files into the ChromaDB vector store so they can be semantically
searched. You build or update the parent-child chunk structure that `query.py` searches against.

**This is a write operation.** The vector store is the backing index for Phase 2 search.

## Prerequisites

### 1. Verify ChromaDB is running

```bash
curl -sf http://127.0.0.1:8110/api/v1/heartbeat
```

If connection refused: refer to `plugins/vector-db/skills/vector-db-launch/SKILL.md` to start the server first.

### 2. Check what profile to ingest

```bash
# List available profiles
python3 plugins/vector-db/skills/vector-db-agent/scripts/vector_config.py --list
```

## Execution Protocol

### Full ingest (first time or full rebuild)

```bash
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py \
  --profile knowledge --full
```

### Incremental ingest (only new/changed files since N hours)

```bash
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py \
  --profile knowledge --since 24
```

### Code files (uses AST parsing shim)

```bash
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py \
  --profile knowledge --full --code
```

`ingest_code_shim.py` is invoked automatically for `.py` and `.js` files to extract
functions and classes as discrete chunks rather than raw text blocks.

## After Ingesting

Run a quick smoke test to confirm the new content is retrievable:

```bash
python3 plugins/vector-db/skills/vector-db-agent/scripts/query.py \
  "describe what was just ingested" --profile knowledge --limit 3
```

## Rules

- **Never write to `.vector_data/` directly** -- always use `ingest.py`.
- **Never read `.sqlite3` files with `cat` or `sqlite3`** -- will corrupt context.
- **Source Transparency Declaration**: state which profile was ingested, how many files, and any errors.
