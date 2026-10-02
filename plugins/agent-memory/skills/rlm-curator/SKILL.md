---
name: rlm-curator
plugin: agent-memory
description: Knowledge Curator agent skill for maintaining RLM semantic ledger hygiene, batch distillation, coverage auditing, and cache cleanup.
allowed-tools: Bash, Read, Write
---

# RLM Knowledge Curator (`rlm-curator`)

Maintains the Recursive Language Model (RLM) semantic ledger accurate and up to date across all project profiles.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Curatorial Tools](#curatorial-tools)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Scripted Writes Only**: Never edit cache markdown files directly; always use `inject_summary.py` or `swarm_run.py`.
2. **Search Delegation**: For querying the cache, invoke the `rlm-search` skill with `query_cache.py`.
3. **Zero-Dependency Core**: Standard library Python 3.8+ only; no external databases needed.

## Quick start

Run an initial coverage inventory assessment across the default profile:

```bash
python3 scripts/inventory.py --profile project
```

## Workflow

1. **Coverage Assessment**: Run `inventory.py` to identify unindexed files or coverage gaps.
2. **Distillation Dispatch**:
   - Single files (< 5 files): Run `scripts/inject_summary.py --profile project --file <path> --summary "<dense-summary>"`.
   - Batch (> 10 files): Run `scripts/swarm_run.py` to distribute summarization.
3. **Cache Cleanup**: Run `scripts/cleanup_cache.py --profile project --dry-run` followed by `--apply` to prune stale entries.
4. **Transparent Reporting**: Emit coverage percentage and updated inventory status to the user.

## Curatorial Tools

| Script | Role |
|---|---|
| `scripts/inventory.py` | Cache coverage and gap auditor |
| `scripts/inject_summary.py` | Direct single-file summary injection |
| `scripts/swarm_run.py` | Automated batch summarization swarm |
| `scripts/cleanup_cache.py` | Stale and orphaned entry cleanup |
| `scripts/rlm_config.py` | Shared manifest and profile manager |

## Verification

Confirm 100% cache coverage and valid ledger formatting:

```bash
python3 scripts/inventory.py --profile project
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for RLM cache curation and maintenance.
- [cheapest_models.md](references/cheapest_models.md) — Model tiers and pricing guidance for batch summarization.
- [fallback-tree.md](references/fallback-tree.md) — Fallback protocol when curation scripts fail or encounters missing engines.
