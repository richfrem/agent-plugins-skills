# Acceptance Criteria: running-exploration-cycle

## 1. Routing
- [ ] Triggers on exploring-an-idea requests ("let's explore this idea", "help me plan this out", "resume my exploration", "where did we leave off").
- [ ] Does not trigger for engineering build requests, or for an existing working prototype: that goes to `reengineering-vibe-code`. A mid-intake mention of existing code redirects once, with the canonical wording.
- [ ] Technical codebase discovery (refactor, bug, subsystem) goes to `handing-off-to-engineering`, not through the phases.

## 2. HARD-GATE
- [ ] No capture, prototype or handoff work starts without an SME-approved Discovery Plan (`PLAN_STATUS: APPROVED` or `## SME Approval`).
- [ ] A plan marked `## Plan Status: DRAFT` never satisfies the gate; `python3 scripts/validate_phase_gate.py 1` exits 1 for it and 0 for an approved plan.
- [ ] "Just build it" is answered with the redirect text of [hard-gate-enforcement.md](hard-gate-enforcement.md) verbatim, with no workaround offered.

## 3. State
- [ ] `python3 scripts/state_engine.py status` prints "No active exploration session" without a database and a JSON object with the session and task counts when one exists.
- [ ] The dashboard is treated as a read-only projection of the state engine; a gate is never passed from conversation memory.
- [ ] An in-progress session is resumed at its active phase, with a short plain-language recap first.

## 4. Intake and brief
- [ ] The brief is written to `exploration/session-brief.md` using the canonical headers in order; unfilled fields carry `[INTAKE DRAFT — confirm]` or `[NEEDS HUMAN INPUT]`.
- [ ] The expert's own phrasing of the trigger is preserved verbatim.

## 5. Conduct
- [ ] One question per message, in business language: none of the jargon listed in [design-rationale.md](design-rationale.md).
- [ ] Each phase ends at its gate with a plain summary and the outcome path; completion is recorded only after a clear yes and a passing `validate_phase_gate.py <phase>`.
- [ ] No model IDs, prices or runtime flags are named; model and runtime choices are left to the `cli-agent` skill.

## 6. Code
- [ ] `python3 -m pytest scripts -q` passes from the skill folder.
