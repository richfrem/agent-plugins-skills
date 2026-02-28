---
name: memory-management
description: "Tiered memory system for cognitive continuity across agent sessions. Manages hot cache (session context loaded at boot) and deep storage (loaded on demand). Use when: (1) starting a session and loading context, (2) deciding what to remember vs forget, (3) promoting/demoting knowledge between tiers, (4) user says 'remember this' or asks about project history."
---

# Memory Management

Tiered memory system that makes an AI agent a continuous collaborator across sessions.

## Architecture

The memory system has two tiers, configurable per project:

```
HOT CACHE (always loaded at boot)
├── <primer_file>             ← Role, identity, constraints
├── <boot_digest_file>        ← Tactical status, active tasks
├── <boot_contract_file>      ← Immutable constraints
└── <snapshot_file>           ← Cognitive Hologram (1-line per file)

SEMANTIC CACHE (fast lookup, loaded on demand)
├── <summary_cache_file>      ← RLM summaries for project specific key content, documentation , etc. 
└── <tool_cache_file>         ← RLM summaries for plugins/skills/scripts/tools

VECTOR STORE (semantic search, loaded on demand)
└── <vector_db_backend>       ← e.g. ChromaDB via vector-db plugin

DEEP STORAGE (loaded on demand)
├── <domain_data_dir>/        ← E.g. Research, topics
│   └── {topic}/analysis.md   ← Deep dives
├── <design_docs_dir>/        ← E.g. ADRs, RFCs
├── <governance_dir>/         ← E.g. Protocols, playbooks
├── <vault_dir>/              ← Linked knowledge graph (e.g. Obsidian)
└── <traces_file>             ← Persistent external logging (e.g. HuggingFace)
```

Projects define their own file paths for each slot. The pattern is universal and projects may omit or add tiers depending on their complexity.

## Lookup Flow

```
Query arrives → 
1. Check hot cache (boot files)         → Covers ~90% of context needs
2. Check topics directory               → Deep knowledge by subject
3. Check decisions directory            → Architecture decisions  
4. Query semantic cache (if available)  → Tool/script discovery
5. Ask user                             → Unknown? Learn it.
```

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

| Type | Hot Cache | Deep Storage |
|------|-----------|-------------|
| Active tasks | Boot digest | — |
| Identity/role | Primer file | — |
| Constraints | Boot contract | — |
| Session state | Snapshot file | Traces file |
| Research topics | Summary in snapshot | `domain_data_dir/{name}/` |
| Design decisions | Referenced by ID | `design_docs_dir/{id}_{name}.md` |
| Governing docs | Referenced by ID | `governance_dir/{id}_{name}.md` |
| Tools/scripts | — | Semantic Cache (RLM) |
| System docs | — | Semantic Cache (RLM) / Vector Store |
| Relational knowledge | — | Linked Vault (e.g. Obsidian) |

## Session Memory Workflow

### At Session Start (Boot)
1. Load hot cache files in order
2. Integrity check validates snapshot
3. If snapshot stale → flag for refresh at session end

### During Session
- **New learning** → Write to `<domain_data_dir>/{topic}/`
- **New decision** → Create design document draft
- **New tool** → Register in tool inventory
- **Correction** → Update relevant file + note in disputes log if contradicting

### At Session End (Seal)
1. Update snapshot file with new content
2. Seal validates no drift since last audit
3. Persist traces to external storage (if configured)

## Conventions
- **Hot cache target**: ~200 lines total across boot files
- **Snapshot**: 1 sentence per file, machine-readable
- **Topic folders**: `lowercase-hyphens/`
- **Document numbering**: 3-digit, sequential
- **Always capture** corrections and contradictions in a disputes log

## Configuration

Projects configure the memory system by setting file paths in their project-specific plugin. Example env vars:

| Variable | Purpose |
|---|---|
| `MEMORY_PRIMER_FILE` | Path to cognitive primer / role definition |
| `MEMORY_BOOT_DIGEST` | Path to tactical boot digest |
| `MEMORY_BOOT_CONTRACT` | Path to immutable constraints |
| `MEMORY_SNAPSHOT_FILE` | Path to learning snapshot |
| `MEMORY_DOMAIN_DIR` | Directory for domain research |
| `MEMORY_DESIGN_DIR` | Directory for design docs (e.g. ADRs) |
| `MEMORY_GOVERNANCE_DIR` | Directory for governing docs (e.g. Protocols) |
