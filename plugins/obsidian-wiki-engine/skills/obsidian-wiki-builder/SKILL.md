---
name: obsidian-wiki-builder
plugin: obsidian-wiki-engine
description: "Transforms raw source files registered in wiki_sources.json into Karpathy-style LLM wiki nodes inside the wiki-root. Generates concept pages, cluster pages, index, and table of contents. Use when building or rebuilding the wiki from raw content."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires `pyyaml` and Python 3.8+. Also requires `rlm-factory` plugin installed.

```bash
pip install -r requirements.txt
```

---
# Obsidian Wiki Builder

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** Obsidian Wiki Engine

## Purpose

Transforms raw source documents (registered via `wiki_sources.json`) into
**Karpathy-style wiki nodes** inside the designated `wiki_root`. Each concept
gets its own `{concept}.md` node with wikilinks, cross-references, and an
RLM summary layer.

## Output Layout (Rigid)

```
{wiki_root}/
  wiki/
    _index.md          ← master concept index
    _toc.md            ← table of contents
    _{cluster}.md      ← per-topic cluster page
    {concept}.md       ← individual wiki node
  rlm/
    {concept}/
      summary.md       ← 1-5 sentence distilled summary
      bullets.md       ← key idea bullets
      deep.md          ← full multi-pass distillation
  meta/
    wiki_sources.json  ← raw source registry (created by wiki-init)
    config.yaml        ← wiki settings
    agent-memory.json  ← stale file tracking
```

## Build Pipeline

`wiki_builder.py` runs a 3-step pipeline internally:

```
ingest.py  →  concept_extractor.py  →  wiki node formatting
```

1. **ingest.py**: Reads raw source files, normalizes content, hashes for staleness detection
2. **concept_extractor.py**: Groups records by concept slug, **merges multi-source records**
   into one authoritative node (the Karpathy "compile" step), improves cluster assignment
   via keyword extraction
3. **wiki node formatting**: Renders merged records into Karpathy-format `.md` files
   with wikilinks, cluster pages, `_index.md`, and `_toc.md`

## Multi-Source Concept Merging

When two source files (e.g. `arch-docs/auth.md` and `research/oauth.md`) produce
the same concept slug, they are merged into **one wiki node** that:
- Combines content from all sources with attribution headers
- Lists all source files in `source_files` frontmatter
- Re-derives the cluster from combined content keywords
- Sets `multi_source: true` for identification

This implements the core Karpathy "compile" metaphor: N raw files → M concept nodes (M ≤ N).

## Usage

### Build wiki nodes from all registered sources
```bash
python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root
```

### Build from one named source only
```bash
python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root --source arch-docs
```

### Use shared .agent/learning/ RLM cache for existing summaries
```bash
python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root \
    --rlm-cache-dir /path/to/project/.agent/learning/rlm_wiki_cache
```

### Dry run (plan without writing)
```bash
python ./scripts/wiki_builder.py --wiki-root /path/to/wiki-root --dry-run
```

## Karpathy Wiki Node Format

Each concept node uses this structure:

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

- {bullet}
- {bullet}

## Details

{full content, truncated to 800 tokens if needed}

## See Also

- [[{related_concept_1}]]
- [[{related_concept_2}]]

## Raw Source

- `{source_label}` → `{source_file}`
```

## Source Registry Format (`rlm_wiki_raw_sources_manifest.json`)

Canonical location: `.agent/learning/rlm_wiki_raw_sources_manifest.json`
(mirrors rlm-factory's `.agent/learning/rlm_profiles.json` convention).

Managed by `raw_manifest.py` via the Guided Discovery agent during `/wiki-init`:

```json
{
  "namespace": "my-project",
  "wiki_root": "/Users/me/vault/wiki-root",
  "sources": {
    "daily-notes": {
      "path": "/Users/me/vault/notes",
      "label": "daily-notes",
      "extensions": [".md"],
      "excludes": ["_archive", "*.tmp"],
      "description": "Daily journal and quick capture notes"
    },
    "arch-docs": {
      "path": "/Users/me/docs/architecture",
      "label": "arch-docs",
      "extensions": [".md", ".txt"],
      "excludes": [],
      "description": "Architecture decision records and design docs"
    }
  },
  "global_excludes": ["_archive", "*.tmp", "__pycache__"]
}
```

## When to Use

- After `/wiki-init` completes source registration
- After adding new raw source documents
- After running `/wiki-distill` to inject fresh RLM summaries
- When the wiki index is stale (`agent-memory.json` shows diffs)

## Related Scripts

- `raw_manifest.py` — `WikiSourceConfig` loader (mirrors `RLMConfig`)
- `ingest.py` — raw file parsing and normalization
- `wiki_builder.py` — Karpathy node formatter and linker
- `distill_wiki.py` — cheap-model distillation wrapper
