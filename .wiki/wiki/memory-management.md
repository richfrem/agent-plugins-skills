---
concept: memory-management
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/memory-management_memory-management.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.322245+00:00
cluster: skill
content_hash: 1d798b5428fd40db
---

# Memory Management

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: memory-management
description: "Tiered memory system for cognitive continuity across agent sessions. Manages hot cache (session context loaded at boot) and deep storage (loaded on demand). Use when: (1) starting a session and loading context, (2) deciding what to remember vs forget, (3) promoting/demoting knowledge between tiers, (4) user says 'remember this' or asks about project history."
allowed-tools: Read, Write
---
# Memory Management

Tiered memory system that makes an AI agent a continuous collaborator across sessions.

## Architecture

The memory system has six tiers, configurable per project:

```
Tier 1: HOT CACHE (always loaded at boot -- ~200 lines target)
+-- <primer_file>             Role, identity, constraints
+-- <boot_digest_file>        Tactical status, active tasks
+-- <boot_contract_file>      Immutable constraints
+-- <snapshot_file>           Cognitive Hologram (1 sentence per file)

Tier 2: RLM SUMMARY LEDGER (fast keyword lookup -- loaded on demand)
+-- <summary_cache_file>      Pre-generated text summaries: docs, protocols, research
                              Plugin: rlm-factory | Skill: rlm-search | Profile: project
+-- <tool_cache_file>         Pre-generated text summaries: plugins, skills, scripts
                              Plugin: rlm-factory | Skill: rlm-search | Profile: tools

Tier 3: VECTOR STORE (semantic embedding search -- loaded on demand)
+-- <vector_db_backend>       ChromaDB via vector-db plugin / vector-db-agent skill
                              Profile: knowledge | Port: configured in vector_profiles.json

Tier 4: DEEP STORAGE (filesystem -- authoritative source, loaded on demand)
+-- <domain_data_dir>/        Research topics: {topic}/analysis.md
+-- <design_docs_dir>/        ADRs, RFCs
+-- <governance_dir>/         Protocols, playbooks

Tier 5: VAULT (Obsidian -- linked knowledge graph, loaded on demand)
+-- <vault_dir>/              Plugin: obsidian-integration
                              Skills: obsidian-vault-crud, obsidian-canvas-architect,
                                      obsidian-graph-traversal, obsidian-bases-manager
                              Env: VAULT_PATH or OBSIDIAN_VAULT_PATH

Tier 6: SOUL (external persistence -- optional, synced at session seal)
+-- <traces_file>             Plugin: project-specific (e.g. huggingface-utils)
                              e.g. lineage/, data/, soul_traces.jsonl on HF Hub
```

Projects define their own file paths for each slot. Tiers may be omitted or added based on project complexity.

## Lookup Flow (3-Phase Search Protocol)

When searching for information, ALWAYS escalate in order. Never skip ahead.

```
Query arrives ->
1. HOT CACHE                     Instant. Boot files cover ~90% of context needs.
2. DEEP STORAGE (topic/decision) Load specific domain dir or design doc by subject.
3. RLM SUMMARY LEDGER (Phase 1)  Keyword search via rlm-factory:rlm-search skill.
4. VECTOR STORE (Phase 2)        Semantic search via vector-db:vector-db-search skill.
5. GREP / EXACT SEARCH (Phase 3) rg/grep scoped to paths from Steps 3 or 4.
6. Ask user                      Unknown? Learn it and persist it.
```

### Phase 1 -- RLM Summary Scan (Table of Contents)

RLM is **amortized prework**: each file read ONCE, summarized ONCE, cached as plain text JSON.
Searching summaries is O(1) keyword lookup -- no embeddings, no inference.

Trigger the `rlm-factory:rlm-search` skill, providing the profile and search term.

**Use Phase 1 when:** You need to understand what a file does, find which file owns a feature,
or navigate the codebase without reading individual files.

**Escalate to Phase 2 when:** The summary is insufficient or no match found.

### Phase 2 -- Vector Store Semantic Search (Back-of-Book Index)

Embedding-based nearest-neighbor search across all indexed chunks. Returns ranked
parent chunks with RLM Super-RAG context pre-injected.

Trigger the `vector-db:vector-db-search` skill, providing the query, profile, and l

*(content truncated)*

## See Also

- [[memory-management-plugin]]
- [[acceptance-criteria-memory-management]]
- [[procedural-fallback-tree-memory-management]]
- [[acceptance-criteria-memory-management]]
- [[procedural-fallback-tree-memory-management]]
- [[acceptance-criteria-memory-management]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/memory-management_memory-management.md`
- **Indexed:** 2026-04-17T06:42:10.322245+00:00
