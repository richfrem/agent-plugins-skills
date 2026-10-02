---
name: dual-loop
plugin: agent-orchestration
description: "(Industry standard: Sequential Agent / Agent as a Tool) Inner/outer agent delegation pattern via strategy packets, with verification and correction loops."
allowed-tools: Bash, Read, Write
---

# Dual-Loop (`dual-loop`)

Splits work between a strategic Outer Loop (Supervisor) and an execution-focused Inner Loop (tactical coding sub-agent).

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Inner loop isolation**: Inner Loop agents are strictly forbidden from running `git` commands.
- **Background execution**: Always redirect standard input (`< /dev/null`) to avoid `SIGTTIN` hangs.
- **Verification gate**: Outer Loop must mechanically verify tests and diffs before merging.
- **Single commit rule**: Commits and merges are executed exclusively by the Outer Loop.

## Quick start

```bash
# Dispatch sub-agent with strategy packet
python scripts/run_agent.py handoffs/task_packet_001.md <target_file> handoffs/result.md \
  "Execute strategy packet exactly." --cli <cli> --model "<model>" < /dev/null
```

## Workflow

1. **Decomposition**: Break work into atomic, testable Work Packages.
2. **Model Selection**: Select companion backend (`agy`, `claude`, `copilot`, `codex`, `llama`) via [cheapest_models.json](references/cheapest_models.json).
3. **Strategy Packet**: Author `handoffs/task_packet_NNN.md` in isolated worktree specifying scope and "NO GIT" rule.
4. **Supervised Review**: Outer Loop audits `git diff` for authorized paths and zero stub placeholders.
5. **Retrospective**: Conduct post-run assessment using [post_run_survey.md](references/post_run_survey.md); escalate repeat friction to triple-loop.

## Verification

```bash
# Verify delta and ensure zero stub placeholders
git -C <WORKTREE_PATH> diff --stat
# Run automated tests against worktree output
pytest <TEST_TARGET>
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Verification gates and criteria.
- [fallback-tree.md](references/fallback-tree.md) — Escalation protocol for loop stalls and timeouts.
- [post_run_survey.md](references/post_run_survey.md) — Post-run self-assessment survey.
- [cheapest_models.json](references/cheapest_models.json) — Multi-model latency and cost parameters.
- [diagrams/dual_loop_architecture.mmd](references/diagrams/dual_loop_architecture.mmd) — Inner/outer loop architecture diagram.
