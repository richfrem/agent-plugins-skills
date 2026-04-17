---
concept: obsidian-wiki-builder
source: plugin-code
source_file: obsidian-wiki-engine/skills/obsidian-wiki-builder/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.658238+00:00
cluster: source
content_hash: fed0b40db6e53316
---

# Obsidian Wiki Builder

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: obsidian-wiki-builder
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
  "sour

*(content truncated)*

## See Also

- [[obsidian-wiki-engine-plugin]]
- [[plugin-dependencies-obsidian-wiki-engine]]
- [[obsidian-wiki-linter]]
- [[acceptance-criteria-prototype-builder]]
- [[obsidian-integration-architecture-background]]
- [[kepano-obsidian-skills-analysis-summary]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `obsidian-wiki-engine/skills/obsidian-wiki-builder/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.658238+00:00
