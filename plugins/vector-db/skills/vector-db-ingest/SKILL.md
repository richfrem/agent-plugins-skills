---
name: vector-db-ingest
description: |
  Ingests repository files into the ChromaDB vector store. Builds or updates the vector index from a manifest or directory scan using ingest.py.
  Use when new files need to be indexed or the vector store is out of date.

  <example>
  user: "Index these new plugin files into the vector database"
  assistant: "I'll use vector-db-ingest to add them to the vector store."
  </example>
  <example>
  user: "The vector store is missing recent files -- update it"
  assistant: "I'll use vector-db-ingest to re-index the changes."
  </example>
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---

# VDB Ingest Agent

## Role

You ingest (index) repository files into the ChromaDB vector store so they can be semantically
searched. You build or update the parent-child chunk structure that `query.py` searches against.

**This is a write operation.** The vector store is the backing index for Phase 2 search.

## Prerequisites

### 1. First-time setup
If `chromadb` is not installed or `vector_profiles.json` is missing, run the init skill first:
```bash
python3 ./init.py
```

### 2. Verify server is running
Use the `vector-db-launch` skill if the server is not already up:
```bash
# Check heartbeat
curl -sf http://127.0.0.1:8110/api/v1/heartbeat

# If not running, start it:
chroma run --host 127.0.0.1 --port 8110 --path .vector_data &
```
See `SKILL.md` for full launch instructions.

## Execution Protocol

### Full ingest (first time or full rebuild)

```bash
python3 ./ingest.py \
  --profile knowledge --full
```

### Incremental ingest (only new/changed files since N hours)

```bash
python3 ./ingest.py \
  --profile knowledge --since 24
```

### Code files (uses AST parsing shim)

```bash
python3 ./ingest.py \
  --profile knowledge --full --code
```

`ingest_code_shim.py` is invoked automatically for `.py` and `.js` files to extract
functions and classes as discrete chunks rather than raw text blocks.

## After Ingesting

Run a quick smoke test to confirm the new content is retrievable:

```bash
python3 ./query.py \
  "describe what was just ingested" --profile knowledge --limit 3
```

## Rules

- **Never write to `.vector_data/` directly** -- always use `ingest.py`.
- **Never read `.sqlite3` files with `cat` or `sqlite3`** -- will corrupt context.
- **Source Transparency Declaration**: state which profile was ingested, how many files, and any errors.
