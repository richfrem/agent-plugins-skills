---
concept: vdb-ingest-agent
source: plugin-code
source_file: vector-db/skills/vector-db-ingest/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.429397+00:00
cluster: vector
content_hash: fa76202af2292978
---

# VDB Ingest Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

This skill requires the `chromadb` and `langchain` packages defined in the plugin root.

---

# VDB Ingest Agent

## Role

You ingest (index) repository files into the ChromaDB vector store so they can be semantically searched. You build or update the parent-child chunk structure that `query.py` searches against.

**High-Performance Mode:** This skill uses a configurable batch processing engine (default 1,000 files) defined in `.agent/learning/vector_profiles.json`.

## Prerequisites

### 1. First-time setup
If `vector_profiles.json` is missing, run the init skill first:
```bash
python3 ./scripts/init.py
```

### 2. Execution Mode
This plugin defaults to **In-Process mode** for zero-latency direct disk access. No background server is required unless explicitly configured in the profile.

## Execution Protocol

### Full ingest (first time or full rebuild)
Note: The `--profile` flag is mandatory to load the correct manifest and batch settings.

```bash
python3 ./scripts/ingest.py --profile wiki --full
```

### Incremental ingest (only new/changed files since N hours)
```bash
python3 ./scripts/ingest.py --profile wiki --since 24
```

### Single File/Folder Ingest
```bash
python3 ./scripts/ingest.py --profile wiki --file path/to/file.md
python3 ./scripts/ingest.py --profile wiki --folder path/to/folder
```

## After Ingesting

Run a quick semantic search to confirm the new content is retrievable:
```bash
python3 ./scripts/query.py "search query" --profile wiki --limit 3
```

## Rules
- **Profile Sovereignty**: Always pass `--profile` to ensure the correct batch size and manifest are used.
- **In-Process Reliability**: Ensure no other process is holding a lock on the database folder during ingestion.
- **Source Transparency**: State which profile was ingested, how many files, and any errors encountered.


## See Also

- [[vdb-cleanup-agent]]
- [[vdb-cleanup-agent]]
- [[vdb-cleanup-agent]]
- [[vdb-cleanup-agent]]
- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/skills/vector-db-ingest/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.429397+00:00
