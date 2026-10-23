# Vibe to Engineering Handoff Pipeline (formerly vibe-to-speckit-superpowers) (absorbed skill)

> Absorbed from the retired `vibe-to-speckit-superpowers` skill into `reengineering-vibe-code`, and renamed because the original name and output folders were tied to two third-party tools. All ten steps are unchanged. The package it produces goes to `handing-off-to-engineering`, the shared handoff for every path.
> Original trigger description: End-to-end pipeline that transforms an undocumented vibe-coded prototype into a specification package and an implementation-ready engineering handoff.

Transforms undocumented prototypes into a specification package and an engineering handoff.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints
- Maintain loose coupling: emit static specifications and tests without hard programmatic dependencies on external CLIs.
- Downstream coordination is mediated through natural-language handoff instructions.
- All 10 pipeline steps must validate cleanly before the final handoff package is emitted.

## Quick start
1. Verify the prototype is available and run the browser audit and runtime observer.
2. Progress through the 10 steps: Discovery, Characterization, Q&A, Specs, Extraction, Verification, Packaging, Certification, Summary, Bootstrap.
3. Deliver the compiled specification package and engineering handoff.

## Workflow
1. **Discovery & Telemetry**: run `vibe-browser-audit` and the runtime observer, writing `exploration/captures/DISCOVERY_REPORT.md`.
2. **Behavioral Safety Net**: run `vibe-behavioral-test-capture` to record characterization tests in `tests/characterization/`.
3. **Interactive Q&A**: capture domain and non-functional answers in `exploration/captures/architectural-qa.json`.
4. **Canonical Specs**: `vibe-togaf-architect` produces `specs/REQS.md` and `specs/domain-lexicon.json` (the written file set is `REQS.md` throughout; the TOGAF reference's `REQUIREMENTS.md` is the same contract under an older name).
5. **Domain Extraction**: `vibe-domain-extractor` isolates framework-free models in `/domain`.
6. **Drift & Truth Verification**: audit symbol drift and test-to-spec boundary compliance.
7. **Spec Packaging**: `vibe-spec-packager` scaffolds the `/handoff-spec/` and `/execution/` task packets.
8. **Certification Manifest**: validate that `exploration/certification-manifest.yaml` confirms every gate passed.
9. **Final Handoff Summary**: compile `exploration/handoffs/handoff-package.md` (the original wrote the singular `exploration/handoff/`, which the validator does not read).
10. **Sandbox Bootstrapping**: hand off the target repository ready for implementation, through `handing-off-to-engineering`.

## Verification
- All 10 pipeline artifacts exist in their designated locations.
- `exploration/certification-manifest.yaml` records passing statuses for all gates.
- The handoff package allows independent execution without legacy prototype dependencies.
