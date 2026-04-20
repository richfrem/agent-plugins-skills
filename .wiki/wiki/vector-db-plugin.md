---
concept: vector-db-plugin
source: plugin-code
source_file: vector-db/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.420038+00:00
cluster: mode
content_hash: d0e30c51e7666db8
---

# Vector DB Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Vector DB Plugin

**Local Semantic Search Engine powered by ChromaDB**

## Start Here

**Skills run from `.agents/skills/` (the deployed runtime), not from `plugins/`.**

```bash
# Verify this plugin is installed and active
ls .agents/skills/vector-db-init/       # should exist
ls .agents/agents/vector-db-init-agent.md  # should exist

# If missing — install via:
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
# or: npx skills add richfrem/agent-plugins-skills
# or: see INSTALL.md
```

**To initialize:** invoke `vector-db-init-agent` (or say "initialize vector db" / "set up ChromaDB").
The agent asks what mode you want (standalone or combined with rlm-factory / obsidian-wiki-engine).

Search your repository by *meaning*, not just keywords. Uses a **Parent-Child Retrieval
Architecture** and local **Nomic Embeddings** to provide precise code context without
sacrificing the surrounding logic. Supports In-Process mode (zero server setup) and
HTTP Server mode (concurrent multi-process access).

## Architecture Highlights

- **Parent-Child Retrieval**: Files stored as parents (full context), searched via child chunks (400-char precise matches). Exact semantic match + full context returned.
- **Nomic Embeddings**: `nomic-ai/nomic-embed-text-v1.5` (768-dim) — enterprise-grade local embeddings, no API keys.
- **In-Process Mode**: Direct disk access, zero background server required. Default for single-agent use.
- **HTTP Server Mode**: `chroma run` background server for concurrent multi-process access.
- **Profile-Driven**: Controlled by `.agent/learning/vector_profiles.json` — multi-profile support.
- **Zero .env dependency**: All settings managed in JSON profiles.
- **LangChain Classic Storage**: `langchain-classic` for robust local FileStore persistence.

## Quick Start (In-Process — recommended)

```bash
# 1. Initialize via guided agent (recommended)
#    Creates vector_profiles.json + vector_knowledge_manifest.json
/vector-db:init

# 2. Ingest
python ./scripts/ingest.py --full --profile knowledge

# 3. Search
python ./scripts/query.py "your question here" --profile knowledge
```

## Quick Start (HTTP Server mode)

```bash
# 1. Initialize
/vector-db:init   # select HTTP Server mode when prompted

# 2. Start background server
chroma run --host 127.0.0.1 --port 8110 --path .vector_data

# 3. Ingest
python ./scripts/ingest.py --full --profile knowledge

# 4. Search
python ./scripts/query.py "your question here" --profile knowledge
```

## Initialization Agent

The `vector-db-init-agent` guides through complete first-time setup:

1. Python dependency check (`chromadb`, `sentence-transformers`, `langchain-community`)
2. Mode selection: In-Process (default) vs HTTP Server
3. Profile configuration with content-type-based chunk sizes
4. `vector_profiles.json` write (merge or overwrite if exists)
5. `vector_knowledge_manifest.json` — directory scope configuration
6. Validation dry-run

Trigger: "initialize vector db", "set up vector search", "set up ChromaDB", `/vector-db:init`

## Config Files (canonical location: `.agent/learning/`)

| File | Purpose |
|:-----|:--------|
| `vector_profiles.json` | Profile definitions (chunk sizes, collections, mode) |
| `vector_knowledge_manifest.json` | Directory scope for ingest |

## Skills

| Skill | Purpose |
|:------|:--------|
| **vector-db-init** | Interactive setup for profiles, deps, and manifest |
| **vector-db-ingest** | Build/update the vector index |
| **vector-db-search** | Semantic search across indexed content |
| **vector-db-launch** | Start the ChromaDB HTTP server |
| **vector-db-cleanup** | Remove deleted files from the index |

## Agents

| Agent | Purpose |
|:------|:--------|
| **vector-db-init-agent** | Full guided initialization wizard |

## Scripts

| Script | Description |
|:-------|:------------|
| `scripts/init.py` | Interactive setup (legacy — prefer init agent) |
| `scripts/ingest.py` | Build/update the database 

*(content truncated)*

## See Also

- [[vector-db-initialization]]
- [[acceptance-criteria-vector-db-init]]
- [[acceptance-criteria-vector-db-init]]
- [[vector-db-launch-python-native-server]]
- [[acceptance-criteria-vector-db-launch]]
- [[vector-db-search]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/README.md`
- **Indexed:** 2026-04-17T06:42:10.420038+00:00
