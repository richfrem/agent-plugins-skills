# Obsidian Wiki Engine Plugin

**Karpathy-style LLM Wiki with Super-RAG retrieval stack.**

Transforms raw markdown sources into a structured, queryable knowledge base using
cross-source concept synthesis, RLM summaries, and optional vector-db semantic search.
Inspired by Karpathy's LLM Wiki: raw → compile → query → file outputs back.

## Start Here

**Skills run from `.agents/skills/` (the deployed runtime), not from `plugins/`.**
The `plugins/` directory is the source repo — skills there are inactive until installed.

```bash
# Verify this plugin is installed and active
ls .agents/skills/obsidian-wiki-builder/   # should exist
ls .agents/agents/wiki-init-agent.md        # should exist

# If missing — install via:
uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills
# or: npx skills add richfrem/agent-plugins-skills
# or: see INSTALL.md
```

**To initialize:** invoke `wiki-init-agent` (or say "initialize wiki" / "set up my wiki").

## Standalone vs Combined

**This plugin works completely standalone.** No other plugins required for core wiki functionality.

| Mode | What you get | External deps required |
|:-----|:-------------|:-----------------------|
| **A — Wiki only** | `/wiki-build`, `/wiki-query` with grep search, concept synthesis | None |
| **B — Wiki + RLM** | + `/wiki-distill`, RLM keyword pre-filter in queries | `rlm-factory` in `.agents/` |
| **C — Wiki + Vector** | + semantic Phase 2 search in `/wiki-query` | `vector-db` in `.agents/` |
| **D — Full Super-RAG** | All three phases: keyword → semantic → concept node | Both above |

The `wiki-init-agent` asks which mode you want upfront and only provisions what's needed.
Use `super-rag-setup-agent` if you want all three plugins configured in one session.

## The Super-RAG Value Proposition (Why Mode D?)

Standard AI assistants and basic RAG systems often operate context-blind at query time — they chop files into random chunks, run basic semantic searches, and try to guess answers from fragmented paragraphs. They hallucinate, miss architectural rules, and fail on complex questions. 

By combining all three layers in **Mode D (Full Super-RAG)**, you eliminate these blind spots and transform the repository into an **Active Cognitive Graph**:

1. **Layer 1: The RLM Cache (`rlm-factory`) — The "Why"**
   Indexes raw code by explicitly writing out its purpose, dependencies, and rules. When injected into the Vector DB, scattered code chunks become highly dense, pre-summarized knowledge. This practically eliminates AI hallucination.
   *(O(1) keyword lookup across dense summaries)*
2. **Layer 2: The Vector DB (`vector-db`) — The "Where"**
   Maps searches to intent rather than requiring exact grep keywords. By ingesting the rich RLM summaries, the semantic search understands the concept behind your query and pulls the right, highly accurate context needle from the haystack.
   *(O(log N) semantic embedding search)*
3. **Layer 3: The LLM Wiki (`obsidian-wiki-engine`) — The "Synthesized Whole"**
   Code is organized for compilers; human knowledge is organized by concepts. The Wiki Engine connects the fragmented dots across raw code and RLM summaries to pre-compute Karpathy-style Concept Nodes offline. 
   *(Karpathy-style full concept nodes)*

**The Result:** It pre-computes the "Senior Staff Architect" understanding of the codebase. Instead of dragging 30 massive source files into a context window, the AI quickly reads the synthesized concept nodes and RLM pre-filters. Every future query is lightning-fast, highly token-efficient, and dead-accurate to your specific ecosystem rules.


## Core Pipeline

```
raw sources (rlm_wiki_raw_sources_manifest.json)
    ↓ ingest.py          — read files, hash for staleness, emit ParsedRecords
    ↓ concept_extractor  — group by concept slug, merge multi-source records
    ↓ wiki_builder.py    — format Karpathy nodes, build clusters + index
    ↓ {wiki-root}/wiki/  — {concept}.md, _index.md, _toc.md, _{cluster}.md
```

**Cross-source synthesis**: when two sources contain files about the same concept, they merge
into one authoritative wiki node. N raw files → M concept nodes (M ≤ N).

## Quick Start

```bash
# 1. Initialize (guided wizard — creates all config files)
/wiki-init

# 2. Build wiki nodes
/wiki-build

# 3. Generate RLM summaries
/wiki-distill

# 4. Query
/wiki-query "attention mechanism"

# 5. Health check
/wiki-audit        # structural (orphans, broken links)
/wiki-lint         # semantic (inconsistencies, gaps, stale articles)
```

