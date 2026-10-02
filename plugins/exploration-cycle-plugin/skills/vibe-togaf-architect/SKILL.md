---
name: vibe-togaf-architect
description: Synthesizes visual discovery findings and interactive Q&A responses into comprehensive C4 and TOGAF architecture specifications with strict tier gate enforcement.
---

# TOGAF-Style System Architecture Definition (vibe-togaf-architect)

Synthesizes visual discovery findings and interactive Q&A responses into formal C4 blueprints and TOGAF-style architecture specifications.

## Contents
- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints
- Enforce the Tier Gate: Never scaffold target sandboxes or downstream packages without explicit user approval of specifications.
- Meticulously separate core logic to salvage (Preservation Gems) from technical debt to remediate.
- All Mermaid diagrams must be strictly valid without syntax errors.

## Quick start
1. Read discovery report at `exploration/captures/DISCOVERY_REPORT.md` and NFR interview responses.
2. Scaffold formal architecture specifications under `/specs`.
3. Halt at the Tier Gate and present architecture specifications for explicit user sign-off.

## Workflow
1. **Input Analysis**: Ingest discovery reports and NFR interview responses; identify user personas, system boundaries, and external APIs.
2. **Requirements Definition**: Author `specs/REQUIREMENTS.md` documenting salvaged business rules, debt remediation, and SLA targets.
3. **C4 Modeling**: Generate system context and component diagrams in `specs/SYSTEM_CONTEXT.md` and `specs/SEQUENCE_DIAGRAMS.md`.
4. **Technology Mapping**: Author `specs/TECH_MAPPING.md` mapping prototype components to enterprise technologies.
5. **Deployment Specification**: Document topology, containerization, and reverse-proxy setup in `specs/DEPLOYMENT.md`.
6. **Tier Gate Review**: Present complete `/specs` package for human review and approval.

## Verification
- Confirm all five specification files exist in `/specs` and contain required sections.
- Verify Mermaid sequence and C4 context diagrams parse cleanly without syntax issues.
- Ensure explicit human sign-off is logged before downstream execution begins.

## References
- [acceptance-criteria.md](references/acceptance-criteria.md)
