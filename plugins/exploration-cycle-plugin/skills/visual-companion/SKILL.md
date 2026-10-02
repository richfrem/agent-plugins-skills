---
name: visual-companion
description: Presents plain-language layout options (Option A, B, C) to the Subject Matter Expert before prototype construction begins, confirming visual structure and direction.
---

# Visual Companion (visual-companion)

Presents plain-language layout and structural options to the Subject Matter Expert before prototype construction begins.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Always present 3 distinct plain-language options (Option A, B, C) before writing any UI or prototype code.
- Record confirmed structural decisions directly into `exploration/captures/layout-direction.md`.
- Brownfield sessions with established design patterns may skip layout options by marking `- [~]`.

## Quick start
1. Read approved Discovery Plan from `exploration/discovery-plans/`.
2. Classify output archetype (Software UI, Process Flow, or Document/Analysis).
3. Present 3 plain-language structural choices and record confirmed direction.

## Workflow
1. **Plan Ingestion**: Review requirements and identify primary archetype.
2. **Option Presentation**: Formulate 3 distinct layout concepts (e.g. single-page vs wizard vs master-detail) and present them to the user.
3. **Feedback Capture**: Refine options based on user feedback and agree on the final layout direction.
4. **Persistence**: Write confirmed direction to `exploration/captures/layout-direction.md`.
5. **Phase Sign-Off**: Signal Phase 2 completion and hand off to `prototype-builder`.

## Verification
- Confirm `exploration/captures/layout-direction.md` exists with selected layout and SME notes.
- Verify user explicit agreement is documented before Phase 3 prototype building starts.
- Ensure chosen layout maps directly to requirements in the Discovery Plan.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
- [copilot_proposer_prompt.md](references/copilot_proposer_prompt.md)
- [program.md](references/program.md)
