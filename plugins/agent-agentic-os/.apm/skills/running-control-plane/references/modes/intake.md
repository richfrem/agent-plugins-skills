# Work Intake (the `intake` mode)

Critical intake gateway for discovery, interview clarification, and four-pillar specification authoring before implementation.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> CRITICAL INTAKE GATEWAY: Use at the start of any non-trivial engineering task, feature, refactor, multi-file bugfix, work package, or new idea—including requests to explore, brainstorm, build, fix, or change something—before planning or code changes. Enforces read-only discovery, 1–3 structured questions with defaults, control-plane registration, and compilation of the immutable four-pillar TASK_SPEC.md.

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
3. **Plan Drafting**: Draft plan via native host facilities. For STANDARD work, choose the execution strategy with the `orchestrating-agent-work` skill (`strategy-selection.md`, then `graph-planning.md` when the strategy is `graph`, which compiles and validates the task's graph manifest) before review. The strategies and their plan artifacts are registered only in `orchestrating-agent-work`'s `patterns.json`.
4. **Stage Transitions**: Transition through `INTAKE` -> `DRAFT_PLAN` -> `PLAN_REVIEW` using `coordinate-transition` (scoping interview and outline happen inside `INTAKE`; adversarial plan audit happens inside `PLAN_REVIEW`).
5. **Advance to Approval**: In `PLAN_REVIEW`, once the plan and audit are ready, request Gate 1 (`PLAN_REVIEW -> APPROVED`) via `coordinate-transition --to APPROVED`, which halts with `HUMAN_PROOF_REQUIRED` for the human's SSH signature.

## Plan changes during implementation

A signed plan is not reopened when the work teaches something. Append each change to `docs/plans/work-tasks/<task-id>/plan-deltas.md` (date, reason, what changed) and fix the gap in the slice that found it. Do not send the task back to planning. The deltas are reviewed with the code at the worktree review. The one exception is a change to a graph manifest whose SHA-256 the human approved: ask the human to approve the new SHA in chat, record it in `plan-deltas.md`, and start the run with that approved value.

## Steps only the human can run

Say so up front when a step needs the human's own terminal answer: gate signatures (passphrase), recovery approvals, review skips and the review-method selection. Give one short, verified command per line (it must not wrap when pasted), name the exact prompts and what to answer, and never answer for the human or record their decision for them.

## Verification

Validate task spec and transition gate evidence deterministically:

```bash
python3 scripts/verify_gate_evidence.py --task-id <task-id>
```

## References

- [edge-matrix.md](../edge-matrix.md) — Command execution taxonomy (AGENT-RUNNABLE, SOFT, HARD).
- [healthy-transcript.md](../healthy-transcript.md) — Example walkthrough transcript.
- [acceptance-criteria.md](../acceptance-criteria.md#mode-intake) — Gate criteria and definitions of done.
- [fallback-tree.md](../fallback-tree.md#mode-intake) — Fallback and recovery when transitions fail.
- [multi-round-external-review-protocol.md](../multi-round-external-review-protocol.md) — Multi-round external review and persona selection protocol.
- [detailed-reference.md](../intake-detailed-reference.md) — Extended contract and protocol documentation.
