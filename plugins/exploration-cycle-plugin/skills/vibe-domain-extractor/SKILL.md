---
name: vibe-domain-extractor
description: Extracts pure, framework-free, IO-free domain models and deterministic business rules from a rapid prototype with strict preservation vs replacement classification and purity audit enforcement.
---

# Domain Extraction (vibe-domain-extractor)

Extracts pure, framework-free, IO-free domain models and deterministic business rules from rapid prototypes.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Zero framework dependencies: No Express, FastAPI, Django, React, or JSX/TSX imports in `/domain`.
- Zero I/O dependencies: No raw SQL, ORM clients, network sockets, or HTTP request libraries.
- 100% deterministic: Domain calculations and invariant validations must be completely pure.

## Quick start
1. Analyze prototype code to classify core domain logic to preserve vs infrastructure to replace.
2. Scaffold clean domain hierarchy (`domain/entities/`, `domain/values/`, `domain/ports/`).
3. Extract pure entities and verify with zero-mock unit tests and static purity audits.

## Workflow
1. **Classification**: Distinguish pure business calculations (PRESERVE) from databases/APIs (REPLACE).
2. **Scaffold Directory Layout**: Establish clean domain structure without framework couplings.
3. **Model Entities & Ports**: Port logic into pure domain entities and define repository interfaces in `ports/`.
4. **Static Purity Audit**: Run `domain-purity-auditor` to verify zero banned I/O or framework imports.
5. **Unit Testing**: Write focused domain tests executing purely in-memory.

## Verification
- Run domain purity check to verify zero external I/O or framework dependencies.
- Confirm all domain unit tests pass deterministically without network or database access.
- Validate port interfaces cover all required persistence interactions.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
