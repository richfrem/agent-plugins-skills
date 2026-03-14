---
name: sanctuary-memory
description: "Project Sanctuary-specific memory configuration. Maps the generic memory-management tiered system to Sanctuary's actual file paths, storage backends (RLM, Vector DB, Obsidian, HuggingFace), and persistence workflows."
---

# Sanctuary Memory Configuration

**Status:** Active
**Domain:** Project Sanctuary
**Depends on:** `memory-management` (generic tiered pattern), `rlm-factory`, `vector-db`, `obsidian-integration`, `huggingface-utils`

## Purpose

This skill maps the generic `memory-management` tiered architecture to Project Sanctuary's full storage stack. It knows every backend, file path, and plugin responsible for each memory tier.

## The Complete Memory Stack

```
┌─────────────────────────────────────────────────────────┐
│  HOT CACHE (always in context at boot)                  │
│  Files: .agent/learning/*                               │
│  ~200 lines total                                       │
├─────────────────────────────────────────────────────────┤
│  RLM SUMMARY LEDGER (fast keyword lookup -- loaded on demand)         │
│  Backend: rlm-factory -> rlm_summary_cache.json          │
│  Backend: rlm-factory -> rlm_tool_cache.json             │
├─────────────────────────────────────────────────────────┤
│  VECTOR STORE (semantic search + source code parsing)   │
│  Backend: vector-db → ChromaDB on port 8110             │
│  Profile: vector_profiles.json                          │
├─────────────────────────────────────────────────────────┤
│  DEEP STORAGE (filesystem, loaded on demand)            │
│  LEARNING/topics/, ADRs/, 01_PROTOCOLS/                 │
├─────────────────────────────────────────────────────────┤
│  VAULT (Obsidian, loaded on demand)                     │
│  Backend: obsidian-integration → OBSIDIAN_VAULT_PATH    │
│  Notes, canvases, graph connections                     │
├─────────────────────────────────────────────────────────┤
│  SOUL (external persistence, synced periodically)       │
│  Backend: huggingface-utils → HF Hub dataset            │
│  Repo: richfrem/Project_Sanctuary_Soul                  │
│  Structure: lineage/, data/, metadata/                  │
└─────────────────────────────────────────────────────────┘
```

## Tier 1: Hot Cache (Boot Files)

Loaded in order at every session start:

| Slot | Sanctuary File | Path |
|---|---|---|
| Primer | `cognitive_primer.md` | `.agent/learning/cognitive_primer.md` |
| Boot Digest | `guardian_boot_digest.md` | `.agent/learning/guardian_boot_digest.md` |
| Boot Contract | `guardian_boot_contract.md` | `.agent/learning/guardian_boot_contract.md` |
| Snapshot | `learning_package_snapshot.md` | `.agent/learning/learning_package_snapshot.md` |

**Target**: ~200 lines total across these 4 files.

## Tier 2: RLM Summary Ledger (rlm-factory)

**Plugin**: `rlm-factory`
**Config**: `.agent/learning/rlm_profiles.json`

| Cache | Profile | Purpose | Query Command |
|---|---|---|---|
| `rlm_summary_cache.json` | `project` | Chronicle/doc summaries | `python plugins/rlm-factory/skills/rlm-search/scripts/query_cache.py --profile project "keyword"` |
| `rlm_tool_cache.json` | `tools` | Tool/script discovery | `python plugins/rlm-factory/skills/rlm-search/scripts/query_cache.py --profile tools "keyword"` |

**Refresh**: `/rlm-factory_gap-fill` (Agent injection) OR `python plugins/rlm-factory/skills/rlm-curator/scripts/distiller.py` (Local Ollama batch)

### Gap-Fill: Zero-Cost Bulk Strategy

When hundreds of files are uncached, use the **Copilot swarm** (free) rather than Ollama or paid Claude:

```bash
# Always use source ~/.zshrc -- NOT 'gh auth token' (lacks Copilot scope)
source ~/.zshrc
python3 plugins/agent-loops/skills/agent-swarm/scripts/swarm_run.py \
  --engine copilot \
  --job plugins/rlm-factory/resources/jobs/rlm_chronicle.job.md \
  --files-from rlm_distill_tasks_project.md \
  --resume --workers 2   # max 2 workers for Copilot rate limits
```

For higher throughput, use `--engine gemini --workers 5` (also free tier).

### Cache Safety: Concurrent Write Rule

