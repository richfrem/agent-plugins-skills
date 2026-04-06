# Design Spec: Dashboard Pattern Refactor (Option 1.5)
**Date:** 2026-04-06
**Status:** Approved
**Author:** SME + Copilot CLI Brainstorming Session

---

## Problem Statement

The `exploration-cycle-plugin` has excellent isolated child skills (`discovery-planning`, `visual-companion`, `subagent-driven-prototyping`, `exploration-handoff`) but no stateful orchestrator binding them into a deterministic loop. The `exploration-workflow` skill exists as a narrative guide only — it describes phases but enforces nothing. The `exploration-orchestrator` skill is an explicit stub. Between sessions, the LLM has no persistent state to read, so it cannot reliably resume or enforce phase sequencing.

---

## Approved Approach: Option A — Full Rewrite

Rewrite `exploration-workflow/SKILL.md` as a first-class state machine. Introduce `exploration-dashboard.md` as the shared state artifact. Apply surgical updates to each child skill. Retire `exploration-orchestrator` entirely.

---

## Section 1: The Dashboard Template

**Location in plugin:** `assets/templates/exploration-dashboard.md`
**Live copy in user workspace:** `exploration/exploration-dashboard.md`

```markdown
# Business Exploration Dashboard

**Session:** [Brief title or topic — filled in during bootstrap]
**Current Phase:** Phase 1 — Problem Framing
**Status:** In Progress

---

## The 4-Phase Exploration Loop

- [ ] **Phase 1: Problem Framing**
  - Skill: `discovery-planning`
  - Gate: SME approval of Discovery Plan
  - Outcome: `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`

- [ ] **Phase 2: Visual Blueprinting**
  - Skill: `visual-companion`
  - Gate: SME selection and confirmation of layout direction
  - Outcome: `exploration/captures/layout-direction.md`

- [ ] **Phase 3: Prototyping**
  - Skill: `subagent-driven-prototyping`
  - Gate: SME walkthrough and sign-off on working prototype
  - Outcome: `exploration/prototype/index.html`

- [ ] **Phase 4: Handoff & Specs**
  - Skill: `exploration-handoff`
  - Gate: SME approval of final handoff package (includes requirements, user stories, risk tier)
  - Outcome: `exploration/handoffs/handoff-package.md`

---

## Session Log

| Phase | Completed | Notes |
|-------|-----------|-------|
| Phase 1 | — | — |
| Phase 2 | — | — |
| Phase 3 | — | — |
| Phase 4 | — | — |
```

**Design decisions:**
- `[ ]`/`[x]` checkboxes are the machine-readable state signal
- Each phase records its Outcome file — orchestrator verifies completion by checking file existence
- Session Log provides human-readable audit trail
- `**Current Phase:**` gives the LLM a single-line read for instant orientation

---

## Section 2: `exploration-workflow` State Machine (6 Blocks)

### Frontmatter
```yaml
name: exploration-workflow
description: >
  SME-facing orchestrator for the 4-phase Business Exploration Loop. Manages
  state via exploration-dashboard.md, enforces phase gates, and routes to
  child skills in sequence. Single canonical entry point — invoke at the start
  of any exploration session or to resume an in-progress session.
  Trigger phrases: "start an exploration", "let's explore this idea",
  "resume my exploration", "where did we leave off", "start discovery".
allowed-tools: Read, Write
```

### Block 1 — Bootstrap (silent)
1. Check for `exploration/exploration-dashboard.md`
2. **If NOT exists:** Create `exploration/` directory if needed. Scaffold new dashboard from template. Ask: *"What are we exploring today? Give it a short name so we can track it."* Fill `**Session:**`, write file, proceed to Block 3.
3. **If EXISTS:** Proceed to Block 2.

### Block 2 — Read State (silent)
1. Read dashboard. Identify active phase = first unchecked `[ ]`.
2. For all `[x]` phases, verify Outcome file exists on disk.
3. If an Outcome file is missing for a completed phase, flag to SME and resolve before advancing.

