# Exploration Workflow Orchestration Guide

Comprehensive reference guide for the Business Exploration Loop orchestrator (`exploration-workflow`).

## Contents

- [Session Types & Phase Activation](#session-types--phase-activation)
- [Pre-Flight & Dispatch Setup](#pre-flight--dispatch-setup)
- [Bootstrap Protocol & Dashboard Schema](#bootstrap-protocol--dashboard-schema)
- [State Reading & Resume Protocol](#state-reading--resume-protocol)
- [Phase Routing & Hard-Gate Enforcement](#phase-routing--hard-gate-enforcement)
- [Superpowers Integration & Task Ledger](#superpowers-integration--task-ledger)
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
1. `copilot-cli` (default if GitHub Copilot installed)
2. `gemini-cli` (Google Gemini CLI available)
3. `claude-subagents` (Anthropic subagents in-session)
4. `direct` (main context execution)

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
- **Phase 2 -> 3**: Requires validation of user stories and behavioral tests.
- **Phase 3 -> 4**: Requires verified prototype artifacts.
- **Phase 4 Completion**: Requires finalized handoff package and TierGate risk determination.

---

## Superpowers Integration & Task Ledger

- Maintain a living task ledger throughout the session.
- Break Phase 3 implementation into manageable slices with TDD test coverage.
- If using `orba/superpowers`, isolate prototyping in dedicated worktrees.

---

## Gotchas & Failure Modes

- **Silent Skip**: Never skip Phase 1 gate even if user insists "just build it".
- **Dashboard Synchronization**: Always update `**Status:**` and active phase checkboxes upon phase completion.
- **Analysis/Docs Phase 3**: Phase 3 must remain skipped (`- [~]`) for non-software sessions.
