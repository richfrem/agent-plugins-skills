---
name: vibe-slice-migrator
description: Progressively migrates legacy prototype routes and features to a clean architecture layer slice-by-slice, verifying them against characterization tests, running purity/drift checks, and executing completion certifications.
---

# Vertical Slice Migration (vibe-slice-migrator)

Progressively migrates legacy prototype routes and features to a clean architecture layer slice-by-slice.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Enforce strict inward dependency directions: Infrastructure -> Application -> Domain.
- Absolute safety pre-check: If slice touches Auth, Billing, Crypto, or Compliance, halt immediately.
- 100% characterization test pass rate required before deprecating any legacy code path.

## Quick start
1. Target discrete route or feature slice and calculate migration risk score.
2. Port business rules to `/domain` and use-case orchestrators to `/application`.
3. Verify with characterization suite and delegate certification to `certification-verifier`.

## Workflow
1. **Isolate Boundary**: Scope a single vertical slice and conduct safety pre-checks.
2. **Implement Core**: Move pure entities into `/domain` and application use-cases into `/application`.
3. **Infrastructure Adapters**: Implement repository and network adapters satisfying domain port interfaces.
4. **Governance Audits**: Verify domain purity (zero framework imports) and check semantic drift against `specs/REQS.md`.
5. **Safety Tests**: Run characterization suite to prove zero behavioral regressions.
6. **Deprecate & Certify**: Mark slice certified and safely retire legacy route.

## Verification
- Confirm 100% of characterization tests pass for the migrated slice.
- Validate domain purity score is 100% with zero third-party I/O imports.
- Ensure all business invariants from `specs/REQS.md` remain satisfied.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
- [architecture-rules.md](references/architecture-rules.md)
