---
name: memory-management
description: "Tiered memory system for cognitive continuity across agent sessions. Manages hot cache (session context loaded at boot) and deep storage (loaded on demand). Use when: (1) starting a session and loading context, (2) deciding what to remember vs forget, (3) promoting/demoting knowledge between tiers, (4) user says 'remember this' or asks about project history."
allowed-tools: Read, Write
---
# Memory Management

Tiered memory system that makes an AI agent a continuous collaborator across sessions.

## Architecture

The memory system has four tiers, configurable per project:

```
HOT CACHE (always loaded at boot -- ~200 lines target)
+-- <primer_file>             Role, identity, constraints
+-- <boot_digest_file>        Tactical status, active tasks
+-- <boot_contract_file>      Immutable constraints
+-- <snapshot_file>           Cognitive Hologram (1 sentence per file)

RLM SUMMARY LEDGER (fast keyword lookup -- loaded on demand)
+-- <summary_cache_file>      Pre-generated text summaries: docs, protocols, research
+-- <tool_cache_file>         Pre-generated text summaries: plugins, skills, scripts

VECTOR STORE (semantic embedding search -- loaded on demand)
+-- <vector_db_backend>       ChromaDB via vector-db plugin

DEEP STORAGE (authoritative source -- loaded on demand)
+-- <domain_data_dir>/        Research topics: {topic}/analysis.md
+-- <design_docs_dir>/        ADRs, RFCs
+-- <governance_dir>/         Protocols, playbooks
+-- <vault_dir>/              Linked knowledge graph (e.g. Obsidian)
+-- <traces_file>             External persistent log (e.g. HuggingFace)
```

Projects define their own file paths for each slot. Tiers may be omitted or added based on project complexity.

## Lookup Flow (3-Phase Search Protocol)

When searching for information, ALWAYS escalate in order. Never skip ahead.

```
Query arrives ->
1. HOT CACHE                     Instant. Boot files cover ~90% of context needs.
2. DEEP STORAGE (topic/decision) Load specific domain dir or design doc by subject.
3. RLM SUMMARY LEDGER (Phase 1)  Keyword search via query_cache.py.
4. VECTOR STORE (Phase 2)        Semantic search via query.py + ChromaDB.
5. GREP / EXACT SEARCH (Phase 3) rg/grep scoped to paths from Steps 3 or 4.
6. Ask user                      Unknown? Learn it and persist it.
```

### Phase 1 -- RLM Summary Scan (Table of Contents)

RLM is **amortized prework**: each file read ONCE, summarized ONCE, cached as plain text JSON.
Searching summaries is O(1) keyword lookup -- no embeddings, no inference.

```bash
python3 plugins/rlm-factory/skills/rlm-search/scripts/query_cache.py \
  --profile plugins "what does the vector query tool do"

python3 plugins/rlm-factory/skills/rlm-search/scripts/query_cache.py \
  --profile project --list
```

**Use Phase 1 when:** You need to understand what a file does, find which file owns a feature,
or navigate the codebase without reading individual files.

**Escalate to Phase 2 when:** The summary is insufficient or no match found.

### Phase 2 -- Vector Store Semantic Search (Back-of-Book Index)

Embedding-based nearest-neighbor search across all indexed chunks. Returns ranked
parent chunks with RLM Super-RAG context pre-injected.

```bash
python3 plugins/vector-db/skills/vector-db-agent/scripts/query.py \
  "nearest-neighbor embedding search implementation" \
  --profile knowledge --limit 5
```

**Use Phase 2 when:** You need specific code snippets, patterns, or implementations.

**Escalate to Phase 3 when:** You have a file path (from Phase 1 or 2) and need an exact line.

### Phase 3 -- Grep / Exact Search (Ctrl+F)

Precise keyword or regex match. Always scope to paths discovered in earlier phases.

```bash
# Scoped to a specific path (use paths from Phase 1/2)
grep_search "VectorDBOperations" plugins/vector-db/skills/

# Ripgrep for regex
rg "def query" plugins/vector-db/ --type py
```

**Anti-patterns:** Never run a full-repo grep without scoping. Never skip Phase 1.

## Dependencies

### `rlm-factory` -- RLM Summary Ledger (Tier 2)

