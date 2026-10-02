---
name: user-story-capture
description: Derives, groups, and refines user stories from exploration captures, prototype behavior, and business context. Formats standard user stories and Gherkin acceptance criteria blocks.
---

# User Story Capture (user-story-capture)

Derives structured user stories and acceptance criteria from exploration captures and prototypes with prioritization for the first implementation slice.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Never invent actor personas or goals unsupported by exploration captures.
- Mark unverified stories and edge cases with `[UNCONFIRMED]`.
- Cite source document for every story (e.g., `(source: brd-draft.md)`).
- Include a mandatory `## Story Gaps` section for open questions and unconfirmed assumptions.

## Quick start
1. Select output format: `standard` (`As a / I want / So that`) or `gherkin` (`Given / When / Then`).
2. Run story extraction script or co-author interactively:
   ```bash
   python ./scripts/execute.py --input <file> --format <standard|gherkin> --output <file.md>
   ```
3. Prioritize stories and refine acceptance criteria with edge-case scenarios.

## Workflow
1. **Context Gathering**: Inquire about source captures, primary actor personas, exclusions, and desired AC format.
2. **Backlog Outlining**: Present numbered lightweight story titles, curate with user, and draft approved items.
3. **Reader Testing**: Predict 2 edge cases or failure modes per priority story and integrate test-driven ACs.
4. **Export**: Format backlog into standardized stories with priority rankings.

## Verification
- Confirm all stories cite supporting exploration or discovery documents.
- Validate that Gherkin scenarios adhere to single `When` clause guidelines.
- Ensure all gaps are logged in `## Story Gaps`.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
- [architecture.md](references/architecture.md)
