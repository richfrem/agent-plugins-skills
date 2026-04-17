---
concept: vector-db-initialization
source: plugin-code
source_file: vector-db/skills/vector-db-init/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.432356+00:00
cluster: manifest
content_hash: fe2f21f4c1197842
---

# Vector DB Initialization

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: vector-db-init
description: Interactively initializes the Vector DB plugin. Guided discovery asks which folders to index, confirms the manifest, then scaffolds vector_profiles.json for high-performance In-Process or Native Server connections. Mandatory first step before ingestion or search.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library for initialization. Performance operations require `chromadb` and `langchain` as defined in the plugin root requirements.

**To install this skill's dependencies:**
```bash
python -m piptools compile requirements.in --output-file requirements.txt
pip install -r requirements.txt
```

---

# Vector DB Initialization

The `vector-db-init` skill is an interactive setup routine that prepares the environment for the Vector database. It follows the same pattern as `rlm-init` and `wiki-init` for a consistent experience across all three retrieval plugins.

## Profile Configuration Reference

All operational settings live in `.agent/learning/vector_profiles.json`. These control performance and connection mode.

| Parameter | Default | Purpose |
|:-----|:--------|:--------|
| `chroma_host` | `""` | Empty = In-Process (Direct Disk); IP = Server mode. |
| `batch_size` | `1000` | Files processed per embedding batch. |
| `embedding_model` | `nomic-ai/nomic-embed-text-v1.5` | Semantic model for indexing. |
| `device` | `cpu` | Hardware: `cpu` or `cuda` (NVIDIA GPU). |
| `parent_chunk_size` | `2000` | Parent chunk granularity. |
| `child_chunk_size` | `400` | Child chunk granularity. |

## When to Use This

- When a user first installs the `vector-db` plugin.
- If the Vector DB profile is missing from `.agent/learning/vector_profiles.json`.
- If you need to add a new manifest profile or update which folders are indexed.
- If you need to re-scaffold a clean configuration after a plugin upgrade.

---

## Default: In-Process (Filesystem) Mode

Vector-db runs **In-Process by default** — ChromaDB persists directly to a local directory
(configured as `chroma_data_path` in `vector_profiles.json`). No server process is needed.

When running `ingest.py` or `query.py` you will see:
```
[WARN] Failed to connect to remote ChromaDB ... Falling back to local.
[DIR] Connecting to local persistent ChromaDB at .agent/learning/vector_wiki_db...
```
**This is expected and correct.** The remote-server check (`127.0.0.1:8110`) happens
automatically in case a server IS running, but falls back gracefully. Only switch to
server mode (`vector-db-launch` skill) if you need multiple concurrent writers.

---


### Step 0: Install Dependencies (MANDATORY — do this first)

**Before anything else**, install the plugin's Python dependencies from the lockfile.

Run from the project root:

```bash
# Regenerate the lockfile from the intent file (only needed when requirements.in changes):
python3 -m piptools compile plugins/vector-db/requirements.in \
    --output-file plugins/vector-db/requirements.txt

# Install all dependencies (always run this on first setup):
python3 -m pip install -r plugins/vector-db/requirements.txt
```

> **Note:** `pip-tools` itself must be installed first if not present:
> ```bash
> python3 -m pip install pip-tools
> ```
>
> **Known gotcha:** The system `pip` command may not be available on macOS. Always use
> `python3 -m pip install ...` rather than bare `pip install ...`.

Verify the critical packages are installed:

```bash
python3 -c "import chromadb; print('chromadb:', chromadb.__version__)"
python3 -c "import einops; print('einops: OK')"
python3 -c "from sentence_transformers import SentenceTransformer; print('sentence-transformers: OK')"
```

If any check fails, the install step above will fix it.

---

### Step 1: Setup Mode Selection

**Ask this after dependencies are installed.**

First, check what other plugins are installed:
```bash
ls .agents/skills/rlm-init/              2>/dev/null && echo "rlm-factory: INSTALLED"          || echo

*(content truncated)*

## See Also

- [[acceptance-criteria-vector-db-init]]
- [[acceptance-criteria-vector-db-init]]
- [[vector-db-launch-python-native-server]]
- [[acceptance-criteria-vector-db-launch]]
- [[vector-db-search]]
- [[acceptance-criteria-vector-db-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `vector-db/skills/vector-db-init/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.432356+00:00
