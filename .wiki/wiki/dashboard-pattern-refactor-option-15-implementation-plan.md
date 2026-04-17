---
concept: dashboard-pattern-refactor-option-15-implementation-plan
source: plugin-code
source_file: exploration-cycle-plugin/docs/superpowers/plans/2026-04-06-dashboard-pattern-refactor.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.578641+00:00
cluster: orchestrator
content_hash: ff35ab4093005026
---

# Dashboard Pattern Refactor (Option 1.5) Implementation Plan

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Dashboard Pattern Refactor (Option 1.5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the exploration-cycle-plugin to implement the Dashboard Pattern — a stateful 4-phase SME orchestrator backed by `exploration-dashboard.md` — replacing the existing narrative-only `exploration-workflow` and retiring the stub `exploration-orchestrator`.

**Architecture:** `exploration-workflow` becomes a rigid state machine with 6 ordered blocks (Bootstrap → Read State → Orientation → Route → HARD-GATE → Dashboard Write). Shared state is maintained in `exploration-dashboard.md` in the user's workspace. Child skills gain a Dashboard Intercept block (redirect if session active) and a Terminal Return block (hand back to orchestrator on completion). `exploration-handoff` absorbs the Scribe Phase as Stage 0.

**Tech Stack:** Markdown prompt engineering only. No code, no scripts, no dependencies. All changes are to `.md` files within the plugin.

**Design Doc:** `docs/superpowers/specs/2026-04-06-dashboard-pattern-refactor-design.md`

---

## File Map

| File | Action |
|---|---|
| `assets/templates/exploration-dashboard.md` | **Create** |
| `skills/exploration-workflow/SKILL.md` | **Rewrite** |
| `skills/discovery-planning/SKILL.md` | **Update** — Intercept + Terminal Return |
| `skills/visual-companion/SKILL.md` | **Update** — Intercept + Terminal Return |
| `skills/subagent-driven-prototyping/SKILL.md` | **Update** — Intercept + Orchestrator Context + Terminal Return |
| `skills/exploration-handoff/SKILL.md` | **Update** — Intercept + Stage 0 Scribe + Terminal Return |
| `skills/exploration-orchestrator/` (entire dir) | **Delete** |
| `skills/deferred/exploration-orchestrator/` (entire dir) | **Delete** |
| `README.md` | **Update** — remove orchestrator from tree |
| `references/architecture.md` | **Update** — replace orchestrator row |
| `references/post-run-survey.md` | **Update** — update title and orchestrator references |

---

## Task 1: Create the Dashboard Template

**Files:**
- Create: `assets/templates/exploration-dashboard.md`

- [ ] **Step 1: Create the `assets/templates/` directory and write the template**

  Create `assets/templates/exploration-dashboard.md` with this exact content:

  ```markdown
  # Business Exploration Dashboard

  **Session:** [to be filled in]
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

- [ ] **Step 2: Verify the file was created correctly**

  Run: `cat plugins/exploration-cycle-plugin/assets/templates/exploration-dashboard.md`
  Expected: Full template content shown, 4 unchecked `- [ ]` phase entries, Session Log table present.

- [ ] **Step 3: Commit**

  ```bash
  git add plugins/exploration-cycle-plugin/assets/templates/exploration-dashboard.md
  git com

*(content truncated)*

## See Also

- [[design-spec-dashboard-pattern-refactor-option-15]]
- [[sme-orchestrator-option-15-detailed-implementation-plan]]
- [[option-15-sme-orchestrator-implementation---copilot-prompt]]
- [[exploration-cycle-plugin-upgrade-implementation-plan]]
- [[implementation-plan-feature]]
- [[spec-kittyplan---create-implementation-plan]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/docs/superpowers/plans/2026-04-06-dashboard-pattern-refactor.md`
- **Indexed:** 2026-04-17T06:42:09.578641+00:00
