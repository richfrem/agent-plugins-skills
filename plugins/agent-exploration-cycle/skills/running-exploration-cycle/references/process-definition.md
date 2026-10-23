# Exploration Process Definition (DRAFT, Slice 0b)

The canonical process in declarative form. [process-overview.mmd](process-overview.mmd) is the picture of the same thing. Each row has the same shape as a stage in the control plane's `transition_templates.yaml` (phase, gate, required artifacts, approver, next phases), so a future workflow-definition layer can load it without rewriting it.

## Phases

Four numbered phases match `validate_phase_gate.py`, the README and the old skill. Phase 0 (Intake) comes before them. Capture is a loop, not a phase. It runs inside Phase 1, after a prototype walkthrough, and as the Phase 4 scribe.

| Phase | Name | Owner skill | Required artifacts | Gate and check | Approver | Next | Skipped when |
|---|---|---|---|---|---|---|---|
| 0 | Intake | running-exploration-cycle | `exploration/session-brief.md` using the canonical headers | Gate 0: brief confirmed | SME | 1 | Never. Shorter for a re-entry spike. |
| 1 | Discovery Plan | running-exploration-cycle, then capturing-business-requirements | `exploration/discovery-plans/*.md` with `PLAN_STATUS: APPROVED` or `## SME Approval`; `captures/problem-framing.md`, `brd-draft.md`, `user-stories-draft.md` | HARD-GATE 1 (a DRAFT never satisfies); `validate_phase_gate 1`; `check_gaps` at most 3 per capture | SME | 2 | Never |
| 2 | Visual Blueprinting | building-interactive-prototypes | `captures/layout-direction.md` or `captures/document-structure.md` | Gate 2; `validate_phase_gate 2` | SME | 3 or 4 | Brownfield with established patterns (`[~]`) |
| 3 | Prototype | building-interactive-prototypes, capturing-business-requirements, business-rule-audit-agent | `exploration/prototype/` (`index.html`, `README.md`), `captures/walkthrough-notes.md`, `captures/prototype-notes.md`, `captures/business-rule-audit.md` | Gate 3: no CONTRADICTED or UNCERTAIN rule left; `validate_phase_gate 3` | SME | 4 | Analysis or docs sessions, discovery-only sessions |
| 4 | Handoff | handing-off-to-engineering | `exploration/handoffs/handoff-package.md` with a `## Risk Assessment` block and `**Tier:**`; `tier3-risk-summary.md` first for Tier 3 | Narrowing gate (5 readiness checks with evidence); Gate 4: `validate_phase_gate 4` and SME approval | SME | route by tier | Never |

## Entry paths

| Path | Trigger | Owner | Joins the process at |
|---|---|---|---|
| 1 Pre-build discovery | Nothing built yet | running-exploration-cycle | Phase 0 |
| 2 Vibe reengineering | A working prototype or code already exists | reengineering-vibe-code | Phase 4 handoff junction |
| 3 Technical discovery | Refactor, bug or subsystem, read-only | handing-off-to-engineering (diagnostic) | Phase 4 handoff junction |
| Re-entry | The engineering cycle found an unresolved ambiguity | handing-off-to-engineering (re-entry scoping) | Phase 0 |

## Exit routes (handoff junction)

Fail fast, Tier 1 self-deploy, Tier 2 review, Tier 3 formal engineering (user control plane, entry `os-control-intake`, called by name), or defer to the roadmap. One Tier-3 definition applies everywhere (contradiction C3 in the consolidation plan).

## Changes from the old documents

- `exploration_session.py` phase `2-requirements` becomes Phase 2 Visual Blueprinting (the validator and README already say so).
- The orchestrator guide's "Phase 2 to 3 requires user stories and behavioral tests" moves into the Phase 1 capture loop and Gate 3.
- Third-party spec and execution frameworks are no longer process steps (they are surveyed as optional constraints in `handing-off-to-engineering`), and neither is the planning-draft branch or the optimizer.
- Technical codebase discovery is shown as its own path.
- The shared exit junction replaces three separate handoff descriptions.
