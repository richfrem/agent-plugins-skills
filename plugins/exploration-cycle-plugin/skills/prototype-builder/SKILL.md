---
name: prototype-builder
description: Orchestrates the prototype build cycle from approved discovery plans to working prototypes and SME walkthroughs. Coordinates layout confirmation and component assembly.
---

# Prototype Builder (prototype-builder)

Orchestrates the prototype build cycle from approved Discovery Plans to working prototypes and SME walkthroughs.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Hard gate: No building may commence without an approved Discovery Plan in `exploration/discovery-plans/`.
- Coordinate build cycles without implementing code directly; delegate components to `subagent-driven-prototyping`.
- Always record raw walkthrough feedback to `exploration/captures/walkthrough-notes.md`.

## Quick start
1. Verify approved Discovery Plan exists in `exploration/discovery-plans/`.
2. Confirm layout direction with `visual-companion` in `exploration/captures/layout-direction.md`.
3. Dispatch component construction to `subagent-driven-prototyping` and guide SME walkthrough.

## Workflow
1. **Gate Check**: Verify plan approval in `exploration/discovery-plans/`; halt and redirect to planning if unapproved.
2. **Layout Direction**: Invoke `visual-companion` to capture wireframes or layout directions.
3. **Component Build**: Invoke `subagent-driven-prototyping` to assemble parts in `exploration/prototype/`.
4. **SME Walkthrough**: Walk the SME through main user journeys and document observations in `exploration/captures/walkthrough-notes.md`.
5. **Phase Handoff**: Synthesize notes into `exploration/captures/prototype-notes.md` and report completion.

## Verification
- Confirm `exploration/prototype/` contains runnable prototype assets.
- Validate that walkthrough notes capture all SME feedback and blocker items.
- Ensure all acceptance criteria from the Discovery Plan are evaluated.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
