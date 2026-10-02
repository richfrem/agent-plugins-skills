---
name: humanize
plugin: dev-utils
description: Transforms synthetic, stiff, or AI-flavored text into natural writing with authentic human rhythm, tone, and personality.
allowed-tools: Read
---

# Humanize Writing (`humanize`)

Transforms synthetic, stiff, or over-polished writing into natural text with an authentic human voice and rhythm.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Preserve Source Facts**: Never invent claims, details, or statistics not present in the original text.
2. **Default Output**: Return rewritten text directly without conversational preamble or throat-clearing.
3. **Voice First**: Do not merely strip bad patterns; replace them with natural character, rhythm, and concrete specifics.

## Quick start

Identify the target channel and review the patterns catalog:

```bash
cat plugins/dev-utils/skills/humanize/references/patterns.md
```

## Workflow

1. **Diagnose Fingerprints**: Internally identify AI markers (triads, em dashes, semicolons, hollow filler) and the core factual thesis.
2. **Rewrite with Specifics**:
   - Prefer concrete details over abstractions ("cut latency in half" vs "improved performance").
   - Maintain one clear idea per sentence and vary cadence across paragraphs.
   - Calibrate register to the destination medium (LinkedIn, technical email, blog post, Slack).
3. **Channel Formatting**: If a claim is pruned for lacking source evidence, append a footnote: `*(Removed: "X" -- no supporting detail in source.)*`.

## Verification

Run self-evaluative quality checks against the rewritten output:
- **Read-Aloud Test**: Does the text sound natural when spoken aloud?
- **Fingerprint Scan**: Confirm that hollow transitions ("Moreover", "Delve", "Crucial") and inflated adjectives are removed.
- **Channel Fit**: Verify length and formatting meet constraints in `channel-rules.md`.

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for voice rewriting and quality gates.
- [channel-rules.md](references/channel-rules.md) — Channel-specific length, structure, and formatting constraints.
- [patterns.md](references/patterns.md) — Comprehensive catalogue of artificial and synthetic writing patterns.
