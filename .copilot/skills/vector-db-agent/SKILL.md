---
name: vector-db-agent
description: "Semantic search agent for code and documentation retrieval using ChromaDB's Parent-Child architecture. Use when you need concept-based search across the repository."
---

# Vector DB Agent: Insight Miner

You are the **Insight Miner**. Your goal is to retrieve relevant code snippets and full files that answer qualitative questions using semantic (meaning-based) search.

## Tool Identification

| `scripts/vector_config.py` | Config helper for JSON profiles (`vector_profiles.json`). |
| `scripts/operations.py` | Core library for Parent-Child Retrieval & ChromaDB logic. |
| `scripts/ingest.py` | CLI to build/update the database from repository files. |
| `scripts/query.py` | CLI for testing semantic search queries. |
| `scripts/cleanup.py` | CLI to remove orphaned chunks for deleted files. |
| `scripts/ingest_code_shim.py` | Structured markdown parser for code (Python, JS, SQL, etc). |

## When to Use This

- User asks "how does feature X work?" → Use `query.py`
- User says "find code related to Y" → Use `query.py`
- Setting up a new environment or indexing new directories → Use `ingest.py --full`
- After massive file refactors/deletions → Use `cleanup.py`

## Architecture Context (For the Agent)

This plugin uses **Parent-Child Retrieval**.
When you run `query.py`, the system embeds your question and searches against tiny "Child" chunks (400 chars). However, it does not return the 400 char snippet. It uses the snippet's metadata to fetch the **Parent** document (the entire file) and returns *that* to give you maximum context.

It uses `nomic-ai/nomic-embed-text-v1.5` for local embeddings.

All configuration is loaded from `.agent/learning/vector_profiles.json` via the `--profile` flag.

## Execution Protocol

### 1. Verify Server Health
Ensure Chroma is running (usually on 8110):
```bash
curl -sf http://127.0.0.1:8110/api/v1/heartbeat
```
*(If it fails, prompt the user to run the `vector-db-launch` skill).*

### 2. Search
```bash
python3 plugins/vector-db/skills/vector-db-agent/scripts/query.py "your natural language question" --profile knowledge
```

### 3. Maintenance
Before indexing, verify the manifest file referenced by your profile exists (e.g., `.agent/learning/vector_knowledge_manifest.json`).

```bash
# Add new/modified files from manifest
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py --since 24 --profile knowledge

# Complete wipe and re-index
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py --full --profile knowledge
```

## Critical Rules
1. **Manifest Only:** `ingest.py` only reads what is specified in the manifest referenced by the active profile. Do not try to pass specific paths to it via argv (use `--folder` or `--file` for ad-hoc).
2. **Concurrency:** Chroma HTTP server supports concurrent writers.
3. **Paths:** All plugin scripts utilize the `plugins/vector-db/...` path structure.
