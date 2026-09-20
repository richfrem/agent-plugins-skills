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

# Interview Spec (`work-intake`)

## Critical Operational Rules (Read First Before Any Action)

1. **Read Guidance and DB First**: Before acting or asking, read the stage YAML (`scripts/control_plane/transition_templates.yaml`), advisory transition guidance (`transition-guidance --task-id <task-id>`), and SQLite DB enforcement. Say exactly which parts were read, never more.
2. **Task Artifact Location**: All task artifacts (spec, plan, outline, reviews) MUST live in `docs/plans/work-tasks/<task-id>/`, NEVER in the `docs/plans` root.
3. **Running Directives Ledger**: Maintain a running ledger of every human directive from the very first message. Consult it before every reply; never lose directives across transitions.
4. **Answer Once & One Question at a Time**: Answer all possible questions from context, authorized sources, or the running ledger first. Ask only ONE question per turn for what is genuinely missing. Never re-ask what is recorded.
5. **No Skips or Impersonation**: Human chat answers to transition questions must be persisted through `coordinate-transition --interactive` (actor=human). Never write interview answers via `record_interview_question.py` as `interviewer`. Never record a review skip on the human's behalf. Skips are human decisions.
6. **On Blocked Gate**: STOP, state the cause and cost in plain words, and do not attempt workaround commands (recovery approvals, direct DB edits). Never hand the human a state-reverting command without explaining what it undoes.
7. **Complete Pasteable Commands Only**: Every command the human must run is repeated in full, ready to paste, every time it is needed. No back-references and no vague references (never "see above" or Python function names).
8. **Never Dispute the Human**: Never dispute or "correct" the human's account of what they said or meant. Take their statement as the record, adjust, and continue.
9. **References**:
   - Classification & Who Runs What: `plugins/agent-agentic-os/references/edge-matrix.md`
   - Worked Transcript: `plugins/agent-agentic-os/references/work-intake-healthy-transcript.md`

---

## Edge Classification (Who Runs What)

Every transition command belongs to one of three classes (see `references/edge-matrix.md`):
- **AGENT-RUNNABLE**: You (the agent) run the command directly once the human says go in chat. Never ask the human to run it.
- **SOFT**: You ask the human in chat for a simple confirmation. Once they approve, YOU run the command. Never hand the command to the human.
- **HARD**: Only cryptographic signatures (Gate 1 `APPROVED`, Gate 3 `VERIFY_EXIT`, closure `DONE`) or policy-reserved commands require human execution. Only hand a command to the human for these, using the full pasteable command.

---

## Stage-Entry Question Contract & Outline

1. Load that state's `stages.<STATE>` contract from `transition_templates.yaml`.
2. Map intent from context, prompt documents, or ledger.
3. Update the outline at `docs/plans/work-tasks/<task-id>/<task-id>-plan-outline.md` after each accepted answer.
4. Fast-track `TRIVIAL` tasks to lightweight verification; standard work proceeds through full specification and implementation plan drafting.
5. In `PLAN_REVIEW`: agent review is optional. When the human accepts the plan, YOU run `coordinate-transition --to AWAITING_APPROVAL`. No review or skip receipt is required.

---

## The 4 Pillars of `TASK_SPEC.md`
Every compiled specification must satisfy:
1. **The Job**: Clear description of system change and subsystem paths.
2. **The Why**: Core problem statement and architectural rationale.
3. **Semantic Guardrails**: Non-negotiable boundaries paired with concrete justifications.
4. **Objective Definition of Done (DoD)**: Programmatic verification commands (`exit 0` tests, linters, audits).
