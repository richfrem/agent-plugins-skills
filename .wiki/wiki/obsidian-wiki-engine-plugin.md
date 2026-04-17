---
concept: obsidian-wiki-engine-plugin
source: plugin-code
source_file: obsidian-wiki-engine/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.633486+00:00
cluster: plugin-code
content_hash: b5230afef64fbc5e
---

# Obsidian Wiki Engine Plugin

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
    ↓ {wiki-root}/wiki/  — {concept}.md, _index

*(content truncated)*

## See Also

- [[plugin-dependencies-obsidian-wiki-engine]]
- [[obsidian-wiki-builder]]
- [[obsidian-wiki-linter]]
- [[adr-manager-plugin]]
- [[optimizer-engine-patterns-reference-design]]
- [[test-scenario-bank-agentic-os-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/README.md`
- **Indexed:** 2026-04-17T06:42:09.633486+00:00
