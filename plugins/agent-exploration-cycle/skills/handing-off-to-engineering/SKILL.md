---
name: handing-off-to-engineering
plugin: agent-exploration-cycle
description: >
  Closes exploration and routes the result: assesses risk and rigor (tiers 1 to 3), writes the
  handoff package for the right consumer, runs read-only technical codebase discovery that produces
  a diagnostic brief, and scopes a re-entry when engineering finds an unresolved ambiguity. Use when
  the user says "prepare the handoff", "hand this to engineering", "what risk tier is this", "write
  the handoff package", "diagnose this codebase before we change it", or "we hit an unknown during
  the build". Not for writing the specification or implementing.
allowed-tools: Bash, Read, Write
---

# Handing Off to Engineering

Shared exit for all paths: [handoff-junction.mmd](references/handoff-junction.mmd).

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

- **Source grounding**: never invent requirements; cite the capture for every major claim.
- **One Tier-3 rule** ([handoff guide](references/exploration-handoff-guide.md)): Tier 3 means a formal engineering cycle, never "deploy after review". Write `tier3-risk-summary.md` first and put it at the top of the package. Q5 alone is Tier 2 with ethics review.
- **Final package**: no `[NEEDS HUMAN INPUT]`; unresolved items become `[UNCONFIRMED]` with a reason plus a `## Deferred Gaps` list; every readiness check carries evidence; emit `PHASE 4 COMPLETE`.
- **Technical discovery is read-only**: no source changes outside `exploration/`.
- **Control plane**: for structured engineering name the `os-control-intake` skill; do not import or path into `agent-agentic-os`.
- Pick runtime and model through the `cli-agent` skill; never name models.

## Quick start

From this skill's folder:

```bash
python3 scripts/technical_diagnostic_engine.py --task-id <id> --title "<title>" --output exploration/DIAGNOSTIC_BRIEF.md
python3 ../running-exploration-cycle/scripts/validate_phase_gate.py 4
```

## Workflow

1. Scribe: fill any missing capture via `capturing-business-requirements`.
2. Assess the five risk questions; choose the delivery path and format; write `exploration/handoffs/handoff-package.md`.
3. Placeholder sweep, then reader test (three blocker questions for the consumer).
4. Validate, get SME approval, route: self-deploy, review, formal engineering via `os-control-intake`, or defer.
5. Re-entry: quote the engineering ambiguity verbatim, draft a new session brief for `running-exploration-cycle`.

## Verification

```bash
python3 -m pytest scripts -q
```

Acceptance criteria: [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- [exploration-handoff.md](references/exploration-handoff.md) (absorbed skill) • [exploration-handoff-guide.md](references/exploration-handoff-guide.md) (tiers, formats) • [exploration-output-standards.md](references/exploration-output-standards.md) (portable outputs)
- [engineering-cycle-contract.md](references/engineering-cycle-contract.md) (what engineering expects, gates, re-entry) • [external-spec-frameworks.md](references/external-spec-frameworks.md) (optional third-party constraints)
- [planning-doc-agent.md](references/planning-doc-agent.md) (re-entry scoping and planning drafts) • [handoff-preparer-agent.md](assets/prompts/handoff-preparer-agent.md) (CLI synthesis template)
