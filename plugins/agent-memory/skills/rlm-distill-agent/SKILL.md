---
name: rlm-distill-agent
plugin: agent-memory
description: Distills uncached files into the Recursive Language Model (RLM) Summary cache Ledger by reading files deeply and injecting high-quality 1-sentence summaries via inject_summary.py.
allowed-tools: Bash, Read, Write
---

# RLM Distill Agent (`rlm-distill-agent`)

Distills uncached files into the RLM Summary Ledger to avoid re-reading full files repeatedly across agent sessions.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Batch Swarm Protocol](#batch-swarm-protocol)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Never Edit Cache Manually**: Always inject summaries via `python3 scripts/inject_summary.py`.
2. **Deep File Reading**: Read the entire file; extract core purpose, key components, and dependencies.
3. **Source Transparency**: Report which files were summarized and their injected summaries.

## Quick start

Check for missing summaries and inject a 1-sentence distillation:

```bash
python3 scripts/inventory.py --profile project
python3 scripts/inject_summary.py --profile project --file path/to/file.py --summary "Concise 1-sentence summary of behavior and components."
```

## Workflow

1. **Identify Gaps**: Run `python3 scripts/inventory.py --profile project` to list unindexed files.
2. **Deep Inspection**: Read target files thoroughly to identify architectural roles and interfaces.
3. **Inject Summary**: Execute `scripts/inject_summary.py` providing a dense, informative 1-sentence description.
4. **Transparent Output**: Output the file path and injected summary to the user.

## Batch Swarm Protocol

For large numbers of missing files (10+), delegate to `scripts/swarm_run.py` using the appropriate engine:
- **GitHub Copilot CLI**: `python3 scripts/swarm_run.py --engine copilot --workers 2 --files-from tasks.md`
- **Google Antigravity CLI**: `python3 scripts/swarm_run.py --engine gemini --workers 5 --files-from tasks.md`
- **Claude Code**: `python3 scripts/swarm_run.py --engine claude --workers 3 --files-from tasks.md`

## Verification

Verify updated inventory coverage metrics after distillation:

```bash
python3 scripts/inventory.py --profile project
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for RLM distillation quality.
- [cheapest_models.md](references/cheapest_models.md) — Model tiers and pricing guidance for distillation engines.
- [RLM_ARCHITECTURE.md](references/RLM_ARCHITECTURE.md) — Architectural overview of RLM semantic cache.
