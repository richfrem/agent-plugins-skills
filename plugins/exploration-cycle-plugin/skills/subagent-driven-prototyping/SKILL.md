---
name: subagent-driven-prototyping
description: Builds prototypes component by component, conducting self-reviews against the Discovery Plan before advancing. Handles greenfield, brownfield, and plugin prototyping slices.
---

# Subagent-Driven Prototyping (subagent-driven-prototyping)

Builds prototypes component by component, self-reviewing each against the Discovery Plan before advancing.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Only advance to the next component when the current component self-review passes and status is `COMPLETE`.
- Build in isolated worktrees or dedicated prototype directories (`exploration/prototype/`).
- Never skip plan verification gates between component builds.

## Quick start
1. Verify presence of approved Discovery Plan and layout direction documents.
2. Decompose build into 3–6 manageable parts (e.g. navigation, controls, data view).
3. Execute iterative build loop: assemble, review, mark `COMPLETE`, and link in `index.html`.

## Workflow
1. **Pre-flight**: Confirm approved Discovery Plan in `exploration/discovery-plans/` and layout in `exploration/captures/`.
2. **Decomposition**: Break the prototype scope into 3–6 modular components.
3. **Build Loop**: Implement each component incrementally matching session mode (greenfield, brownfield, or plugin).
4. **Self-Review**: Compare implementation against Discovery Plan acceptance criteria.
5. **Assembly**: Link finished components into `exploration/prototype/index.html` and produce a completion handoff block.

## Verification
- Confirm all defined components compile or render correctly in `exploration/prototype/`.
- Validate test execution or behavioral assertions for critical logic.
- Verify status for every component in the task ledger is marked `COMPLETE`.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
- [cheapest_models.md](references/cheapest_models.md)
- [copilot_proposer_prompt.md](references/copilot_proposer_prompt.md)
- [program.md](references/program.md)
- [prototyping-build-guide.md](references/prototyping-build-guide.md)
