---
name: adr-management
plugin: dev-utils
description: Scaffolds, lists, searches, and manages Architecture Decision Records (ADRs) to record permanent institutional memory.
allowed-tools: Bash, Read, Write
---

## Dependencies

Requires Python 3.8+ (standard library only).

---

# Architecture Decision Records (`adr-management`)

Manages Architecture Decision Records to ensure significant technical and architectural choices are permanently documented.

## Contents

- [Dependencies](#dependencies)
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Querying ADRs](#querying-adrs)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Fill All Sections**: Never leave an ADR partially empty; extrapolate context, decision, consequences, and alternatives.
2. **Filename Convention**: Always format filenames as `NNN-short-descriptive-title.md`.
3. **Status Lifecycle**: Mark new records `Proposed` or `Accepted`; mark superseded records `Superseded` with links.

## Quick start

Create a new ADR with an automatic sequential ID:

```bash
python3 scripts/adr_manager.py create "Title" --context "Context" --decision "Decision" --consequences "Consequences"
```

## Workflow

1. **Scaffold Record**: Run `adr_manager.py create "<Title>"` to create the template file in `docs/architecture/decisions/` or `ADRs/`.
2. **Populate Content**: Open the generated file and document technical context, rationale, consequences, and alternatives.
3. **Cross-Reference**: Link related decisions by number (e.g. `ADR-003`).

## Querying ADRs

- **View Record**: `python3 scripts/adr_manager.py get <NUMBER>`
- **Search Keywords**: `python3 scripts/adr_manager.py search "<KEYWORD>"`
- **Next Number**: `python3 scripts/next_number.py --type adr`

## Verification

List existing ADRs and verify sequential indexing:

```bash
python3 scripts/adr_manager.py list
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for ADR scaffolding and indexing.