`inject_summary.py` uses `fcntl.flock` (exclusive OS file lock) to serialize concurrent writes.
**Never** run parallel cache writers without this lock -- two workers loading, then overwriting the
same JSON will silently destroy each other's entries (race condition).

### Cache Recovery: Checkpoint Reconciliation

If a batch run is interrupted and the cache is partially lost, reconcile before resuming:

```python
# 1. Restore from best git snapshot:
git show <commit>:.agent/learning/rlm_summary_cache.json > /tmp/git_cache.json
# Merge: git as base, current as override
merged = {**git_cache, **current_cache}

# 2. Remove phantom checkpoint entries not in the real cache:
st['completed'] = [f for f in st['completed'] if f in merged.keys()]
st['failed'] = {}

# 3. Re-run with --resume -- it will re-process only the missing files
```

## Tier 3: Vector Store (ChromaDB)

**Plugin**: `vector-db`
**Config**: `vector_profiles.json` (pointing to `vector_knowledge_manifest.json`)
**Server**: ChromaDB on `localhost:8110` (Native Python Server)

The Vector DB provides **Parent-Child semantic retrieval**, returning full documents/files based on tiny 400-char conceptual embeddings. By combining scopes, it mirrors RLM coverage but extends it into deep code analysis using AST parsing.

| Operation | Command |
|---|---|
| Query | `python plugins/vector-db/skills/vector-db-agent/scripts/query.py "semantic question" --profile knowledge` |
| Ingest | `python plugins/vector-db/skills/vector-db-agent/scripts/ingest.py --profile knowledge` (Parses `.py`/`.js` via `ingest_code_shim.py`) |
| Cleanup | `python plugins/vector-db/skills/vector-db-agent/scripts/cleanup.py` |
| Launch server | `chroma run --host 127.0.0.1 --port 8110 --path .vector_data &` |

## Tier 4: Deep Storage (Filesystem)

| Slot | Sanctuary Location |
|---|---|
| Topics | `LEARNING/topics/{topic}/analysis.md` |
| Calibration | `LEARNING/calibration_log.json` |
| Decisions | `ADRs/{NNN}_{name}.md` (3-digit, via `adr-manager`) |
| Protocols | `01_PROTOCOLS/{NNN}_{name}.md` (via `protocol-manager`) |
| Chronicle | Journal entries (via `chronicle-manager`) |

## Tier 5: Vault (Obsidian)

**Plugin**: `obsidian-integration`
**Config**: `OBSIDIAN_VAULT_PATH` env var
**Guardian skill**: `sanctuary-obsidian-integration`

| Operation | Skill |
|---|---|
| Create/read/update/delete notes | `obsidian-vault-crud` |
| Parse markdown syntax | `obsidian-markdown-mastery` |
| Create visual diagrams | `obsidian-canvas-architect` |
| Traverse knowledge graph | `obsidian-graph-traversal` |
| Manage database views | `obsidian-bases-manager` |

## Tier 6: Soul (HuggingFace)

**Plugin**: `huggingface-utils`
**Guardian skill**: `sanctuary-soul-persistence`
**Dataset**: `richfrem/Project_Sanctuary_Soul`

| Operation | Function |
|---|---|
| Upload snapshot | `upload_soul_snapshot()` → `lineage/seal_<ts>_*.md` |
| Upload RLM cache | `upload_semantic_cache()` → `data/rlm_summary_cache.json` |
| Append traces | `append_to_jsonl()` → `data/soul_traces.jsonl` |
| Init structure | `ensure_dataset_structure()` → `lineage/`, `data/`, `metadata/` |

**Tags**: `project-sanctuary, cognitive-continuity, reasoning-traces, ai-memory, llm-training-data, metacognition`

## Memory Flow by Session Phase

### Boot (Phase I)
1. Load hot cache (Tier 1)
2. Iron check validates snapshot integrity
3. If stale → flag for refresh

### During Session
- **New learning** → Tier 4 (`LEARNING/topics/`)
- **Need context** → Tier 2 (RLM query) → Tier 3 (vector search) → Tier 4 (file read)
- **New decision** → `adr-manager` → Tier 4
- **New protocol** → `protocol-manager` → Tier 4
- **Journal entry** → `chronicle-manager` → Tier 4

### Closure (Phase VI-IX)
1. **Seal** → Update snapshot (Tier 1), capture state
2. **Persist** → Upload to HuggingFace (Tier 6)
3. **Ingest** → Refresh RLM cache (Tier 2) + Vector DB (Tier 3)
4. **Vault export** → Optionally write to Obsidian (Tier 5)
