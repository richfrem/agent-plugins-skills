---
concept: procedural-fallback-tree-vector-db-agent
source: plugin-code
source_file: vector-db/skills/vector-db-search/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.441984+00:00
cluster: must
content_hash: 6ca066e11626c0bd
---

# Procedural Fallback Tree: Vector DB Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Vector DB Agent

If the primary database wrappers (`scripts/query.py`, `scripts/ingest.py`) fail, execute the following triage steps exactly in order:

## 1. Connection Refused (Server Down)
If the python scripts exit with an HTTP `Connection refused` referencing port `8110`:
- **Action**: Do not attempt to read the database manually. It means the background `chroma` server is not running on the operating system. You must either start the server manually (`vector-db-launch`) or instruct the user they must boot it up according to their profile initialization.

## 2. Invalid Profile Configuration
If `scripts/query.py` or `scripts/ingest.py` crash stating the requested `--profile` name does not exist in `.agent/learning/vector_profiles.json`:
- **Action**: Do not attempt to write the profile manually into the configuration JSON. You must execute the `vector-db-init` initialization script to guide the user organically through generating a sanitized profile structure.

## 3. Langchain Classic Storage Missing
If the ingestion tool throws a `ModuleNotFoundError` specifically noting `langchain.storage` or `langchain-classic` is missing:
- **Action**: Do not attempt to rewrite the ingestion logic. You specify that the `langchain-classic` package must be Pip installed because it contains the legacy FileStore components required by the Parent-Child retriever architecture.


## See Also

- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-create-azure-agent]]
- [[procedural-fallback-tree-create-sub-agent]]
- [[procedural-fallback-tree-claude-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[procedural-fallback-tree-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/skills/vector-db-search/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.441984+00:00
