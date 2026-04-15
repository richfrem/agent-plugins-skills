---
description: "Full rebuild of the LLM wiki from scratch: re-reads all registered raw sources, rebuilds all wiki nodes, and refreshes all RLM summaries. Use after major content changes."
argument-hint: "[--source <name>] [--skip-distill]"
allowed-tools: Bash, Read, Write
---

# /wiki-rebuild

Full pipeline rebuild: ingest + build + distill.

## Usage

```bash
# Full rebuild (ingest + build + distill)
/wiki-rebuild

# Rebuild one source only
/wiki-rebuild --source arch-docs

# Skip distillation (rebuild wiki structure only)
/wiki-rebuild --skip-distill
```

## Pipeline

```
/wiki-ingest   → parse raw sources, build wiki nodes
/wiki-distill  → refresh all RLM summaries
/wiki-audit    → report orphans and missing summaries
```

Equivalent to running:

```bash
python ./scripts/ingest.py --wiki-root {wiki_root}
python ./scripts/wiki_builder.py --wiki-root {wiki_root}
python ./scripts/distill_wiki.py --wiki-root {wiki_root}
python ./scripts/audit.py --wiki-root {wiki_root}
```

## When to Use

- After adding new registered sources to `wiki_sources.json`
- After large content updates across multiple source folders
- When `agent-memory.json` reports many stale files
- Initial population after `/wiki-init`
