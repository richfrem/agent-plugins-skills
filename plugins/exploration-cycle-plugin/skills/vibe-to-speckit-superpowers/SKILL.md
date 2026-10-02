---
name: vibe-to-speckit-superpowers
description: End-to-end pipeline that transforms an undocumented vibe-coded prototype into a Spec Kit-compatible specification package and a Superpowers-ready implementation handoff.
---

# Vibe to Spec Kit & Superpowers Pipeline (vibe-to-speckit-superpowers)

Transforms undocumented prototypes into Spec Kit specifications and Superpowers implementation handoffs.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)

## Critical Constraints
- Maintain loose coupling: Emit static specifications and tests without hard programmatic dependencies on external CLIs.
- Downstream coordination is mediated via natural language handoff instructions.
- Ensure all 10 pipeline steps validate cleanly before emitting the final handoff package.

## Quick start
1. Verify prototype availability and execute browser audit and runtime observer.
2. Progress through 10-step pipeline: Discovery -> Characterization -> Q&A -> Specs -> Extraction -> Verification -> Packaging -> Certification -> Summary -> Bootstrap.
3. Deliver compiled Spec Kit and Superpowers handoff packages.

## Workflow
1. **Discovery & Telemetry**: Run `vibe-browser-audit` and `runtime-observer` -> `exploration/captures/DISCOVERY_REPORT.md`.
2. **Behavioral Safety Net**: Run `vibe-behavioral-test-capture` to record characterization tests in `tests/characterization/`.
3. **Interactive Q&A**: Capture domain and NFR answers in `exploration/captures/architectural-qa.json`.
4. **Canonical Specs**: Invoke `vibe-togaf-architect` -> `specs/REQS.md` and `specs/domain-lexicon.json`.
5. **Domain Extraction**: Invoke `vibe-domain-extractor` to isolate framework-free models in `/domain`.
6. **Drift & Truth Verification**: Audit symbol drift and test-to-spec boundary compliance.
7. **Spec Packaging**: Invoke `vibe-spec-packager` to scaffold `/speckit/` and `/superpowers/` task packets.
8. **Certification Manifest**: Validate `exploration/certification-manifest.yaml` confirms all gates passed.
9. **Final Handoff Summary**: Compile `exploration/handoff/handoff-package.md`.
10. **Sandbox Bootstrapping**: Hand off target repository ready for implementation execution.

## Verification
- Confirm all 10 pipeline artifacts exist in their designated directory locations.
- Verify `exploration/certification-manifest.yaml` records passing statuses for all gates.
- Validate that the generated handoff package allows independent execution without legacy prototype dependencies.