| Component | Value |
|:----------|:------|
| **Plugin** | `plugins/rlm-factory/` |
| **Skill (write)** | `skills/rlm-curator/` -- distill, inject, audit, cleanup |
| **Skill (read)** | `skills/rlm-search/` -- query the ledger |
| **Script: Phase 1 search** | `skills/rlm-search/scripts/query_cache.py` |
| **Script: inject summary** | `skills/rlm-curator/scripts/inject_summary.py` |
| **Script: audit coverage** | `skills/rlm-curator/scripts/inventory.py` |
| **Script: shared config** | `skills/rlm-curator/scripts/rlm_config.py` |
| **Cache files** | `.agent/learning/rlm_summary_cache.json` (docs), `.agent/learning/rlm_tool_cache.json` (tools) |

### `vector-db` -- Vector Store (Tier 3)

| Component | Value |
|:----------|:------|
| **Plugin** | `plugins/vector-db/` |
| **Skill** | `skills/vector-db-agent/` -- ingest, query, operations |
| **Script: Phase 2 search** | `skills/vector-db-agent/scripts/query.py` |
| **Script: ingest files** | `skills/vector-db-agent/scripts/ingest.py` |
| **Script: operations** | `skills/vector-db-agent/scripts/operations.py` |
| **Script: config** | `skills/vector-db-agent/scripts/vector_config.py` |
| **Backend** | ChromaDB (`chromadb.HttpClient` with `PersistentClient` fallback) |

## Promotion / Demotion Rules

### Promote to Hot Cache when:
- Knowledge is referenced in 3+ consecutive sessions
- It's critical for active work (current spec, active protocol)
- It's a constraint or identity anchor

### Demote to Deep Storage when:
- Spec/feature is completed and merged
- Governing document is superseded by newer version
- Topic research is concluded
- Technical decision is ratified (move from draft to archive)

### What Goes Where

| Type | Hot Cache | On-Demand Tier |
|------|-----------|----------------|
| Active tasks | Boot digest | -- |
| Identity/role | Primer file | -- |
| Constraints | Boot contract | -- |
| Session state | Snapshot file | Traces file |
| Research topics | Summary in snapshot | `domain_data_dir/{name}/` |
| Design decisions | Referenced by ID | `design_docs_dir/{id}_{name}.md` |
| Governing docs | Referenced by ID | `governance_dir/{id}_{name}.md` |
| Plugins/scripts/tools | -- | RLM Summary Ledger (tool cache) |
| Docs/protocols/research | -- | RLM Summary Ledger (summary cache) |
| System docs | -- | RLM Summary Ledger + Vector Store |
| Relational knowledge | -- | Linked Vault (e.g. Obsidian) |

## Session Memory Workflow

### At Session Start (Boot)
1. Load hot cache files in order (primer -> contract -> digest -> snapshot)
2. Integrity check validates snapshot is current
3. If snapshot stale -> flag for refresh at session end

### During Session
- **New learning** -> Write to `<domain_data_dir>/{topic}/`
- **New decision** -> Create design document draft
- **New tool** -> Register in tool inventory
- **Correction** -> Update relevant file + note in disputes log if contradicting

### At Session End (Seal)
1. Update snapshot file with new content learned this session
2. Seal validates no drift since last audit
3. Persist traces to external storage (if configured)

## Conventions
- **Hot cache target**: ~200 lines total across all boot files
- **Snapshot**: 1 sentence per file, machine-readable
- **Topic folders**: `lowercase-hyphens/`
- **Document numbering**: 3-digit, sequential
- **Always capture** corrections and contradictions in a disputes log

## Configuration

Projects configure the memory system by setting file paths in their project-specific plugin:

| Variable | Purpose |
|:---------|:--------|
| `MEMORY_PRIMER_FILE` | Path to cognitive primer / role definition |
| `MEMORY_BOOT_DIGEST` | Path to tactical boot digest |
| `MEMORY_BOOT_CONTRACT` | Path to immutable constraints |
| `MEMORY_SNAPSHOT_FILE` | Path to learning snapshot (hologram) |
| `MEMORY_DOMAIN_DIR` | Directory for domain research |
| `MEMORY_DESIGN_DIR` | Directory for design docs (e.g. ADRs) |
| `MEMORY_GOVERNANCE_DIR` | Directory for governing docs (e.g. Protocols) |

## Architecture Diagrams

| Diagram | What It Shows |
|:--------|:--------------|
| [memory_architecture.mmd](references/diagrams/architecture/memory_architecture.mmd) | Full 4-tier memory system with exact plugin/skill/script names per tier |
| [memory_lookup_flow.mmd](references/diagrams/architecture/memory_lookup_flow.mmd) | 3-phase search sequence: Hot Cache -> RLM Ledger -> Vector Store -> Grep |
| [memory_session_lifecycle.mmd](references/diagrams/architecture/memory_session_lifecycle.mmd) | Session Boot -> Active -> Seal lifecycle with all event types |

