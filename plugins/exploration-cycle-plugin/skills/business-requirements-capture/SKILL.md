---
name: business-requirements-capture
plugin: exploration-cycle-plugin
description: >
  Captures and refines business requirements, including functional requirements,
  non-functional requirements, business rules, constraints, assumptions, and
  success measures. Produces structured BRD-style documents with [CONFIRMED] and
  [UNCONFIRMED] confidence markers. Trigger with "capture requirements",
  "generate a BRD", "document business rules", "list the constraints", or
  "create a requirements document".
allowed-tools: Bash, Read, Write
---

# Business Requirements Capture (`business-requirements-capture`)

Generates structured Business Requirements Documents (BRDs) and business rules ledgers from exploration session captures.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Anti-hallucination**: Never invent requirements not explicitly documented or confirmed in source captures.
- **Scope discipline**: Do not make speculative architectural or technical decisions beyond user intent.
- **Confidence markers**: Mark explicit statements as `[CONFIRMED]` and inferences as `[UNCONFIRMED]`.
- **Prerequisite context**: Do not proceed without exploration session input context.

## Quick start

```bash
# Generate requirements document from input session capture
python ./scripts/execute.py --input <capture.md> --mode brd --output exploration/captures/brd.md
```

## Workflow

1. **Context Ingestion**: Inquire about input sources, output scope (`brd`, `rules`, `constraints`), and focus.
2. **Drafting & Marking**: Draft requirements tagging each item `[CONFIRMED]` or `[UNCONFIRMED]`.
3. **Consolidated Gaps**: Record all open assumptions in a `## Consolidated Gaps` ledger.
4. **Reader Testing**: Predict 3 specific questions the downstream engineer or PM will ask and resolve them inline.

## Verification

```bash
# Verify output document exists and contains required sections
test -f exploration/captures/brd.md && grep -E "CONFIRMED|UNCONFIRMED" exploration/captures/brd.md
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and confidence marking rules.
