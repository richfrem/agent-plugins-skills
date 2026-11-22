# the `intake` mode — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Socratic Intake & Task Registration

Register the task in `context/control_plane.db`:
```bash
python3 scripts/agent_control.py init --task-id "<task-id>" --title "<title>" --runtime "<runtime>" --spec-path "docs/plans/work-tasks/<task-id>/<task-id>-spec.md" --human-confirmed "HUMAN-CONFIRMED: <summary>"
```

## Triage Heuristics & Commands

Ask the human exactly one triage question:
> *"Is this a trivial fix (single-file/few-line, no architectural impact) or a standard task requiring the full spec/review pipeline? [Recommended: <heuristic default>]"*

- Heuristic: single file touched, description contains words like "typo", "fix wording", "one-line" → default `TRIVIAL`; anything else → default `STANDARD`.

### STANDARD Flow
During `INTAKE`, gather scoping answers and update the plan outline (`docs/plans/work-tasks/<task-id>/<task-id>-plan-outline.md`), then advance to `DRAFT_PLAN`:
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "DRAFT_PLAN" --reason "Intake outline confirmed; drafting spec and plan"
```
Compile the spec and implementation plan under `docs/plans/work-tasks/<task-id>/` and advance to `PLAN_REVIEW`:
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "PLAN_REVIEW" --reason "Draft spec and plan ready for review"
```

### TRIVIAL Fast-Track Flow
In `on-demand` mode (default), unregistered trivial branches pass without control-plane gating. For registered tasks, early closure uses the signed `* -> DONE` edge:
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "DONE" --reason "Early closure"
```
If mis-triaged, use the escape hatch:
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "ESCALATED" --reason "Mis-triaged as TRIVIAL"
```

## Adversarial Plan Audit (Inside `PLAN_REVIEW`)

In `PLAN_REVIEW`, run the adversarial plan audit (`plan_audit.py`) or record a human-signed waiver decision via `signed_decisions`, then request Gate 1 (`PLAN_REVIEW -> APPROVED`):
- Target files: `docs/plans/work-tasks/<task-id>/<task-id>-spec.md`, `docs/plans/work-tasks/<task-id>/<task-id>-implementation-plan.md`, relevant architectural references.
- Persona template: `bundling-context`'s `plan-critique-reviewer` template or the read-only review trio (`architect-review`, `security-auditor`, `tdd-contract-reviewer`).
- See [adversarial-plan-audit.md](adversarial-plan-audit.md) and [multi-round-external-review-protocol.md](multi-round-external-review-protocol.md) for convergence and multi-round rules.

```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "APPROVED" --reason "Plan and audit ready for Gate 1 signature"
```
