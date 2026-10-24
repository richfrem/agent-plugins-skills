# Design Rationale: Why the Exploration Cycle Works This Way

Distilled from the April 2026 design briefs and the June 2026 enforcement plan, which are retired. Read this to understand why the loop halts where it does; read [process-definition.md](process-definition.md) for what it does.

## Purpose and boundary

The cycle puts exploration into the hands of the people closest to a problem (Business Area Experts, Subject Matter Experts) with AI doing the analyst, designer and documentation work. Guarded exploration, including vibe coding, has a valuable place in an organisation **provided it has guardrails**. The boundary: a prototype articulates design and intent; it is not a production system. The output is structured, validated intent. Complex or sensitive systems still need a formal engineering cycle.

Four outcomes are valid and valuable: a throwaway prototype (kill a flawed idea at near-zero cost), Tier 1 direct deployment, Tier 2 security review with red teaming, Tier 3 handoff to formal engineering (tiers: see the handoff guide in `handing-off-to-engineering`).

## Why a state machine (the dashboard pattern)

**Problem.** The child skills were good, but the workflow skill was a narrative guide: it described phases and enforced nothing, and a new session had no state to resume from.

**Options weighed.** (1) Hard-fork a developer harness and rewrite it for business users: inherits its rigor but carries a permanent merge burden and couples the skills to the fork. (1.5) Keep the plugin model and rebuild the *pattern* inside our own workflow skill: no upstream merge debt, same determinism. (2) Plain routing with no gates: unrepeatable. (3) A web portal in front of the skills: the strongest democratisation, but needs its own engineering cycle, so it stays a later option. **Decision: 1.5**, borrow the pattern, not the code.

**Orchestrator loop** (six blocks, drawn in [orchestrator-loop.mmd](orchestrator-loop.mmd)):
1. Bootstrap (silent): no state yet means create it and ask for a short session name.
2. Read state (silent): active phase is the first incomplete one; verify the outcome file of every completed phase exists, and resolve any missing one before advancing.
3. Orientation summary (always shown): a short friendly status, then wait for soft confirmation.
4. Phase routing: Discovery Plan, Visual Blueprinting, Prototype, Handoff each go to their skill, with the context "you are part of an active session; return here when the phase is complete".
5. HARD-GATE: summarise what was produced (1 to 3 bullets), show the outcome path, ask for a clear yes. Do not record completion until the SME affirms. Changes requested: return to the phase skill and repeat.
6. Write state: mark the phase complete, set the next current phase, log date and one-line outcome, loop to block 3.
Completion: all four done, status Complete, point the team at `exploration/handoffs/handoff-package.md`.

**State authority.** The SQLite state engine is the source of truth (sessions, tasks, approvals, leases, nonces). `exploration/exploration-dashboard.md` is a read-only projection rendered from it (the seed template is the dashboard asset of this skill). The model must not tick checkboxes without a state transaction.

**Session hygiene (intended behaviour, not enforced by code today).** If a session is In Progress at bootstrap, ask whether to resume or archive it; archiving renames `exploration/` to `exploration-archive-YYYYMMDD-HHMMSS/` before a fresh state starts. Deterministic pre-write blocking of out-of-order writes was planned (a PreToolUse hook) and never built; see the plugin's map-debt ledger.

**Superseded: Dashboard Intercept.** Every child skill once began with "if an exploration dashboard exists and is not Complete, stop and redirect to the workflow skill". It was removed (a repository test asserts the text is gone) because the SessionStart hook plus the bootstrap gate in [using-exploration-cycle.md](using-exploration-cycle.md) now do that job once, centrally.

## Language for non-technical users

Never say: scaffold, repo, branch, commit, worktree, invoke, dispatch, iterate, initialize, spin up, phase, gate, spec, schema, subagent, context, tokens, pipeline, orchestrate, instantiate, decompose. Say: "let me save that", "I'll take a note of that", "we'll build this together", "here's what I heard, does this look right?", "build", "create", "set up", "put together". One question at a time, and confirm back in plain words before every transition.

| Engineering term | Say instead |
|---|---|
| brainstorming | Discovery Planning Session |
| writing plans | Discovery Plan |
| subagent-driven development | Subagent-driven prototyping |
| git worktree | Prototype Sandbox ("isolated workspace") |
| spec reviewer prompt | Spec Alignment Checker |
| verification before completion | Prototype Acceptance Check |
| code review | Spec Compliance Review |
| TDD | Prototype Validation Loop |
| commit / branch | Save Checkpoint / Prototype Version |

## Placeholder scan

Before an exploration can conclude, scan the emerging documents for TBD, TODO, contradictions and ambiguity ("the TDD of specs"). The deterministic version is `validate_phase_gate.py`.

## The five skills

| Skill | Absorbed |
|---|---|
| running-exploration-cycle | exploration-workflow, using-exploration-cycle, exploration-session-brief, discovery-planning, exploration-optimizer; agents intake, problem-framing, discovery-planning, exploration-cycle-orchestrator |
| capturing-business-requirements | business-requirements-capture, user-story-capture, business-workflow-doc; agents requirements-doc, prototype-companion |
| building-interactive-prototypes | prototype-builder, subagent-driven-prototyping, visual-companion; agent prototype-builder |
| handing-off-to-engineering | exploration-handoff; agents handoff-preparer, planning-doc |
| reengineering-vibe-code | the eight vibe-* skills; agents vibe-orchestrator, runtime-observer |

Four independent agents remain at plugin level: `business-rule-audit-agent`, `certification-verifier`, `domain-purity-auditor`, `semantic-drift-auditor`.

## Attribution

The conversational dashboard pattern, the blank-slate subagent logistics, the state-machine discipline and the HARD-GATE mechanism were inspired by and adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT licence), translated for non-technical experts. The plugin has no runtime dependency on it.
