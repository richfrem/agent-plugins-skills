---
description: "Parse all registered raw source directories and build Karpathy-style wiki nodes. Reads wiki_sources.json to discover sources, runs ingest.py + wiki_builder.py, and writes wiki nodes into wiki-root/wiki/."
argument-hint: "[--source <name>] [--dry-run]"
allowed-tools: Bash, Read, Write
---

# /wiki-ingest

Parses all raw source directories from `wiki_sources.json` and builds Karpathy-style wiki nodes.

## Usage

```bash
# Ingest all registered sources
/wiki-ingest

# Ingest one named source only
/wiki-ingest --source arch-docs

# Dry run — show what would be created without writing
/wiki-ingest --dry-run
```

## Under the Hood

```bash
python ./scripts/ingest.py --wiki-root {wiki_root}
python ./scripts/wiki_builder.py --wiki-root {wiki_root}
```

`ingest.py` reads each file listed by `WikiSourceConfig`, normalizes it,
and outputs a parsed record. `wiki_builder.py` formats these into Karpathy
wiki nodes and writes `wiki/{concept}.md` + updates `_index.md` and `_toc.md`.

## Prerequisites

- `/wiki-init` must have been run (wiki_sources.json must exist)
- Raw source directories must be accessible at the registered paths

## Output

```
{wiki-root}/wiki/
  _index.md        ← updated master concept index
  _toc.md          ← updated table of contents
  _{cluster}.md    ← cluster pages (one per topic group)
  {concept}.md     ← one page per concept
```

## Next Steps

```bash
/wiki-distill   ← generate RLM summaries for the new nodes
/wiki-query     ← query the populated wiki
```
