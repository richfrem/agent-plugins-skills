---
name: vibe-reengineer
description: Orchestrates the 7-step surgical vibe-to-enterprise reengineering pipeline with automated safety scoring and economic controls. Coordinates preservation, stabilization, modularization, and replatforming.
---

# Vibe Reengineering Loop (vibe-reengineer)

Coordinates the 7-step surgical vibe-to-enterprise reengineering pipeline with automated safety scoring and economic controls.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Canonical truth hierarchy: `specs/REQS.md` > `tests/characterization/` > `/domain` > Specs > Prototype Code.
- Characterization tests cannot override quantitative invariants in `REQS.md`.
- Autonomous rewrites of auth, payments, cryptography, and compliance logging are strictly forbidden.

## Quick start
1. Score module migration risk (5–25) across coupling, side-effects, hidden state, test coverage, dynamism.
2. Select reengineering mode: Preservation (A), Stabilization (B), Modularization (C), Replatform (D), or Domain Extraction (E).
3. Execute the 7-step pipeline from discovery through characterization to certified slice migration.

## Workflow
1. **Discovery & Telemetry**: Run `vibe-browser-audit` and `runtime-observer`.
2. **Behavioral Safety Net**: Capture characterization tests via `vibe-behavioral-test-capture`.
3. **Requirements Consolidation**: Author `specs/REQS.md` and define domain glossary.
4. **Domain Core Extraction**: Extract framework-free models via `vibe-domain-extractor` into `/domain`.
5. **Architectural Scaffolding**: Generate ADRs and architecture blueprints via `vibe-spec-packager`.
6. **Slice Migration**: Incrementally port routes via `vibe-slice-migrator` verified by `certification-verifier`.
7. **Final Safety Net**: Execute complete test suite ensuring 100% parity against original characterization tests.

## Verification
- Confirm all characterization tests pass with 100% behavioral parity.
- Verify domain purity audits report zero banned imports in `/domain`.
- Ensure no forbidden rewrite modules were altered autonomously without human sign-off.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
- [cheapest_models.md](references/cheapest_models.md)
- [vibe-reengineer-guide.md](references/vibe-reengineer-guide.md)