### Block 3 — Orientation Summary (always shown)
Present a brief, friendly status message. Example mid-session:
> "Welcome back! Here's where we are:
> ✅ Phase 1 — Problem Framing: Complete
> ✅ Phase 2 — Visual Blueprinting: Complete
> 🔵 Phase 3 — Prototyping: Up next
>
> Ready to pick up where we left off and start building the prototype?"

For a new session:
> "Great — we're all set up. We'll work through 4 phases together, starting with Problem Framing. Ready to begin?"

Wait for soft confirmation before proceeding.

### Block 4 — Phase Routing
| Active Phase | Invoke |
|---|---|
| Phase 1 — Problem Framing | `discovery-planning` |
| Phase 2 — Visual Blueprinting | `visual-companion` |
| Phase 3 — Prototyping | `subagent-driven-prototyping` |
| Phase 4 — Handoff & Specs | `exploration-handoff` |
| All 4 complete | → Completion Block |

When invoking a child skill, pass context: *"You are operating as part of an active Exploration Session. When your phase is complete, return here so we can update the session dashboard."*

### Block 5 — HARD-GATE (phase completion approval)
1. Present plain-language summary of what was produced (1–3 bullets).
2. Show the Outcome file path.
3. Ask: *"Does everything look right? If you're happy with it, just say the word and I'll mark Phase [N] complete."*
4. `<HARD-GATE>` — Do NOT update dashboard until SME gives clear affirmation ("Yes", "Looks good", "Approved", "Go ahead", etc.).
5. If changes requested: return to child skill, apply changes, re-present. Repeat until satisfied.

### Block 6 — Dashboard Write (after gate approval)
Using Write tool:
1. Change `[ ]` → `[x]` for completed phase.
2. Update `**Current Phase:**` to next phase name (or "Complete" if Phase 4).
3. Update `**Status:**` field.
4. Fill Session Log row with date and one-sentence outcome note.
5. Loop back to Block 3 for next phase.

### Completion Block (all 4 phases done)
> "🎉 Congratulations — your Exploration Session is complete!
> All four phases are finished and your handoff package is ready.
> Your exploration outputs are in the `exploration/` folder.
> The next step is Opportunity 4: Engineering. Hand your team the `exploration/handoffs/handoff-package.md` to begin the build."

Update `**Status:**` to `Complete`.

---

## Section 3: Child Skill Updates

### Dashboard Intercept Block (added to ALL 4 child skills — first instruction)
```
## Dashboard Intercept

Before doing anything else, silently check for `exploration/exploration-dashboard.md`.

- **If the file EXISTS:** Stop immediately. Do not proceed with this skill's standalone flow.
  Announce: "It looks like you have an active Exploration Session in progress. Let me take
  you back to your session dashboard so we can keep your progress on track."
  Then invoke `exploration-workflow` to resume from the correct phase.

- **If the file does NOT exist:** Proceed with this skill's standalone flow as normal.
```

### `discovery-planning` — Terminal State Update
Replace final announcement with:
```
## Completion — Return to Orchestrator
Once the Discovery Plan is approved and saved:
1. Announce: "Your plan is saved — Phase 1 is complete."
2. If within an active Exploration Session: "Returning to your session dashboard now."
   Invoke `exploration-workflow` to trigger the Phase 1 HARD-GATE and dashboard update.
```

### `visual-companion` — Terminal State Update
Replace Step 5 with:
```
## Completion — Return to Orchestrator
Once layout direction is confirmed and saved:
1. Announce: "Layout confirmed — Phase 2 is complete."
2. If within an active Exploration Session: "Returning to your session dashboard now."
   Invoke `exploration-workflow` to trigger the Phase 2 HARD-GATE and dashboard update.
```

