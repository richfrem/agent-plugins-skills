# Exploration Workflow Orchestration Guide

Comprehensive reference guide for the Business Exploration Loop orchestrator (`exploration-workflow`).

## Contents

- [Session Types & Phase Activation](#session-types--phase-activation)
- [Pre-Flight & Dispatch Setup](#pre-flight--dispatch-setup)
- [Bootstrap Protocol & Dashboard Schema](#bootstrap-protocol--dashboard-schema)
- [State Reading & Resume Protocol](#state-reading--resume-protocol)
- [Phase Routing & Hard-Gate Enforcement](#phase-routing--hard-gate-enforcement)
- [Task Ledger & Isolation](#task-ledger--isolation)
- [Gotchas & Failure Modes](#gotchas--failure-modes)

---

## Session Types & Phase Activation

| Type | Intent | Active Phases |
|------|--------|---------------|
| **Greenfield** | Building new app/system from scratch | All 4 phases |
| **Brownfield** | Adding feature or legacy analysis | Phase 1 required; Phase 3 modifies codebase |
| **Analysis/Docs** | Non-software deliverables (BRD, process map, policy) | Phases 1 & 4 required; Phase 3 skipped |
| **Spike** | Timeboxed proof-of-concept / tech validation | Phase 1 required; iterations flexible |

---

## Pre-Flight & Dispatch Setup

Select the worker dispatch model:
1. A `cli-agent` backend (copilot, agy, claude, codex or local), when an external CLI is installed and authorized
2. `claude-subagents` (in-session sub-agents)
3. `direct` (main context execution)

See [dispatch-strategies.md](dispatch-strategies.md); model and runtime choices belong to the `cli-agent` skill.

---

## Bootstrap Protocol & Dashboard Schema

Initialize `exploration/exploration-dashboard.md`:

```markdown
# Exploration Session Dashboard
**Status:** In Progress
**Session Type:** [Greenfield / Brownfield / Analysis / Spike]
**Active Phase:** Phase 1 — Discovery Planning
**Dispatch Strategy:** [Selected strategy]

## Phases
- [ ] Phase 1: Discovery Planning (`discovery-planning`)
- [ ] Phase 2: Behavioral Capture (`visual-companion` / `vibe-behavioral-test-capture`)
- [ ] Phase 3: Prototyping (`subagent-driven-prototyping` / `prototype-builder`)
- [ ] Phase 4: Handoff Package (`exploration-handoff`)

## Session Artifacts
- Brief: `exploration/session-brief.md`
- Discovery Plan: `exploration/discovery-plans/`
- Captures: `exploration/captures/`
- Prototypes: `exploration/prototype/`
- Handoff: `exploration/handoffs/`
```

---

## State Reading & Resume Protocol

When user asks to resume or check status:
1. Read `exploration/exploration-dashboard.md`.
2. Inspect last completed phase from HANDOFF_BLOCKs.
3. Present plain-language status recap to SME before proceeding.

---

## Phase Routing & Hard-Gate Enforcement

At each phase gate:
- **Phase 1 -> 2**: Requires explicit approval of Discovery Plan.
- **Phase 2 -> 3**: Requires the SME's confirmation of the layout direction (`captures/layout-direction.md` or `document-structure.md`); user stories and behavioral notes are checked in the Phase 1 capture loop and at Gate 3.
- **Phase 3 -> 4**: Requires verified prototype artifacts.
- **Phase 4 Completion**: Requires finalized handoff package and TierGate risk determination.

---

## Task Ledger & Isolation

- Maintain a living task ledger throughout the session.
- Break Phase 3 implementation into manageable slices, each with a validation check.
- Isolate prototyping in a dedicated workspace using the `os-control-worktree` skill (rules in the Phase 3 reference of `building-interactive-prototypes`).

---

## Gotchas & Failure Modes

- **Silent Skip**: Never skip Phase 1 gate even if user insists "just build it".
- **Dashboard Synchronization**: Always update `**Status:**` and active phase checkboxes upon phase completion.
- **Analysis/Docs Phase 3**: Phase 3 must remain skipped (`- [~]`) for non-software sessions.
