# Domain Patterns: Exploration Session Failures

Failures at the session orchestration level: classification, gate enforcement, state management. Use when the improvement-loop target is `running-exploration-cycle`. Reviewed during the consolidation: each pattern notes what changed.

## Known Patterns

### Pattern 1: Session type misclassification leads to the wrong phase set

**Failure type:** the expert describes a process problem but is classified as Greenfield, which enables Phase 3 (prototype) when the real deliverable is a process change recommendation.

**Root cause:** routing on keywords ("workflow", "approval") that appear in both software and process-change contexts. The Intervention Check (Greenfield track question 4 in [discovery-planning-tracks.md](discovery-planning-tracks.md)) catches this only if it fires.

**Escape:**
- Make Phase 0 classification ([intake-agent.md](intake-agent.md)) check the explicit signal "existing manual process" versus "no process exists yet"; only the latter is Greenfield.
- Add a negative example to the `running-exploration-cycle` evals: a process-change scenario that looks Greenfield but routes to Analysis/Docs.
- Ensure the Intervention Check always fires, even when the routing seems confident.

**Confirmed improvements:** 2+ (recorded by the retired optimizer loop). *Review: the original named a "routing guide" and `discovery-planning/SKILL.md`; those now live in intake and the discovery-planning reference.*

### Pattern 2: HARD-GATE bypass via "quick question" framing

**Failure type:** the expert opens with "just a quick question" and the agent starts capturing requirements without a Discovery Plan.

**Root cause:** the gate was prose. A low-stakes trigger reads as a clarification, not a session start.

**Escape:**
- Add "quick question about" and "wondering if" as should-route-to-gate cases in the `running-exploration-cycle` evals and keep the skill's HARD-GATE constraint first.
- Before any capture begins, verify that an approved Discovery Plan exists or that the session is in Phase 0.

**Confirmed improvements:** 3+. *Review: partly enforced in code since the consolidation. `validate_phase_gate.py 1` now rejects a plan without `PLAN_STATUS: APPROVED` or `## SME Approval`, so a DRAFT cannot pass; the prose check at the start of capture is still advisory (a pre-write hook was planned and never built).*

### Pattern 3: Premature handoff, Phase 4 before Phase 3 artifacts exist

**Failure type:** the conductor routes to Phase 4 before prototype artifacts are confirmed, producing a handoff with an empty "Prototype Notes" section.

**Root cause:** the read-state block (Block 2) checks outcome files for completed phases, but the Phase 3 outcome is `exploration/prototype/index.html`, and agents sometimes write only `README.md` and mark Phase 3 complete.

**Escape:**
- Before marking Phase 3 complete, verify that both `index.html` and `README.md` exist under `exploration/prototype/` for Greenfield sessions.
- For Analysis/Docs and legacy-brownfield sessions (Phase 3 skipped), skip this check; the `[~]` marker is the authority.

**Confirmed improvements:** 2+. *Review: implemented. `validate_phase_gate.py 3` requires `README.md`, `captures/prototype-notes.md`, and, for Greenfield sessions, `index.html`.*

## Novel candidates (awaiting a second confirmation)

None recorded.