## Config Files (canonical location: `.agent/learning/`)

| File | Purpose |
|:-----|:--------|
| `rlm_wiki_raw_sources_manifest.json` | Raw content sources registry |
| `rlm_profiles.json` | RLM distillation profiles (wiki profile) |
| `rlm_wiki_cache.json` | Distilled RLM summaries for wiki nodes |
| `vector_profiles.json` | Vector-db profiles (wiki profile, optional) |

## Skills

| Skill | Purpose |
|:------|:--------|
| **obsidian-wiki-builder** | Build Karpathy wiki nodes from raw sources |
| **obsidian-rlm-distiller** | Generate RLM summary layers for wiki nodes |
| **obsidian-query-agent** | 3-phase wiki query (RLM → vector → grep) |
| **obsidian-wiki-linter** | Semantic health check (inconsistencies, gaps, stale articles) |
| **obsidian-init** | Obsidian vault initialization and configuration |
| **obsidian-vault-crud** | Safe read/write/delete with atomic locks |
| **obsidian-markdown-mastery** | Strict Obsidian syntax parsing (wikilinks, callouts) |
| **obsidian-canvas-architect** | Programmatic JSON Canvas creation |
| **obsidian-graph-traversal** | Wikilink connection graph analysis |
| **obsidian-bases-manager** | Dynamic Obsidian Bases (.base) manipulation |

## Agents

| Agent | Purpose |
|:------|:--------|
| **wiki-init-agent** | Guided wizard: sources, wiki-root, rlm/vector profile provisioning |
| **super-rag-setup-agent** | Full 3-plugin orchestrator: rlm-factory + vector-db + obsidian-wiki-engine |
| **wiki-build-agent** | Pointer to obsidian-wiki-builder SKILL.md |
| **wiki-distill-agent** | Pointer to obsidian-rlm-distiller SKILL.md |
| **wiki-query-agent** | Pointer to obsidian-query-agent SKILL.md |
| **wiki-lint-agent** | Pointer to obsidian-wiki-linter SKILL.md |

## Commands

| Command | Description |
|:--------|:------------|
| `/wiki-init` | Initialize wiki root, sources manifest, optional rlm/vector profiles |
| `/wiki-build` | Full build: ingest → concept synthesis → wiki nodes |
| `/wiki-distill` | Generate RLM summary layers (summary, bullets, full) |
| `/wiki-query` | Query the wiki — 3-phase search with optional `--save-as` |
| `/wiki-audit` | Structural health check (orphans, missing summaries, broken wikilinks) |
| `/wiki-lint` | Semantic health check (inconsistencies, gaps, stale articles) |
| `/wiki-ingest` | Ingest raw sources only (no formatting) |
| `/wiki-rebuild` | Full rebuild from scratch |
| `/obsidian-init` | Initialize Obsidian vault configuration |

## Output Structure

```
{wiki-root}/
  wiki/
    _index.md           master concept index
    _toc.md             table of contents
    _{cluster}.md       per-topic cluster page
    {concept}.md        individual wiki node
  rlm/
    {concept}.json      RLM summary layers per concept
  meta/
    config.yaml         wiki configuration
    agent-memory.json   concept to source file mapping
    lint-report.md      most recent /wiki-lint output
```

## Dependencies

| Dependency | Required for | Must be installed at |
|:-----------|:-------------|:---------------------|
| `pip:ruamel.yaml` | All modes — YAML parsing | `pip install ruamel.yaml` |
| `rlm-factory` | Modes B + D — `/wiki-distill`, RLM keyword search | `.agents/skills/rlm-init/` |
| `vector-db` | Modes C + D — vector Phase 2 in `/wiki-query` | `.agents/skills/vector-db-init/` |

```bash
# Always required
pip install ruamel.yaml

# Check what's installed in .agents/
ls .agents/skills/ | grep -E "rlm-init|vector-db-init"
```

**Mode A (wiki only) has zero external plugin dependencies.**

## Recommended Workflow

```bash
/wiki-build      # build nodes first
/wiki-distill    # generate RLM summaries (needs nodes to exist)
/wiki-audit      # structural health check
/wiki-lint       # semantic health check (after ~20+ nodes)
```

For full Super-RAG setup (all 3 plugins at once), use `super-rag-setup-agent`.
