---
concept: wiki-build
source: plugin-code
source_file: obsidian-wiki-engine/commands/wiki-build.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.639579+00:00
cluster: sources
content_hash: e4cc113c67a83fd3
---

# /wiki-build

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
description: "Build Karpathy-style wiki nodes from raw sources. Runs ingest → concept_extractor (cross-source synthesis) → wiki_builder. Merges multi-source concept records into authoritative nodes."
argument-hint: "[--source label] [--rlm-cache-dir path] [--dry-run]"
---

# /wiki-build

Runs the full wiki node build pipeline: ingest raw sources, extract and merge
concepts across sources, and format Karpathy-style wiki nodes.

## Quick Reference

```bash
# Build all stale/new nodes from all sources
/wiki-build

# Build from one named source only
/wiki-build --source arch-docs

# Build with shared .agent/learning/ RLM cache
/wiki-build --rlm-cache-dir .agent/learning/rlm_wiki_cache

# Dry run (plan without writing)
/wiki-build --dry-run
```

## Pipeline

```
raw sources (wiki_sources.json)
    ↓ ingest.py          — read files, hash for staleness, emit ParsedRecords
    ↓ concept_extractor  — group by concept slug, merge multi-source records
    ↓ wiki_builder.py    — format Karpathy nodes, build clusters + index
    ↓ {wiki-root}/wiki/  — output: {concept}.md, _index.md, _toc.md, _{cluster}.md
```

## Cross-Source Synthesis

When two sources contain files about the same concept, they are merged into
**one authoritative wiki node** listing both sources. This is the Karpathy
"compile" step: N raw files → M concept nodes (M ≤ N).

## Output Structure

```
{wiki-root}/wiki/
  _index.md         ← master concept index
  _toc.md           ← table of contents
  _{cluster}.md     ← per-topic cluster page
  {concept}.md      ← individual wiki node
```

## Recommended Sequence

```bash
/wiki-build      ← build nodes first
/wiki-distill    ← generate RLM summaries (needs nodes to exist)
/wiki-audit      ← structural health check
/wiki-lint       ← semantic health check (after ~20+ nodes)
```

See `skills/obsidian-wiki-builder/SKILL.md` for the full execution protocol.


## See Also

- [[obsidian-wiki-engine-plugin]]
- [[wiki-audit]]
- [[wiki-distill]]
- [[wiki-ingest]]
- [[wiki-init]]
- [[wiki-lint]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/commands/wiki-build.md`
- **Indexed:** 2026-04-17T06:42:09.639579+00:00
