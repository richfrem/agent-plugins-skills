---
name: agent-swarm
plugin: agent-orchestration
description: "(Industry standard: Parallel Agent) Parallel multi-agent execution pattern for independent sub-tasks running concurrently across isolated worktrees."
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ (standard library only).

---

# Agent Swarm (`agent-swarm`)

Parallel multi-agent execution for batch operations, independent work packages, and mass migrations.

## Contents

- [Dependencies](#dependencies)
- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [Engine Optimization](#engine-optimization)
- [References](#references)

## Constraints

- **Independent execution**: Each worker task must be completely independent with zero shared in-memory state.
- **Background stdin**: Append `< /dev/null` to background commands to prevent `SIGTTIN` hangs.
- **Idempotence**: Post-processing commands must be safe to rerun with `--resume`.
- **Concurrency caps**: Limit Copilot CLI to `--workers 2` to prevent throttling; Gemini/Claude supports 5-10.

## Quick start

```bash
# Execute batch job with resume support
python ./scripts/swarm_run.py \
    --engine gemini \
    --job ./resources/jobs/my_job.job.md \
    --files-from checklist.md \
    --resume --workers 5
```

## Workflow

1. **Partition**: Break work into discrete, independent task files with bounded scopes.
2. **Select Engine**: Choose CLI backend (`agy`, `gemini`, `copilot`, `claude`, `llama`).
3. **Dispatch**: Run `swarm_run.py` pointing to the job file and target file list.
4. **Inspect**: Review intermediate logs and resolve failed workers via `--resume`.
5. **Merge**: Run mechanical test suites across all completed worker outputs.

## Verification

```bash
# Validate batch execution completed without orphaned tasks
python ./scripts/swarm_run.py --dry-run --files-from checklist.md
# Run test suite on completed batch outputs
pytest tests/
```

## Engine Optimization

- **Copilot CLI**: Ignores `-p` with stdin; `swarm_run.py` prepends prompt to file content. Concurrency max 2.
- **Gemini / Claude**: Accepts `-p` normally; supports high concurrency (`--workers 5`).
- **Atomic Writes**: If workers write to shared stores, use `fcntl.flock` for atomic file operations.

## References

- [PATTERN_GUIDE.md](references/PATTERN_GUIDE.md) — Comparative loop patterns and architecture.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Verification gates and trigger criteria.
- [fallback-tree.md](references/fallback-tree.md) — Error escalation and checkpoint reconciliation tree.
