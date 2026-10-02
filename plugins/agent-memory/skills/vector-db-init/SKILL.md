---
name: vector-db-init
plugin: agent-memory
description: Interactively initializes the Vector DB plugin, configuring source manifests and vector_profiles.json for In-Process or Server mode.
allowed-tools: Bash, Read, Write
---

# Vector DB Initialization (`vector-db-init`)

Prepares the local environment and manifests for ChromaDB vector embeddings and semantic search.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Operational Parameters](#operational-parameters)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **In-Process Default**: Operates directly on disk via `chroma_data_path`; no daemon required unless multi-process concurrency is needed.
2. **Dependency Install**: Requires `chromadb` and `sentence-transformers` available in the python environment.
3. **Manifest Sovereignty**: Configuration persists in `.agent/learning/vector_profiles.json`.

## Quick start

Execute automatic profile scaffolding for local vector storage:

```bash
python3 scripts/init.py
```

## Operational Parameters

Settings configured in `.agent/learning/vector_profiles.json`:
- `chroma_host`: Empty string for in-process direct disk mode; IP:port for server mode.
- `batch_size`: Embedding batch size (default: 1,000 files).
- `embedding_model`: `nomic-ai/nomic-embed-text-v1.5`.
- `parent_chunk_size`: 2,000 chars; `child_chunk_size`: 400 chars.

## Workflow

1. **Dependency Verification**: Ensure dependencies are installed in virtualenv.
2. **Target Discovery**: Identify project directories to index (e.g. `docs/`, `plugins/`).
3. **Manifest Generation**: Write `.agent/learning/vector_knowledge_manifest.json`.
4. **Scaffold Profile**: Run `python3 scripts/init.py` to create the profile configuration.
5. **Next Steps**: Guide user to run `vector-db-ingest` to index content.

## Verification

Confirm configuration file generation and validity:

```bash
test -f .agent/learning/vector_profiles.json && echo "Profile configured"
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for vector database bootstrapping.
- [vector-db-bootstrap-guide.md](references/vector-db-bootstrap-guide.md) — Step-by-step initialization manual.
