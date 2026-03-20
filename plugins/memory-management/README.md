# Memory Management Plugin 🧠

Tiered memory system for cognitive continuity across agent sessions. Makes AI agents
continuous collaborators -- they carry context between sessions instead of starting blank.

## Installation
### Option 1: Skills Only (End Users)
```bash
npx skills add ./plugins/memory-management
```
This installs the skills from this plugin.

### Option 2: Full Deployment (Skills + Commands + Agents)
For complete access to all components, use the bridge-plugin skill:
```bash
# Use the bridge-plugin skill to deploy all components
# python ./plugins/plugin-manager/scripts/bridge_installer.py --plugin plugins/memory-management
```

## Architecture

Memory is organized into four tiers, loaded progressively based on need:

```
HOT CACHE (always loaded at boot -- ~200 lines total)
+--> <primer_file>          Role, identity, constraints
+--> <boot_digest_file>     Tactical status, active tasks
+--> <boot_contract_file>   Immutable constraints
+--> <snapshot_file>        Cognitive Hologram (1 sentence per file)

SEMANTIC CACHE (fast, O(1) lookup -- loaded on demand)
+--> <summary_cache_file>   RLM summaries: docs, READMEs, research
+--> <tool_cache_file>      RLM summaries: plugins, skills, scripts

VECTOR STORE (semantic search -- loaded on demand)
+--> <vector_db_backend>    ChromaDB via vector-db plugin

DEEP STORAGE (authoritative source -- loaded on demand)
+--> <domain_data_dir>/     Research topics: {topic}/analysis.md
+--> <design_docs_dir>/     ADRs, RFCs
+--> <governance_dir>/      Protocols, playbooks
+--> <vault_dir>/           Linked knowledge graph (Obsidian)
+--> <traces_file>          External persistent log (HuggingFace)
```

## Lookup Flow

```
Query arrives ->
1. Hot cache (boot files)        ~90% of context needs, instant
2. Topics directory              Deep knowledge by subject
3. Decisions directory           Architecture decisions
4. Semantic cache (rlm-factory)  Tool/script/plugin discovery
5. Vector store (vector-db)      Semantic content search
6. Ask user                      Unknown? Learn it.
```

## Use Cases

Use this plugin when:
1. Starting a session and loading context
2. Deciding what to remember vs forget
3. Promoting/demoting knowledge between tiers
4. The user says "remember this" or asks about project history

## Skills

| Skill | Purpose |
|:------|:--------|
| **memory-management** | Primary skill: ingest, retrieve, and manage long-term context |

## Dependencies

| Plugin | Why |
|:-------|:----|
| `rlm-factory` | Provides Recursive Language Model (RLM) Summary Ledger via `rlm-factory:rlm-search` and `rlm-factory:rlm-distill-agent` skills |
| `vector-db` | Provides Vector Store tier (ChromaDB semantic search) |
| `obsidian-integration` | Provides Vault tier (Tier 5) -- read/write Obsidian notes via `obsidian-integration:obsidian-vault-crud` skill |

## Promotion / Demotion Rules

**Promote to Hot Cache when:**
- Referenced in 3+ consecutive sessions
- Critical for active work (current spec, active protocol)
- Constraint or identity anchor

**Demote to Deep Storage when:**
- Feature merged and closed
- Document superseded
- Research concluded
- Decision ratified

## Configuration

Projects set file paths via environment variables or project-local config:

| Variable | Purpose |
|:---------|:--------|
| `MEMORY_PRIMER_FILE` | Cognitive primer / role definition |
| `MEMORY_BOOT_DIGEST` | Tactical boot digest |
| `MEMORY_BOOT_CONTRACT` | Immutable constraints |
| `MEMORY_SNAPSHOT_FILE` | Learning snapshot (hologram) |
| `MEMORY_DOMAIN_DIR` | Domain research directory |
| `MEMORY_DESIGN_DIR` | Design docs directory (ADRs) |
| `MEMORY_GOVERNANCE_DIR` | Governing docs directory (Protocols) |

## Structure

```
memory-management/
+-- .claude-plugin/
|   +-- plugin.json        # Plugin manifest + dependencies
+-- skills/
|   +-- memory-management/
|       +-- SKILL.md       # Full tiered memory protocol
+-- README.md
```

## Plugin Components

### Skills
- `memory-management`

### Dependencies
- `rlm-factory`
- `vector-db`
- `obsidian-integration`

