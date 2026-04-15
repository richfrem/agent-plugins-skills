---
name: obsidian-query-agent
description: "Progressive-disclosure query against the Obsidian LLM wiki. Returns RLM summary first, expands to bullets, then full wiki node on demand. Use when looking up concepts, searching the wiki, or getting instant context from the knowledge graph."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ and pyyaml.

```bash
pip install -r requirements.txt
```

---
# Obsidian Query Agent

**Status:** Active
**Author:** Richard Fremmerlid
**Domain:** Obsidian Wiki Engine

## Purpose

Progressive-disclosure query interface for the Obsidian LLM wiki. Returns the
**cheapest useful answer first**: a 1-5 sentence RLM summary. The caller can
then request bullets, then the full wiki node — expanding context only as needed.

## Progressive Disclosure Levels

| Level | Content | Cost |
|:------|:--------|:-----|
| `summary` | 1-5 sentence distilled answer | ~50 tokens |
| `bullets` | 6-10 key idea bullets | ~150 tokens |
| `full` | Complete wiki node + wikilinks | ~800 tokens |
| `raw` | Original source file content | variable |

## Usage

### Quick summary (default)
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow"
```

### Bullet-level detail
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow" --level bullets
```

### Full wiki node
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "authentication flow" --level full
```

### List all indexed concepts
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root --list
```

### JSON output (for programmatic use)
```bash
python ./scripts/query_wiki.py --wiki-root /path/to/wiki-root "api design" --json
```

## Search Strategy

1. Exact concept name match in `wiki/_index.md`
2. Fuzzy label match across all concept nodes
3. Full-text keyword scan of `wiki/*.md` summaries
4. Falls back to `rlm/` summary layer if wiki node is missing

## When to Use

- Any time you need fast context about a concept in the wiki
- Before reading a full raw source file (use summary first)
- When `/wiki-ingest` has been run and nodes are populated
- As a pre-flight check before expensive agent operations

## Related Scripts

- `query_wiki.py` — progressive-disclosure query engine
- `raw_manifest.py` — `WikiSourceConfig` for path resolution
- `audit.py` — reports missing or stale nodes
