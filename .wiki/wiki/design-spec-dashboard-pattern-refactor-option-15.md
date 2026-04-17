---
concept: design-spec-dashboard-pattern-refactor-option-15
source: plugin-code
source_file: exploration-cycle-plugin/docs/superpowers/specs/2026-04-06-dashboard-pattern-refactor-design.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.581697+00:00
cluster: phase
content_hash: c3ab19ea648514a8
---

# Design Spec: Dashboard Pattern Refactor (Option 1.5)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
> "Welcome back! Here's where we a

*(content truncated)*

## See Also

- [[dashboard-pattern-refactor-option-15-implementation-plan]]
- [[sme-orchestrator-option-15-detailed-implementation-plan]]
- [[option-15-sme-orchestrator-implementation---copilot-prompt]]
- [[optimizer-engine-patterns-reference-design]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[optimizer-engine-patterns-reference-design]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/docs/superpowers/specs/2026-04-06-dashboard-pattern-refactor-design.md`
- **Indexed:** 2026-04-17T06:42:09.581697+00:00
