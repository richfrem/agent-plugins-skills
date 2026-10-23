# Strategy: agent-swarm (parallel independent jobs)

Parallel multi-agent execution for batch operations, independent work packages, and mass migrations.

## Constraints

- **Independent execution**: Each worker task must be completely independent with zero shared in-memory state.
- **Caller Workspace Isolation**: Swarm runs within the provided `--workdir` (default: cwd); it does not create git worktrees. The caller must provide an isolated worktree when write isolation is needed.
- **Background stdin**: Append `< /dev/null` to background commands to prevent `SIGTTIN` hangs.
- **Idempotence**: Post-processing commands must be safe to rerun with `--resume`.
- **Concurrency caps**: Limit Copilot CLI to `--workers 2` to prevent throttling; Gemini/Claude supports 5-10.
- **Tool Restrictions**: Worker subprocesses must not execute `git` write commands directly.

## Quick start

```bash
# Execute batch job with resume support
python3 scripts/swarm_run.py \
    --engine claude \
    --job ./resources/jobs/my_job.job.md \
    --files-from checklist.md \
    --resume --workers 5
```

## Workflow

1. **Partition**: Break work into discrete, independent task files with bounded scopes.
2. **Select Engine**: Choose CLI backend (`claude`, `copilot`, `agy`).
3. **Dispatch**: Run `swarm_run.py --job <job-file> --files-from <list>`.
4. **Inspect**: Review intermediate logs in `.swarm-run/` and resolve failed workers via `--resume`.
5. **Merge**: Run mechanical test suites across all completed worker outputs.

## Verification

```bash
# Validate batch execution plan without making LLM calls
python3 scripts/swarm_run.py --job ./resources/jobs/my_job.job.md --dry-run --files-from checklist.md

# Run test suite on completed batch outputs
pytest tests/
```

## Engine Optimization

- **Copilot CLI**: Ignores `-p` with stdin; `swarm_run.py` prepends prompt to file content. Concurrency max 2.
- **Agy / Claude**: Accepts `-p` normally; supports high concurrency (`--workers 5`).
- **Post-Command Serial Execution**: If workers write to a shared store or summary file, pass `--post-serial` to execute `post_cmd` serially under a cross-platform threading lock.
