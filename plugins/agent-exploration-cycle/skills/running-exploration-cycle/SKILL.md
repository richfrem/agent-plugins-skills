---
name: running-exploration-cycle
plugin: agent-exploration-cycle
description: >
  Runs the business exploration cycle end to end: starts or resumes a session (intake interview,
  session brief), enforces the Discovery Plan HARD-GATE, routes the four phases (Discovery Plan,
  Visual Blueprinting, Prototype, Handoff) to the sibling skills and keeps session state. Use when
  the user says "let's explore this idea", "I have an idea I want to explore", "help me plan this
  out", "start discovery", "resume my exploration", "where did we leave off", or starts any
  conversation about a need, problem or idea before building. Not for hardening an existing
  prototype (use reengineering-vibe-code) or for engineering build work.
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# Running the Exploration Cycle

Front door and conductor of the exploration plugin. Process: [process-overview.mmd](references/process-overview.mmd) and [process-definition.md](references/process-definition.md).

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **HARD-GATE**: no capture, prototype or handoff work until the SME has approved the Discovery Plan (`PLAN_STATUS: APPROVED` or `## SME Approval`); a DRAFT never counts. Use the redirect in [hard-gate-enforcement.md](references/hard-gate-enforcement.md) verbatim, offer no workaround.
- **State**: the SQLite state engine is authoritative; `exploration/exploration-dashboard.md` is a read-only projection. Never rely on conversation memory for a gate. If you were dispatched as a subagent, skip this skill.
- **One question at a time**, in the SME's business language (no git, branch or subagent jargon).
- **Routing**: an existing working prototype goes to `reengineering-vibe-code`; technical codebase discovery goes to `handing-off-to-engineering`.
- **Models**: never name models or prices here; choose runtime and model through the `cli-agent` skill.

## Quick start

Run from this skill's folder, with `CLAUDE_PROJECT_DIR` set to the project:

```bash
python3 scripts/state_engine.py status
python3 scripts/validate_phase_gate.py 1
python3 scripts/check_gaps.py --files exploration/captures/brd-draft.md --threshold 3
```

## Workflow

1. **Resume check**: run `status`; an in-progress session continues at its active phase ([using-exploration-cycle.md](references/using-exploration-cycle.md)).
2. **Phase 0 Intake**: interview, classify, write `exploration/session-brief.md` ([intake](references/intake-agent.md), [brief](references/exploration-session-brief.md)); pick session type and dispatch ([session-setup.mmd](references/session-setup.mmd), [dispatch](references/dispatch-strategies.md)).
3. **Phase 1 Discovery Plan**: [discovery-planning.md](references/discovery-planning.md) and [tracks](references/discovery-planning-tracks.md); then the capture loop in `capturing-business-requirements`.
4. **Phases 2 and 3**: hand to `building-interactive-prototypes`. **Phase 4**: hand to `handing-off-to-engineering`.
5. Each phase ends at its gate ([state-and-gates.mmd](references/state-and-gates.mmd)); wait for the SME, then run the validator for that phase.

## Verification

```bash
python3 scripts/validate_phase_gate.py <phase>   # 1 to 4
python3 -m pytest scripts -q
```

Acceptance criteria: [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Process: [process-definition.md](references/process-definition.md) • [orchestrator-loop.mmd](references/orchestrator-loop.mmd) • [high-level-process.mmd](references/high-level-process.mmd) • [design-rationale.md](references/design-rationale.md) (read to know why the loop halts where it does)
- Entry and state: [exploration-workflow.md](references/exploration-workflow.md) • [exploration-orchestrator-guide.md](references/exploration-orchestrator-guide.md) • [environment-check.md](references/environment-check.md)
- Phase 0 and 1: [problem-framing-agent.md](references/problem-framing-agent.md) • [discovery-planning-agent.md](references/discovery-planning-agent.md) • [exploration-cycle-orchestrator-agent.md](references/exploration-cycle-orchestrator-agent.md) (CLI-dispatch director)
- Seed template: [exploration-dashboard.md](assets/exploration-dashboard.md)
- Quality: [architecture.md](references/architecture.md) (artifact markers) • [post-run-survey.md](references/post-run-survey.md) • [domain-patterns.md](references/domain-patterns.md) and [exploration-session patterns](references/domain-patterns-exploration-session.md) (known failures and escapes) • [exploration-optimizer.md](references/exploration-optimizer.md) (retired loop, use `os-lab`)
