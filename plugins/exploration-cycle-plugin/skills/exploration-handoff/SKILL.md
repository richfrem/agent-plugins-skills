---
name: exploration-handoff
plugin: exploration-cycle-plugin
description: >
  Interactive co-authoring skill for the narrow end of the exploration funnel.
  Synthesizes session briefs, BRDs, story sets, and prototype notes into a
  structured handoff package targeted at the correct downstream consumer.
allowed-tools: Bash, Read, Write
---

# Exploration Handoff (`exploration-handoff`)

Synthesizes session briefs, BRDs, story sets, and prototype notes into a structured handoff package targeted at the downstream consumer.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Source grounding**: Never invent missing requirements or assumptions during handoff packaging.
- **Risk evaluation**: All handoff packages must evaluate risk tiers (Tier 1 low, Tier 2 moderate, Tier 3 formal SDLC).
- **Reader testing**: Predict 3 specific blocker questions the consumer will ask and resolve them inline or mark in `## Unresolved Ambiguity`.

## Quick start

```bash
# Verify exploration artifacts exist before drafting handoff package
ls -la exploration/
```

## Workflow

1. **Automated Scribe Capture**: Ingest briefs, user stories, BRDs, and diagrams from `exploration/captures/`.
2. **Audience Mapping**: Determine recipient (Engineering, Executive Sponsor, Operations, Security).
3. **Risk Tier Assessment**: Assign Tier 1 (direct deployment), Tier 2 (review needed), or Tier 3 (formal SDLC).
4. **Synthesis & Reader Testing**: Compile handoff package and resolve potential consumer blocker questions.
5. **Finalize**: Output `exploration/handoffs/handoff-package.md`, emit `HANDOFF_BLOCK`, and yield to `exploration-workflow`.

## Verification

```bash
# Verify handoff package exists and contains risk tier
test -f exploration/handoffs/handoff-package.md && grep -E "RISK_TIER|HANDOFF_BLOCK" exploration/handoffs/handoff-package.md
```

## References

- [exploration-handoff-guide.md](references/exploration-handoff-guide.md) — Complete Tier 1-3 schemas and TierGate criteria.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and delivery path criteria.
