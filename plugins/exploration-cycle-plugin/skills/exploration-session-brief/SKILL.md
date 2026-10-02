---
name: exploration-session-brief
description: Co-authors exploration session briefs at the wide end of the exploration funnel. Captures and refines core intent across software, business processes, or strategic roadmaps.
---

# Exploration Session Brief (exploration-session-brief)

Co-authors exploration session briefs at the wide end of the exploration funnel, capturing and refining core intent into structured, reader-tested briefs.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Remain solution-agnostic until domain requirements dictate otherwise.
- Never invent stakeholder personas, constraints, or unverified assumptions; flag gaps as `[UNCONFIRMED]`.
- Always write finalized briefs directly to `exploration/session-brief.md`.

## Quick start
1. Initiate context gathering with domain, trigger event, and raw material inputs.
2. Propose tailored outline: Problem Statement, Stakeholders, Current vs Desired State, Constraints, Open Questions.
3. Iteratively draft concise sections and perform reader blind-spot testing.

## Workflow
1. **Context Gathering**: Inquire in a single message regarding domain scope, trigger pain points, and existing transcripts or notes.
2. **Section Refinement**: Propose domain-tailored sections and draft iteratively (2–5 sentences per section).
3. **Reader Testing & Blind Spots**: Predict 3 specific unaddressed questions from the primary reader; resolve inline or record under `## Open Questions`.
4. **Finalization**: Package verified brief into `exploration/session-brief.md`.

## Verification
- Confirm `exploration/session-brief.md` exists and contains all required sections.
- Verify all unconfirmed assumptions are marked `[UNCONFIRMED]`.
- Ensure open reader questions are documented with explicit follow-up owners.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
- [architecture.md](references/architecture.md)
