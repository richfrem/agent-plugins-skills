---
concept: rlm-factory-plugin
source: plugin-code
source_file: rlm-factory/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.668351+00:00
cluster: agent
content_hash: a7f73c9e057578b7
---

# RLM Factory Plugin 🏭

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# RLM Factory Plugin 🏭

Recursive Language Model factory — distill repository files into dense semantic summaries
for O(1) keyword retrieval. **Works completely standalone** with zero external plugin deps.
Pair with vector-db and/or obsidian-wiki-engine for a full Super-RAG 3-tier search stack.

## Standalone vs Combined

**RLM factory is a complete product on its own.** Every file read once, summarized once,
cached as plain text JSON. Searching is O(1) keyword lookup — no embeddings, no inference.

| Mode | What you get | External deps in `.agents/` |
|:-----|:-------------|:----------------------------|
| **Standalone** | O(1) keyword search across all file summaries | None |
| **+ vector-db** | Phase 1 narrows candidates; Phase 2 finds by meaning | `vector-db-init/` |
| **+ obsidian-wiki-engine** | RLM distillation layers per concept node; wiki query uses RLM pre-filter | `obsidian-wiki-builder/` |
| **Full Super-RAG** | All three: keyword → semantic → concept node | Both above |

## Start Here

**Skills run from `.agents/skills/` (the deployed runtime), not from `plugins/`.**

```bash
# Verify this plugin is installed and active
ls .agents/skills/rlm-init/           # should exist
ls .agents/agents/rlm-factory-init-agent.md  # should exist

# If missing — install via:
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
# or: npx skills add richfrem/agent-plugins-skills
# or: see INSTALL.md
```

**To initialize:** invoke `rlm-factory-init-agent` (or say "initialize RLM" / "set up my semantic cache").
The agent asks what mode you want (standalone or combined with vector-db / obsidian-wiki-engine).

## Prerequisites

- **Claude Code** ≥ 1.0.33
- **Python** ≥ 3.8
- **Python Dependencies**: `pip install requests python-dotenv`

## Verify Installation

After loading, the following skills should be available in `.agents/skills/`:
- `rlm-init` — Bootstrap caching and profile setup
- `rlm-search` — O(1) keyword search across the summary ledger
- `rlm-curator` — Audit coverage, analyze cache gaps
- `rlm-distill-agent` — Agent-powered summarization engine
- `rlm-cleanup-agent` — Pruning stale/orphan entries

```bash
# Confirm skills are installed
ls .agents/skills/ | grep rlm
```

---

## Configuration

### Profiles (`rlm_profiles.json`)

Configuration lives in `.agent/learning/rlm_profiles.json` (no `.env` required).
Profiles declare which files to index, where to store the cache, and which model to use.

See `resources/` for manifest files and `rlm_profiles.json` for profile templates.

## Usage Guide

### Quick Start
```bash
# 1. Check what's already memorized
python3 ./scripts/inventory.py --profile project

# 2. Search for a topic (natively across markdown)
python3 ./scripts/query_cache.py "authentication" --profile project

# 3. Distill missing files (Automatic via Swarm)
# Note: Limit --workers 2 when using gpt-5-mini free tier
python3 ./scripts/swarm_run.py --engine copilot --workers 2 ...

# 4. Clean up deleted files
python3 ./scripts/cleanup_cache.py --profile project --apply
```

### Memory Banks (Profiles)

| Profile | Flag | Cache Location | Use For |
|:---|:---|:---|:---|
| **Project** | `--type project` | `rlm_summary_cache/` | Project Docs, READMEs |
| **Tool** | `--type tool` | `rlm_tool_cache/` | Python scripts, CLI tools |

---

## Customizing Your Factory 🛠️

The RLM Factory is now entirely manifest-driven and project-agnostic. You can customize the distillation behavior by editing the files in the `resources/` directory:

### 1. `resources/manifest-index.json`
This is the profile registry. You can add or rename profiles here:
```json
"project": {
    "description": "Custom Docs Profile",
    "manifest": "assets/resources/rlm_manifest.json",
    "cache": ".agent/learning/custom_cache.json",
    "parser": "directory_glob",
    "prompt_path": "./resources/prompts/rlm/custom_prompt.md",
    "env_prefix": "RLM_CUSTOM",
    "allowed_suffixes": [".md", ".txt"],
    "l

*(content truncated)*

## See Also

- [[acceptance-criteria-rlm-factory-curator]]
- [[procedural-fallback-tree-rlm-factory]]
- [[agent-protocol-rlm-factory]]
- [[acceptance-criteria-rlm-factory-curator]]
- [[procedural-fallback-tree-rlm-factory]]
- [[agent-protocol-rlm-factory]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `rlm-factory/README.md`
- **Indexed:** 2026-04-17T06:42:09.668351+00:00
