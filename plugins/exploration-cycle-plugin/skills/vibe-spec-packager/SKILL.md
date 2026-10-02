---
name: vibe-spec-packager
description: Compiles verified architectural specs into Spec Kit-compatible specification packages, generates Superpowers-ready execution handoffs, and bootstraps clean target codebase sandboxes.
---

# Specification Packaging & Codebase Scaffolding (vibe-spec-packager)

Compiles verified architectural specifications into Spec Kit packages, builds Superpowers execution packages, and scaffolds target sandboxes.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Strict alignment: Every task in `speckit/tasks.md` must link to an explicit requirement in `speckit/spec.md`.
- Never hand-author custom isolation/TDD/review prose; map directly to governing Superpowers skills.
- Require passing alignment validation prior to declaring the packaging phase complete.

## Quick start
1. Consolidate verified `/specs` into standard Spec Kit structure under `/speckit/`.
2. Generate Superpowers execution package under `/superpowers/` with discipline mappings.
3. Validate alignment report and scaffold target clean codebase directory under `target/`.

## Workflow
1. **Consolidate Specifications**: Generate `constitution.md`, `spec.md`, `plan.md`, `tasks.md`, `traceability.md`, and `domain-lexicon.json`.
2. **Generate Superpowers Package**: Create `session-brief.md`, `execution-protocol.md`, and `discipline-map.md`.
3. **Validate Alignment**: Run `speckit-superpowers-alignment-validator` and emit report.
4. **Scaffold Target Sandbox**: Initialize target repository layout copying pure domain code, characterization tests, and specs.

## Verification
- Confirm `reports/speckit-superpowers-alignment-report.json` passes with zero unmapped tasks.
- Verify bidirectional traceability between requirements and implementation work packages.
- Ensure bootstrapped target directory contains runnable characterization tests and pure domain models.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
