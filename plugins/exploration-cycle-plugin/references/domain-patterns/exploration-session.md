# Domain Patterns: Exploration Session Failures

Failures observed at the session orchestration level — classification, gate enforcement, and
state management. Use when the exploration-optimizer target is `exploration-workflow` or
`discovery-planning`.

## When to use this file

Check before formulating an improvement hypothesis. Apply the matching escape first.

---

## Known Patterns

### Pattern 1: Session Type Misclassification → Wrong Phase Set

**Failure type:** SME describes a process problem but gets classified as Greenfield, enabling
Phase 3 (prototype build) when the real deliverable is a process change recommendation.

**Root cause:** The scenario routing guide matches on keywords ("workflow", "approval") that
appear in both software and process-change contexts. The Intervention Check (Q4) catches this
but only if it fires correctly.

**Escape:**
- Strengthen the routing guide to check for the explicit signal "existing manual process" vs
  "no process exists yet" — the latter is Greenfield, the former often isn't.
- Add a negative example to `discovery-planning/SKILL.md` showing a process-change scenario
  that LOOKS like Greenfield but routes to Analysis/Docs.
- Ensure the Intervention Check Q4 always fires, even when the routing seems confident.

**Confirmed improvements:** 2+

---

### Pattern 2: HARD-GATE Bypass via "Quick Question" Framing

**Failure type:** SME frames the start of a session as "just a quick question" and the agent
starts capturing requirements without a Discovery Plan in place.

**Root cause:** The HARD-GATE check is a prose instruction. When the user trigger is low-stakes
("quick question", "just wondering"), agents sometimes treat it as a clarification request
rather than a session start and skip the gate.

**Escape:**
- Add trigger phrases "quick question about" and "wondering if" to the negative-example block
  in `exploration-workflow/SKILL.md` — these should route to the gate check, not bypass it.
- Add an explicit check in Block 0: before any capture begins, verify that a Discovery Plan
  exists or that the session is in Bootstrap phase.

**Confirmed improvements:** 3+

---

### Pattern 3: Premature Handoff — Phase 4 Before Phase 3 Artifacts Exist

**Failure type:** Orchestrator routes to Phase 4 (Handoff) before prototype artifacts are
confirmed present, producing a handoff with empty "Prototype Notes" section.

**Root cause:** Block 2 checks for Outcome files for complete phases, but the outcome file
for Phase 3 is `exploration/prototype/index.html` — agents sometimes write only
`exploration/prototype/README.md` and mark Phase 3 complete without `index.html`.

**Escape:**
- Add a Phase 3 completion gate: before marking `[x]`, verify that BOTH `index.html` AND
  `README.md` exist under `exploration/prototype/` for Greenfield sessions.
- For Analysis/Docs and Brownfield-legacy sessions (Phase 3 disabled), this check should be
  skipped — the dashboard `[~]` marker is the authority.

**Confirmed improvements:** 2+

---

## Novel Candidates (awaiting 2nd confirmation)

[Empty — append here when a novel failure is confirmed once]
