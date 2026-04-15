---
description: "Audit the Obsidian LLM wiki for orphaned nodes, missing RLM summaries, stale source files, and broken wikilinks. Reports health metrics and a prioritized fix list."
argument-hint: "[--wiki-root <path>] [--fix-stale] [--json]"
allowed-tools: Bash, Read, Write
---

# /wiki-audit

Audits the wiki for orphans, missing summaries, and stale content.

## Usage

```bash
# Full audit report
/wiki-audit

# Audit with auto-fix for stale agent-memory entries
/wiki-audit --fix-stale

# JSON output for programmatic processing
/wiki-audit --json
```

## Checks Performed

| Check | Description |
|:------|:------------|
| Missing summaries | Wiki nodes with no `rlm/{concept}/summary.md` |
| Stale nodes | Source files changed since last ingest (via hash in `agent-memory.json`) |
| Orphan nodes | Wiki nodes whose source file no longer exists |
| Broken wikilinks | `[[links]]` pointing to non-existent concept pages |
| Missing sources | Paths in `wiki_sources.json` that no longer exist on disk |

## Output Example

```
[AUDIT] Wiki Root: /path/to/wiki-root
[OK]    Total nodes: 47
[WARN]  Missing RLM summaries: 12  → run /wiki-distill
[WARN]  Stale nodes: 3             → run /wiki-ingest
[ERROR] Orphan nodes: 1            → source file deleted
[OK]    Broken wikilinks: 0
[OK]    All registered sources exist on disk
```

## Under the Hood

```bash
python ./scripts/audit.py --wiki-root {wiki_root} [options]
```
