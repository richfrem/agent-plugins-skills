# Vector DB Plugin

**Local Semantic Search Engine powered by ChromaDB**

Search your repository by *meaning*, not just keywords. Uses a highly-accurate **Parent-Child Retrieval Architecture** and local **Nomic Embeddings** to provide precise code context to the agent without sacrificing the "big picture" surrounding logic.

## Architecture Highlights
- **Parent-Child Retrieval**: Files are stored exactly as they are (Parents), but searched via tiny chunks (Children). This guarantees exact semantic matches of specific functions, while returning the entire file to the LLM for maximum context.
- **Nomic Embeddings**: Uses `nomic-ai/nomic-embed-text-v1.5` (768-dim) for enterprise-grade, local code embedding without API keys.
- **Python-Native Server**: Zero Docker/Podman required. Runs `chroma run` as a background HTTP server for safe, concurrent agent access.
- **Manifest-Driven**: Controlled by `ingest_manifest.json`, giving you exact precision over which directories are indexed.

## Prerequisites
- Python 3.8+
- Use the initialization skill to set up the environment:
  ```bash
  python3 plugins/vector-db/skills/vector-db-init/scripts/init.py
  ```

## Commands

| Command | Description |
|:---|:---|
| `plugins/vector-db/skills/vector-db-init/scripts/init.py` | Interactive setup for `.env`, PIP deps, and Manifest. |
| `chroma run --host 127.0.0.1 --port 8110 --path .vector_data` | Background server launch (Option C, Recommended). |
| `python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py` | CLI to build/update the database. |
| `python3 plugins/vector-db/skills/vector-db-agent/scripts/query.py` | CLI for testing semantic searches. |
| `python3 plugins/vector-db/skills/vector-db-agent/scripts/cleanup.py` | Scans for and removes deleted files from the DB. |

## Quick Start
```bash
# 1. Initialize DB + Manifest
python3 plugins/vector-db/skills/vector-db-init/scripts/init.py

# 2. Start the Server (In a background terminal / new tab)
chroma run --host 127.0.0.1 --port 8110 --path .vector_data

# 3. Ingest Repository
python3 plugins/vector-db/skills/vector-db-agent/scripts/ingest.py --full

# 4. Search
python3 plugins/vector-db/skills/vector-db-agent/scripts/query.py "your question here"
```
