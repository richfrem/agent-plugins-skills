---
concept: business-exploration-dashboard
source: plugin-code
source_file: exploration-cycle-plugin/assets/templates/exploration-dashboard.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.599927+00:00
cluster: phase
content_hash: 75e8949505a7271e
---

# Business Exploration Dashboard

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Business Exploration Dashboard

**Session:** [to be filled in]
**Session Type:** [Greenfield | Brownfield | Analysis/Docs | Spike]
**Dispatch Strategy:** [copilot-cli | claude-subagents | direct]
**Current Phase:** Phase 1 — Problem Framing
**Status:** In Progress

---

## The Exploration Loop

Phases marked `[~]` are intentionally skipped for this session type.

- [ ] **Phase 1: Problem Framing**
  - Skill: `discovery-planning`
  - Gate: SME approval of Discovery Plan
  - Outcome: `exploration/discovery-plans/discovery-plan-YYYY-MM-DD.md`

- [ ] **Phase 2: Visual Blueprinting**
  - Skill: `visual-companion`
  - Gate: SME selection and confirmation of layout direction
  - Outcome: `exploration/captures/layout-direction.md`

- [ ] **Phase 3: Build**
  - Skill: `subagent-driven-prototyping`
  - Gate: SME walkthrough and sign-off on working build
  - Outcome (Greenfield): `exploration/prototype/index.html`
  - Outcome (Brownfield): Changes in existing codebase + `exploration/prototype/README.md`

- [ ] **Phase 4: Handoff & Specs**
  - Skill: `exploration-handoff`
  - Gate: SME approval of final handoff package
  - Outcome: `exploration/handoffs/handoff-package.md`

---

## Session Type Guide

| Type | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|------|---------|---------|---------|---------|
| **Greenfield** (new app) | Required | Required | Standalone prototype | Required |
| **Brownfield** (existing app) | Required | Optional | Builds into codebase | Optional |
| **Analysis/Docs** (non-software) | Required | Optional (structure) | Skipped | Required (primary output) |
| **Spike** (investigation) | Required, may repeat | Flexible | Flexible | Optional |

---

## Session Log

| Phase | Completed | Notes |
|-------|-----------|-------|
| Phase 1 | — | — |
| Phase 2 | — | — |
| Phase 3 | — | — |
| Phase 4 | — | — |


## See Also

- [[agent-execution-prompt-exploration-cycle-plugin-upgrade]]
- [[bae-quick-start-guided-exploration-process]]
- [[business-rule-audit-agent]]
- [[business-requirements-capture]]
- [[opportunity-3-exploration-design]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/templates/exploration-dashboard.md`
- **Indexed:** 2026-04-17T06:42:09.599927+00:00