### `subagent-driven-prototyping` — Entry Context + Terminal State
Add after Dashboard Intercept, before Required Inputs Check:
```
## Orchestrator Context
If dispatched by `exploration-workflow`, the Discovery Plan and layout direction have
already been approved. The Required Inputs Check below is a verification step only —
do not re-present these artifacts for re-approval. Proceed directly to Component Decomposition.
```

Replace Completion Report with:
```
## Completion — Return to Orchestrator
Once all components are assembled and README is written:
1. Announce: "Your prototype is ready — Phase 3 is complete."
2. If within an active Exploration Session: "Returning to your session dashboard now."
   Invoke `exploration-workflow` to trigger the Phase 3 HARD-GATE and dashboard update.
```

### `exploration-handoff` — Stage 0 Scribe + Terminal State
Prepend before existing Stage 1:
```
## Stage 0: Scribe Activities (Automated Capture Before Synthesis)

Before opening the handoff dialogue, silently check for `exploration/prototype/`.
If it exists, run the following three capture activities in sequence:
> "Capturing [activity name] first — this gives us the raw material for the handoff."

1. **Business Requirements Capture** (invoke `business-requirements-capture`)
   Output: `exploration/captures/business-requirements.md`

2. **User Story Capture** (invoke `user-story-capture`)
   Output: `exploration/captures/user-stories.md`

3. **Business Workflow Doc** (invoke `business-workflow-doc` — ONLY if the Discovery Plan
   describes a process flow with sequential steps or decision branches)
   Output: `exploration/captures/workflow-diagram.md`

Announce: "Requirements and stories captured. Now let's put together your handoff package."
Then proceed to Stage 1. Stage 0 outputs are now source artifacts for synthesis.
```

Append after Stage 3 / Final Output:
```
## Completion — Return to Orchestrator
Once handoff package is approved and written:
1. Announce: "Your handoff package is complete — Phase 4 is done."
2. If within an active Exploration Session: "Returning to your session dashboard now."
   Invoke `exploration-workflow` to trigger the Phase 4 HARD-GATE, dashboard update,
   and Completion Block.
```

---

## Section 4: Cleanup & Deletion

### Files to Delete
- `skills/exploration-orchestrator/` — entire directory (SKILL.md, acceptance-criteria.md, evals/)
- `skills/deferred/exploration-orchestrator/` — entire nested directory (registry conflict risk: dynamic scanner picks up any SKILL.md)

### Reference File Updates
| File | Change |
|---|---|
| `README.md` | Remove `exploration-orchestrator/` from skills directory tree |
| `references/architecture.md` | Replace `exploration-orchestrator` row with `exploration-workflow` as state machine orchestrator |
| `references/post-run-survey.md` | Replace any `exploration-orchestrator` mentions with `exploration-workflow` |

### New Directory
- `assets/templates/` — create and add `exploration-dashboard.md` canonical blank template

---

## Full Change Summary

| File | Action |
|---|---|
| `assets/templates/exploration-dashboard.md` | **Create** — new dashboard template |
| `skills/exploration-workflow/SKILL.md` | **Rewrite** — full state machine (Blocks 1–6) |
| `skills/discovery-planning/SKILL.md` | **Update** — add Intercept Block + Terminal Return |
| `skills/visual-companion/SKILL.md` | **Update** — add Intercept Block + Terminal Return |
| `skills/subagent-driven-prototyping/SKILL.md` | **Update** — add Intercept Block + Orchestrator Context + Terminal Return |
| `skills/exploration-handoff/SKILL.md` | **Update** — add Intercept Block + Stage 0 Scribe + Terminal Return |
| `skills/exploration-orchestrator/` (entire dir) | **Delete** |
| `skills/deferred/exploration-orchestrator/` (entire dir) | **Delete** |
| `README.md` | **Update** — remove orchestrator from tree listing |
| `references/architecture.md` | **Update** — replace orchestrator row |
| `references/post-run-survey.md` | **Update** — replace orchestrator references |
