---
name: capturing-business-requirements
plugin: agent-exploration-cycle
description: >
  Captures what a business explorer knows as structured documents: business requirements (BRD with
  rules, constraints, assumptions), user stories with acceptance criteria, Mermaid workflow
  diagrams, and prototype observation notes. Use when the user says "capture requirements",
  "generate a BRD", "document business rules", "list the constraints", "write user stories",
  "Gherkin acceptance criteria", "map this process", "draw the approval flow", or after a prototype
  walkthrough. Not for architecture specs or engineering plans.
allowed-tools: Bash, Read, Write
---

# Capturing Business Requirements

Capture loop shown in [capture-loop.mmd](references/capture-loop.mmd). It runs inside Phase 1, after a prototype walkthrough, and as the Phase 4 scribe.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **Never invent.** Only record what the captures or the SME state; mark inferences `[UNCONFIRMED]` and explicit statements `[CONFIRMED]`. Do not promote without SME sign-off.
- **Gap marker**: the exact string `[NEEDS HUMAN INPUT]` (reason in parentheses after it). `check_gaps.py` counts it; any variation is missed. It must not appear in the final handoff.
- Track each open decision once under `## Consolidated Gaps`; treat `Decision Pre-fills` in the brief as confirmed.
- One capture mode per invocation; cite the source file for every story and rule.
- `prototype-notes.md` has a single writer: the observation extraction in [prototype-companion-agent.md](assets/prompts/prototype-companion-agent.md).
- Cheap multi-pass work goes through the `cli-agent` skill using the prompt templates here; never name models.

## Quick start

From this skill's folder:

```bash
python3 scripts/business_requirements_capture_execute.py --input <capture.md> --mode brd --output exploration/captures/brd-draft.md
python3 scripts/user_story_capture_execute.py --input <brd-draft.md> --format gherkin --output exploration/captures/user-stories-draft.md
python3 scripts/generate_workflow.py --input <brd-draft.md> --output exploration/captures/workflow-map.md --type flowchart
```

## Workflow

1. Ingest the brief and approved plan; pick the mode (problem framing, BRD, stories, issues and opportunities, workflow, prototype observations).
2. Draft with markers and a Consolidated Gaps section; run `check_gaps` (more than 3 gaps in a capture sends the session back to the brief).
3. Reader test: predict the questions the consumer will ask and resolve them inline.
4. Hand the captures back to `running-exploration-cycle`.

## Verification

```bash
python3 ../running-exploration-cycle/scripts/check_gaps.py --files exploration/captures/*.md --threshold 3
```

Acceptance criteria: [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Absorbed skills: [business-requirements-capture.md](references/business-requirements-capture.md) (BRD modes) • [user-story-capture.md](references/user-story-capture.md) (story formats, edge cases) • [business-workflow-doc.md](references/business-workflow-doc.md) (diagram types)
- Prompt templates for cheap CLI passes: [requirements-doc-agent.md](assets/prompts/requirements-doc-agent.md) (five capture modes) • [prototype-companion-agent.md](assets/prompts/prototype-companion-agent.md) (walkthrough to notes)
