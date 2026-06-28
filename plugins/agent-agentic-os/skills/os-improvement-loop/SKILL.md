---
name: os-improvement-loop
plugin: agent-agentic-os
version: 0.5.0
description: >
  Pattern 5: Concurrent Event-Driven Multi-Agent Loop. Coordinates multiple Claude sessions
  as OS threads sharing a common event bus and memory address space. Every loop cycle is a
  full improvement cycle: execute, eval against benchmark (KEEP/DISCARD), emit friction events,
  and close with surveys, metrics, memory persistence, and Triple-Loop triggers.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Concurrent Agent Loop

Treats concurrent sessions as OS threads sharing a common event bus and memory address space. Every cycle includes execution, independent peer evaluation, friction tracking, self-assessment surveys, post-run metrics, and memory persistence.

---

## When to Use This Pattern

Use when:
- Coordinating continuous improvement across multiple concurrent agent sessions.
- Evaluating and improving multiple skills, workflows, or templates in parallel.
- You need every cycle to generate measurable accuracy gains and persistent memory.

Do NOT use for:
- Single-session procedural tasks (use `os-eval-runner` directly).
- Signal-only coordination with no evaluation, survey, or memory steps.

---

## Key Invariants

- **No-Rollback Rule**: Never manually roll back changes during a cycle unless `evaluate.py` registers an explicit accuracy regression.
- **Eval Gate Mandatory**: Every modification must pass the independent evaluation gate (`evaluate.py` exit code 0). No manual bypasses.
- **NEVER STOP Discipline**: Do not abort a running loop due to minor/moderate errors. Complete the loop close checklist and log unresolved issues as Map Debt.
- **Outer Loop Ownership**: The outer loop owns session lifecycle. Inner loop tasks (`os-eval-runner`) must not prematurely close a session without running Stage 4 (memory promotion and survey collection).

---

## Stage Pointers & Reference Protocols

The execution details are split across modular references:
- [Stage 0: Setup and Orientation](references/stage-0-orientation.md) — Pre-flight reads, registry, and packet design.
- [Stage 1: INNER_AGENT Execution](references/stage-1-execution.md) — Strategy execution, friction logging, and local scoring.
- [Stage 2: PEER_AGENT Verification](references/stage-2-verification.md) — Independent evaluation run and verdict formulation.
- [Stage 3: Decision Logic](references/stage-3-decision.md) — KEEP/DISCARD actions and correction packets.
- [Stage 4: Loop Close Checklist](references/stage-4-close.md) — Surveys, ledger updates, memory promotion, and retrospectives.
- [Orchestrator Meta-Survey](references/orchestrator-meta-survey.md) — Meta-evaluation of loop coordination patterns.

---

## Smoke Test

1. **Verify Event Registry**: Run `os-init` or start a test loop. Assert that `context/events.jsonl` registers start events correctly.
2. **Execute Scorer**: Run `python3 ./scripts/evaluate.py --skill skills/todo-check/` on a dummy check to verify that exit codes map correctly (0 for KEEP, 1 for DISCARD, 2 for path error).
3. **Friction Event Test**: Propose a manual edit, emit a mock `friction` event, resolve it with `friction.resolved`, and verify the metrics engine logs the resolution gate pass.

---

## Gotchas

- **Conflation of Loops**: Conflating the inner target skill loop with the outer OS-improvement loop. Outer loop changes the OS workflows; inner loop changes target skills.
- **Orphaned Sessions**: Completing inner loop tasks but failing to run memory promotion and survey curation. Ephemeral findings are lost.
- **Directory Symlinks**: Creating directory-level symlinks from skills to shared roots. This violates ADR-003. Use file-level symlinks.

---

## HANDOFF_BLOCK Template

Every loop execution that completes a cycle must output this block in its handoff:

```markdown
## HANDOFF_BLOCK
- **Cycle ID**: cycle-YYYYMMDD-HHMMSS
- **Target Skill**: [path/to/target]
- **Verdict**: KEEP / DISCARD
- **Score (Before -> After)**: [0.XX -> 0.YY]
- **Friction Events**: [N encountered / N resolved]
- **Outstanding Map Debt**: [list links or IDs]
- **Recommended Next Step**: [next hypothesis to test]
```
