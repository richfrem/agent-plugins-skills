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

## Interactive Setup Protocol

### Step 0: Setup Mode Selection

**Ask this before anything else.**

First, check what other plugins are installed:
```bash
ls .agents/skills/rlm-init/              2>/dev/null && echo "rlm-factory: INSTALLED"          || echo "rlm-factory: NOT FOUND"
ls .agents/skills/obsidian-wiki-builder/ 2>/dev/null && echo "obsidian-wiki-engine: INSTALLED"  || echo "obsidian-wiki-engine: NOT FOUND"
```

Then ask:
```
Vector DB works standalone with zero external dependencies. You can also combine it with
other plugins for a more powerful retrieval stack. What setup would you like?

  A) Vector DB only (standalone)
     - Semantic search over any indexed folders
     - No other plugins needed — works right now

  B) Vector DB + RLM Phase 1 pre-filter                [requires: rlm-factory in .agents/]
     - RLM keyword pre-filter -> vector semantic search
     - Reduces noise, improves precision for large corpora

  C) Vector DB as wiki Phase 2 search                  [requires: obsidian-wiki-engine in .agents/]
     - Adds vector semantic search to /wiki-query
     - /wiki-query: RLM keyword (O(1)) -> vector (O(log N)) -> grep exact

  D) Full Super-RAG                                    [requires: rlm-factory + obsidian-wiki-engine]
     - All three phases: RLM keyword -> vector semantic -> wiki concept nodes

Enter A, B, C, or D (default: A):
```

If required plugins are NOT installed for the chosen mode:
```
[plugin-name] is not installed in .agents/.

To install it:

  # Recommended (uvx -- works on Mac, Linux, Windows)
  uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills

  # See full install guide
  cat INSTALL.md

After installing, re-run /vector-db:init and choose your desired mode.

Continue with Mode A (standalone) for now? (y) or abort and install first? (n)
```

---

### Step 1: Guided Source Discovery

Scan the project root and present a numbered table of candidate directories:

```bash
find . -maxdepth 1 -type d | grep -v '^\.$' | grep -v -E '\.(git|venv|vscode|windsurf|claude|agents|agent|knowledge_vector_data|wiki|vector_data)$' | sort
```

Present results as a numbered table with a one-line description of each folder. Then ask:

```
Which folders should be treated as raw content sources for vector indexing?

  Enter numbers separated by commas (e.g. 1, 3, 5)
  or type custom paths (relative or absolute)
  or both (e.g. 1, 2, /path/to/other/dir)

  You can specify all sources now in one go.
```

Resolve all selected paths to their relative form from the project root (e.g. `plugins/`, `plugin-research/`).
Validate each path exists. Warn if a path does not exist -- ask the user to confirm or skip it.

Then ask once, globally:

```
Any subdirectory patterns or file types to exclude beyond the defaults?
Defaults: .git/, node_modules/, .venv/, __pycache__/, requirements.in, requirements.txt

Press Enter to accept defaults, or type additions (e.g. temp/, *.tmp):
```

---

### Step 2: Confirm and Write Manifest

Display the complete manifest before writing, using the same flat schema as `rlm-factory` and `obsidian-wiki-engine`:

```json
{
  "description": "Globs tracking project documentation and knowledge records.",
  "include": [
    "<folder_1>/",
    "<folder_2>/"
  ],
  "exclude": [
    "/.git/",
    "/node_modules/",
    "/.venv/",
    "/__pycache__/",
    "requirements.in",
    "requirements.txt"
  ]
}
```

Ask: "Does this look correct? (y to write, e to edit, q to abort)"

If `.agent/learning/vector_knowledge_manifest.json` already exists:
- Ask: "A manifest already exists. Overwrite, merge (add new includes only), or abort? (o/m/q)"
- **Merge**: append new paths to the existing `include` array; never remove existing entries
- **Overwrite**: replace entirely with the new manifest

Write to: `.agent/learning/vector_knowledge_manifest.json`
Create parent directories if needed.

> **Note on manifest naming**: `vector_profiles.json` may reference `vector_wiki_manifest.json` (legacy name).
> The canonical filename going forward is `vector_knowledge_manifest.json`. If the profile still points
> to the old name, update the `manifest` field in `vector_profiles.json` to match.

---

### Step 3: Scaffold Profile and Install Dependencies

After the manifest is confirmed, run the init script which handles profile scaffolding and dependency installation:

```bash
python3 ./scripts/init.py
```

The script will:
1. Install Python dependencies from the lockfile (`requirements.txt`)
2. Scaffold or update `.agent/learning/vector_profiles.json` with the `wiki` profile
3. Set `chroma_host: ""` (In-Process mode by default — no server needed)

After the script runs, verify the profile's `manifest` field points to `vector_knowledge_manifest.json`.
If it still shows `vector_wiki_manifest.json`, update it:

```json
{
  "version": 2,
  "profiles": {
    "wiki": {
      "manifest": ".agent/learning/vector_knowledge_manifest.json"
    }
  },
  "default_profile": "wiki"
}
```

---

### Step 4: Verify and Show Next Steps

Confirm the files written, then print:

```
=== Vector DB Setup Complete (Mode <X>) ===

Files written:
  - .agent/learning/vector_knowledge_manifest.json  (<N> sources)
  - .agent/learning/vector_profiles.json            (wiki profile ready)

Next steps:
  /vector-db:ingest   <- build the semantic index from your sources
  /vector-db:search   <- run semantic queries
  /vector-db:audit    <- check index coverage

[Mode B/C/D] To activate the full retrieval stack:
  /rlm-factory:init   <- set up RLM Phase 1 keyword pre-filter
  /wiki-init          <- set up wiki concept node layer
```
