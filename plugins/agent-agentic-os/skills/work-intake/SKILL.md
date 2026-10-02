---
name: work-intake
plugin: agent-agentic-os
version: 1.4.0
description: >
  CRITICAL INTAKE GATEWAY: Use at the start of any non-trivial engineering task,
  feature, refactor, multi-file bugfix, work package, or new idea—including requests
  to explore, brainstorm, build, fix, or change something—before planning or code
  changes. Enforces read-only discovery, 1–3 structured questions with defaults,
  control-plane registration, and compilation of the immutable four-pillar TASK_SPEC.md.
allowed-tools: Bash, Read, Write
---

# Work Intake (`work-intake`)

Critical intake gateway for discovery, interview clarification, and four-pillar specification authoring before implementation.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Confirm Approver Identity First**: Real work lives in `context/control_plane.db` where only the human operator's signing key approves; simulation runs in `simulation_control_plane.db` with agent test identity (`test-human@local`).
2. **Read Guidance & DB First**: Read `transition_templates.yaml`, `transition-guidance`, and SQLite DB first; say exactly which parts were read, never more.
3. **Artifact Location & Running Ledger**: Task artifacts live in `docs/plans/work-tasks/<task-id>/`, never plans root. Maintain a running ledger of every human directive from first message.
4. **Question Budget & Chat Answers**: Answer from context first; ask only ONE question per turn. Never re-ask what is recorded and never dispute the human's account. Persist chat answers via `coordinate-transition --interactive` (actor=human); never write interview answers as interviewer.
5. **Pasteable Commands Only**: Every command the human must run is complete and ready to paste, with no back-references, no vague references, and never "see above".
6. **Stop on Blocked Gate**: On blocked gate, STOP and state cause and cost; no workaround commands (recovery approvals, direct DB edits). Never record a review skip on the human's behalf.

## Quick start

Check advisory guidance for the active task state:

```bash
python3 scripts/control_plane/coordinator.py transition-guidance --task-id <task-id>
```

## Workflow

1. **Read Guidance & State**: Read `transition_templates.yaml` and SQLite DB enforcement before asking or acting.
2. **Interview & Spec Synthesis**: Interview for missing requirements. Compile the 4 pillars of `TASK_SPEC.md` (The Job, The Why, Semantic Guardrails, Objective DoD).
3. **Plan Drafting**: Outline and draft implementation plan in `docs/plans/work-tasks/<task-id>/`.
4. **Stage Transitions**: Transition through `INTAKE` -> `INTERVIEW` -> `DRAFT_PLAN` -> `PLAN_REVIEW` using `coordinate-transition`.
5. **Advance to Approval**: In `PLAN_REVIEW`, once the plan is accepted, agent runs `coordinate-transition --to AWAITING_APPROVAL`.

## Verification

Validate task spec and transition gate evidence deterministically:

```bash
python3 scripts/verify_gate_evidence.py --task-id <task-id>
```

## References

- [edge-matrix.md](references/edge-matrix.md) — Command execution taxonomy (AGENT-RUNNABLE, SOFT, HARD).
- [work-intake-healthy-transcript.md](references/work-intake-healthy-transcript.md) — Example walkthrough transcript.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Gate criteria and definitions of done.
- [fallback-tree.md](references/fallback-tree.md) — Fallback and recovery when transitions fail.
- [multi-round-external-review-protocol.md](references/multi-round-external-review-protocol.md) — Multi-round external review and persona selection protocol.
- [detailed-reference.md](references/detailed-reference.md) — Extended contract and protocol documentation.
