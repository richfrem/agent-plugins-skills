# Specification Packaging & Codebase Scaffolding (vibe-spec-packager) (absorbed skill)

> Absorbed from the retired `vibe-spec-packager` skill into `reengineering-vibe-code`. Rewritten in the consolidation to be framework-neutral: the original output folders and validator carried the names of two third-party tools. The constraints, file set and checks are unchanged.
> Original trigger description: Compiles verified architectural specs into a specification package, generates an execution handoff, and bootstraps a clean target codebase sandbox.

Compiles verified architectural specifications into a neutral specification package, builds an execution package for the receiving team, and scaffolds the target sandbox.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints
- Strict alignment: every task in `handoff-spec/tasks.md` must link to an explicit requirement in `handoff-spec/spec.md`.
- Never hand-author custom isolation, TDD or review prose; map to the receiving team's governing rules and skills. In this repository that means the `os-control-worktree` skill and the testing and review rules; elsewhere, whatever the team uses.
- Require passing alignment validation before declaring the packaging phase complete.
- Never overwrite existing project code or wipe folders without a safety check, and fit the scaffold to the stack approved in `specs/TECH_MAPPING.md` when that file exists (see the acceptance criteria).

## Quick start
1. Consolidate the verified `/specs` into the package under `/handoff-spec/`.
2. Generate the execution package under `/execution/` with the discipline mappings.
3. Validate alignment, then scaffold the clean target codebase directory under `target/`.

## Workflow
1. **Consolidate specifications**: generate `constitution.md` (project principles), `spec.md`, `plan.md`, `tasks.md`, `traceability.md` and `domain-lexicon.json`.
2. **Generate the execution package**: create `session-brief.md`, `execution-protocol.md` and `discipline-map.md` (isolation, testing and review disciplines, each mapped to the receiving team's rule or skill).
3. **Validate alignment**: check that every task maps to a requirement and every requirement to at least one task, and emit `reports/spec-task-alignment-report.json`. The original named a `speckit-superpowers-alignment-validator`; no such script exists in this repository, so the check is manual or needs a new validator (logged as map debt in the consolidation plan).
4. **Scaffold the target sandbox**: initialize the target repository layout, copying the pure domain code, the characterization tests and the specs.

## Verification
- `reports/spec-task-alignment-report.json` passes with zero unmapped tasks.
- Bidirectional traceability exists between requirements and implementation work packages.
- The bootstrapped target directory contains runnable characterization tests and pure domain models.
