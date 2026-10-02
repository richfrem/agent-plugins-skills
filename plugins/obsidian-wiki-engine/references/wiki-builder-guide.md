# Obsidian Wiki Builder Guide

## Contents
- [Output Layout Specification](#output-layout-specification)
- [3-Stage Build Pipeline](#3-stage-build-pipeline)
- [Multi-Source Concept Merging](#multi-source-concept-merging)
- [Karpathy Node Markdown Schema](#karpathy-node-markdown-schema)
- [Source Manifest Schema](#source-manifest-schema)

---

## Output Layout Specification

A fully-built wiki root contains three top-level directories:

```
{wiki_root}/
  wiki/
    _index.md          <- Master concept index
    _toc.md            <- Table of contents
    _{cluster}.md      <- Per-topic cluster page
    {concept}.md       <- Individual wiki node
  rlm/
    {concept}/
      summary.md       <- 1-5 sentence distilled summary
      bullets.md       <- Key idea bullets
      deep.md          <- Full multi-pass distillation
  meta/
    wiki_sources.json  <- Raw source registry (from wiki-init)
    config.yaml        <- Wiki configuration settings
    agent-memory.json  <- State and hash tracking
```

---

## 3-Stage Build Pipeline

`wiki_builder.py` runs three sequential stages:

1. **`ingest.py`**: Scans raw source files, normalizes markdown text, and generates SHA256 hashes for staleness detection.
2. **`concept_extractor.py`**: Groups records by concept slug and merges multi-source records into authoritative concepts.
3. **Wiki Node Formatting**: Renders merged records into Karpathy-format markdown files with bidirectional wikilinks.

---

## Multi-Source Concept Merging

When multiple source files yield the same concept slug, the compiler merges them into one authoritative node:
- Merges content with source attribution headers.
- Records all originating files in `source_files` frontmatter array.
- Recalculates topic cluster from combined keyword density.
- Flags `multi_source: true` for downstream audits.

---

## Karpathy Node Markdown Schema

```markdown
---
concept: {concept_name}
source: {source_label}
source_file: {relative_path}
wiki_root: {wiki_root}
generated_at: {timestamp}
cluster: {cluster_name}
---

# {Concept Name}

{1-sentence RLM summary}

## Key Ideas
- {bullet_1}
- {bullet_2}

## Details
{full_content}

## See Also
- [[{related_concept_1}]]
- [[{related_concept_2}]]

## Raw Source
- `{source_label}` -> `{source_file}`
```

---

## Source Manifest Schema

Location: `.agent/learning/rlm_wiki_raw_sources_manifest.json`

```json
{
  "namespace": "project-name",
  "wiki_root": "/path/to/wiki-root",
  "sources": {
    "arch-docs": {
      "path": "/path/to/docs",
      "label": "arch-docs",
      "extensions": [".md"],
      "excludes": ["_archive"],
      "description": "Architecture records"
    }
  },
  "global_excludes": ["_archive", "*.tmp", "__pycache__"]
}
```
