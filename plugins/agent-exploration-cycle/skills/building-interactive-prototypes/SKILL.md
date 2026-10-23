---
name: building-interactive-prototypes
plugin: agent-exploration-cycle
description: >
  Takes an approved Discovery Plan to a working, clickable prototype: presents plain-language layout
  options (A, B, C), builds the prototype component by component with a review after each, and walks
  the expert through it. Use when the user says "build the prototype", "let's build it", "show me a
  working version", "what should it look like", "layout options", "wireframe" or "walk me through
  it", and an approved plan exists. Not for production code or for reengineering an existing app.
allowed-tools: Bash, Read, Write
---

# Building Interactive Prototypes

Phases 2 and 3: [prototyping-chain.mmd](references/prototyping-chain.mmd).

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **Gate**: build nothing until `exploration/discovery-plans/` holds an approved plan (`PLAN_STATUS: APPROVED` or `## SME Approval`). Existence of a file is not approval.
- Offer three distinct layout options in plain language before any code; brownfield sessions with established patterns may skip (`[~]`).
- Build 3 to 6 components, one at a time; advance only when a component is `COMPLETE` (other states: `BLOCKED`, `NEEDS_CONTEXT`). Review each for plan alignment, then quality.
- Work in an isolated workspace using the `os-control-worktree` skill; with the expert say "isolated workspace" and "validation check", never git or TDD terms ([language table](references/phase3-execution-discipline.md)).
- Write only the raw `walkthrough-notes.md`; structured notes come from `capturing-business-requirements`.
- Pick runtime and model through the `cli-agent` skill; never name models.

## Quick start

```bash
ls exploration/discovery-plans/ && ls exploration/captures/layout-direction.md
python3 ../running-exploration-cycle/scripts/validate_phase_gate.py 2
```

## Workflow

1. Gate check, then layout options and confirmation into `exploration/captures/layout-direction.md` (or `document-structure.md`).
2. Decompose, build and review each component into `exploration/prototype/`; assemble `index.html` and a `README.md`.
3. Walk the expert through each main flow; record `exploration/captures/walkthrough-notes.md`.
4. Hand over for observation extraction and the business-rule audit; report `PHASE 3 COMPLETE`.

## Verification

```bash
python3 ../running-exploration-cycle/scripts/validate_phase_gate.py 3
```

Acceptance criteria: [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Absorbed skills: [visual-companion.md](references/visual-companion.md) (layout options) • [prototype-builder.md](references/prototype-builder.md) (phase coordinator) • [subagent-driven-prototyping.md](references/subagent-driven-prototyping.md) (component loop)
- Guides: [prototyping-build-guide.md](references/prototyping-build-guide.md) (build modes, review) • [phase3-execution-discipline.md](references/phase3-execution-discipline.md) (isolation, language, why validate) • [prototype-builder-agent.md](references/prototype-builder-agent.md) (walkthrough script) • [acceptance criteria](references/prototype-builder-acceptance-criteria.md)
