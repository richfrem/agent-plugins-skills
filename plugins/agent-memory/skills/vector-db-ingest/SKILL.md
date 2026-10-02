---
name: vector-db-ingest
plugin: agent-memory
description: Ingests repository files into the ChromaDB vector store, building or updating the vector index using ingest.py.
allowed-tools: Bash, Read, Write
---

# Vector DB Ingest (`vector-db-ingest`)

Ingests and indexes repository files into the ChromaDB vector store for semantic retrieval.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints

1. **Profile Sovereignty**: Always specify `--profile` to ensure the correct manifest and batch configuration are loaded.
2. **Lock Concurrency**: Ensure no concurrent process holds a lock on the database folder during ingestion.
3. **Transparency**: Report target profile, indexed file count, and any processing errors.

## Quick start

Run incremental ingestion for the default wiki profile (last 24 hours):

```bash
python3 scripts/ingest.py --profile wiki --since 24
```

## Workflow

1. **Prerequisite Check**: Ensure profiles exist in `.agent/learning/vector_profiles.json` (or initialize via `vector-db-init`).
2. **Execute Ingest**: Run `scripts/ingest.py` with `--profile` and appropriate target scope:
   - Specific file: `python3 scripts/ingest.py --profile wiki --file path/to/file.md`
   - Specific directory: `python3 scripts/ingest.py --profile wiki --folder path/to/folder`
   - Incremental: `python3 scripts/ingest.py --profile wiki --since 24`
   - Full rebuild: `python3 scripts/ingest.py --profile wiki --full`
3. **Report Output**: State target profile, number of chunks created, and total runtime.

## Verification

Confirm indexed content is immediately retrievable via semantic query:

```bash
python3 scripts/query.py "test query" --profile wiki --limit 3
```
