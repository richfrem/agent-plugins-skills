---
name: co-pilot-loop
plugin: agent-orchestration
description: "Cooperative Multi-Agent Coordination Loop. Spawns a lightweight companion sub-agent to perform spec discovery, planning, and implementation while the primary agent acts as QA Director."
allowed-tools: Bash, Read, Write
---

# Cooperative Co-Pilot Loop (`co-pilot-loop`)

Splits engineering tasks between a Supervisor (Outer Loop) and an Executor (Inner Loop sub-agent) running inside an isolated worktree.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **No-Git rule**: The companion Executor is strictly forbidden from running any `git` commands.
- **Background protection**: Always append `< /dev/null` to CLI dispatch commands to prevent `SIGTTIN` hangs.
- **Sequential review gates**: Gate 1 (Spec), Gate 2 (Plan), Gate 3 (QA) must be completed in order.
- **Single commit rule**: All commits are made exclusively by the Supervisor after QA approval.

## Quick start

```bash
# Spawn companion sub-agent with strategy packet
python ./scripts/run_agent.py <PERSONA_FILE> <PACKET_FILE> <OUTPUT_FILE> "<INSTRUCTION>" \
  --cli agy --model "Gemini 3.5 Flash (Low)" < /dev/null
```

## Workflow

1. **Setup & Model**: Consult [cheapest_models.md](references/cheapest_models.md) or [cheapest_models.json](references/cheapest_models.json) to select companion model.
2. **Packet Handoff**: Create isolated worktree and assemble Strategy Packet specifying scope and no-git constraint.
3. **Gate 1 (Spec Review)**: Supervisor validates spec has zero placeholders (`TODO`/`TBD`) and ADR alignment.
4. **Gate 2 (Plan Review)**: Supervisor validates dependency ordering, rollback steps, and TDD contract.
5. **Gate 3 (Execution & QA)**: Executor implements in worktree; Supervisor audits `git diff` and runs test suite.
6. **Retrospective & Merge**: Merge validated changes from worktree and log session summary.

## Verification

```bash
# Verify supervisor gate acceptance criteria
pytest plugins/agent-orchestration/tests/test_loop_strategies.py
# Check git diff in companion worktree before merge
git -C <WORKTREE_PATH> diff --stat
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Structural and behavioral expectations for co-pilot loop.
- [fallback-tree.md](references/fallback-tree.md) — Fallback escalation protocol for loop hangs and test failures.
- [cheapest_models.md](references/cheapest_models.md) — Companion sub-agent token and latency guide.
- [cheapest_models.json](references/cheapest_models.json) — Structured CLI model capability catalog.
