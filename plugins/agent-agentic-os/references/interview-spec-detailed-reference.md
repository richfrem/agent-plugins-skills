# interview-spec — Detailed Reference

Extracted from SKILL.md per Layer-1 procedural-core line budget (issue #551).

## Socratic Intake & Task Registration

Register the task in `context/control_plane.db`:
```bash
python3 scripts/agent_control.py init --task-id "<task-id>" --title "<title>" --runtime "<runtime>" --spec-path "docs/plans/<task-id>-spec.md"
```

## Triage Heuristics & Commands

Ask the human exactly one triage question:
> *"Is this a trivial fix (single-file/few-line, no architectural impact) or a standard task requiring the full spec/review pipeline? [Recommended: <heuristic default>]"*

- Heuristic: single file touched, description contains words like "typo", "fix wording", "one-line" → default `TRIVIAL`; anything else → default `STANDARD`.

### STANDARD Flow
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "INTERVIEW" --reason "Beginning Socratic intake"
```
During the interview, use `record_interview_question.py` to record each Q&A turn. Once concluded, compile the spec/plan using `write_plan_document.py` and coordinate:
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "DRAFT_PLAN" --reason "Draft spec and plan compiled from interview"
```

### TRIVIAL Fast-Track Flow
Fast-track straight to `DONE` via the `intake_to_done_trivial` edge (no spec file written):
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "DONE" \
  --reason "TRIVIAL fast-track" --interactive \
  --answers '{"triage_classification": "TRIVIAL: <one-line reason>, files=<n>, diff=<short sha or `git diff --stat` one-liner>"}'
```
If mis-triaged, use the escape hatch:
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "ESCALATED" --reason "Mis-triaged as TRIVIAL"
```

## Multi-Agent Review Stage Gate (User-Controlled)

Present the User Stage Gate:
> *"Step 3 (draft plan) is done. Do you want to trigger a multi-agent review of this plan (Step 4a — an external AI reviews it before you decide), or proceed straight to Step 5 (asking for your approval)?"*

### Path A: User Chooses Multi-Agent Review
```bash
python3 scripts/agent_control.py coordinate-transition --task-id "<task-id>" --to "MULTI_AGENT_REVIEW" --reason "User requested multi-agent review bundle"
```
Package with `context-bundler`:
- Target files: `docs/plans/<task-id>-spec.md`, `implementation_plan.md`, relevant architectural references.
- Persona template: `assets/templates/plan-critique-reviewer.md` or Multi-Persona Fan-Out.
- Output location: `temp/review_<task-id>/`.
- Present bundle path to user for browser review (ChatGPT, Claude Web, Grok). Ingest feedback, iterate, and transition to `AWAITING_APPROVAL`.
- See `references/multi-round-external-review-protocol.md` for persona selection and multi-round rules.

### Path B: User Skips Multi-Agent Review
```bash
python3 scripts/agent_control.py transition --task-id "<task-id>" --to "AWAITING_APPROVAL" --reason "User opted to skip multi-agent review gate"
```
