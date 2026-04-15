---
name: vector-db-init
description: Interactively initializes the Vector DB plugin. Scaffolds the configurable vector_profiles.json for high-performance In-Process or Native Server connections. Mandatory first step before ingestion or search.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library for initialization. Performance operations require `chromadb` and `langchain` as defined in the plugin root requirements.

---

# Vector DB Initialization

The `vector-db-init` skill is an automated setup routine that prepares the environment for the Vector database. 

## Profile Configuration

This skill scaffolds a dynamic registry in `.agent/learning/vector_profiles.json`. All operational settings (batch size, models, chunking) are centralized here to avoid hardcoding in library scripts.

| Parameter | Default | Purpose |
|:-----|:--------|:--------|
| `chroma_host` | `""` | Empty for In-Process mode (Direct Disk); IP for Server mode. |
| `batch_size` | `1000` | Ingestion speed (number of files processed before embedding). |
| `embedding_model` | `nomic-ai/nomic-embed-text-v1.5` | The semantic model used for indexing. |
| `chunk_size` | `2000` (Parent) / `400` (Child) | The granularity of text splitting. |

## When to Use This
- When a user first installs the `vector-db` plugin.
- If the Vector DB profile is missing from `.agent/learning/vector_profiles.json`.
- If you need to re-scaffold a clean configuration schema after a plugin upgrade.

## Instructions for Agent

1. **Run the Initialization Script:**
   You must execute the configuration script located at `scripts/init.py`.
   ```bash
   python3 ./scripts/init.py
   ```

2. **Wait for Completion:** 
   The script will scaffold `.agent/learning/vector_profiles.json` and a default manifest. It defaults to **In-Process mode** for zero-dependency performance.

3. **Verify:**
   Inform the user their environment is ready. They can now adjust batch sizes or models directly in the JSON profile before running `vector-db-ingest`.
