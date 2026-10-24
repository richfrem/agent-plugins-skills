# Strategy: dual-loop (supervisor / worker)

Splits work between a strategic Outer Loop (Supervisor) and an execution-focused Inner Loop (tactical coding sub-agent).

## Constraints

- **Inner loop isolation**: Inner Loop agents are strictly forbidden from running `git` commands.
- **Background execution**: Always redirect standard input (`< /dev/null`) to avoid `SIGTTIN` hangs.
- **Verification gate**: Outer Loop must mechanically verify tests and diffs before merging.
- **Single commit rule**: Commits and merges are executed exclusively by the Outer Loop.

## Quick start

Dispatch the inner loop through the `cli-agent` skill (cli-agents plugin), run from that skill's root:

```bash
python3 scripts/run_agent.py handoffs/task_packet_001.md <target_file> handoffs/result.md \
  "Execute strategy packet exactly." --cli <cli> --model "<model>" < /dev/null
```

## Workflow

1. **Decomposition**: Break work into atomic, testable Work Packages.
2. **Model Selection**: Select companion backend (`agy`, `claude`, `copilot`, `codex`, `llama`) via [cheapest_models.json](cheapest_models.json).
3. **Strategy Packet**: Author `handoffs/task_packet_NNN.md` in isolated worktree specifying scope and "NO GIT" rule.
4. **Supervised Review**: Outer Loop audits `git diff` for authorized paths and zero stub placeholders.
5. **Retrospective**: Conduct post-run assessment using [post_run_survey.md](post_run_survey.md); escalate repeat friction to the agent-agentic-os skill lab (os-lab).

## Verification

```bash
# Verify delta and ensure zero stub placeholders
git -C <WORKTREE_PATH> diff --stat
# Run automated tests against worktree output
pytest <TEST_TARGET>
```
