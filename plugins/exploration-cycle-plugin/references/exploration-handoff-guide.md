# Exploration Handoff Guide & Output Formats

Deep reference for `exploration-handoff` covering stage details, TierGate risk assessment, reader testing, and output format templates.

## Contents

- [Stage 0: Scribe Activities](#stage-0-scribe-activities)
- [Stage 1.5: Risk & Rigor Assessment (TierGate)](#stage-15-risk--rigor-assessment-tiergate)
- [Stage 3: Reader Testing & Validation](#stage-3-reader-testing--validation)
- [Stage 4: Delivery Path Formats](#stage-4-delivery-path-formats)
  - [Tier 1: Low-Risk Deployment Brief](#tier-1-low-risk-deployment-brief)
  - [Tier 2: Moderate-Risk Security Review](#tier-2-moderate-risk-security-review)
  - [Tier 3: Formal SDLC Engineering Package](#tier-3-formal-sdlc-engineering-package)
  - [Legacy Analysis Format](#legacy-analysis-format)
  - [Process Change Recommendation](#process-change-recommendation)
  - [Strategic Recommendation](#strategic-recommendation)
- [Anti-Hallucination & Traceability Rules](#anti-hallucination--traceability-rules)

---

## Stage 0: Scribe Activities

Before synthesis, run automated captures based on session type:
- **Software sessions (Phase 3 ran)**:
  1. `business-requirements-capture` → `exploration/captures/business-requirements.md`
  2. `user-story-capture` → `exploration/captures/user-stories.md`
  3. `business-workflow-doc` (if process flows present) → `exploration/captures/workflow-diagram.md`
- **Non-software sessions**: Skip prototype captures. Capture problem-framing, BRD draft, or workflow diagram if missing.

---

## Stage 1.5: Risk & Rigor Assessment (TierGate)

| # | Question | Logic & Routing |
|---|----------|-----------------|
| 1 | Personal or sensitive data? (PII, health, financial) | Yes → Tier 2 minimum |
| 2 | Public-facing or outside immediate team? | Yes → Tier 2 minimum |
| 3 | Access to production / high-privilege systems? | Yes + Q1/Q2 → Tier 3 |
| 4 | Financial transactions or regulatory compliance? | Yes + Q1/Q2 → Tier 3 |
| 5 | Decisions about people (hiring, eligibility, bias)? | Yes → Tier 2 + Ethics Review |

### Tier Actions:
- **Tier 1 (Low Risk)**: Direct deployment, lightweight self-assessment.
- **Tier 2 (Moderate Risk)**: Security / ethics review required before deployment.
- **Tier 3 (High Risk)**: Formal engineering SDLC cycle required.
- **Throwaway**: Idea not viable; capture learnings and close.

---

## Stage 3: Reader Testing & Validation

Predict 3 blocker questions specific to the downstream consumer:
- **Engineering**: Data model, edge cases, acceptance criteria.
- **Executive**: Cost to build vs delay, risk mitigations.
- **Operations**: Process ownership, escalation paths.
- **Security**: Data storage boundaries, auth mechanisms.

---

## Stage 4: Delivery Path Formats

### Tier 1: Low-Risk Deployment Brief
- Overview of what was built
- Deployment / execution instructions
- Monitoring guide for first week
- Self-assessment checklist

### Tier 2: Moderate-Risk Security Review
- Data flow diagram & touched assets
- Authentication and authorization patterns
- Known risks and active mitigations
- Red team questions checklist

### Tier 3: Formal SDLC Engineering Package
1. Executive Summary
2. Business Context
3. User Stories (with acceptance criteria)
4. Business Rules
5. Process Flows
6. Functional Requirements
7. Non-Functional Requirements
8. Constraints & Limits
9. Prototype Notes & Validations
10. Risk Assessment (TierGate block)
11. Open Questions / Ambiguity Markers
12. Out of Scope

### Legacy Analysis Format
1. System Overview & Architecture
2. Preserved Capabilities
3. Known Pain Points & Technical Debt
4. Integration Map
5. Data Volume & Sensitivity
6. Modernisation Options Evaluated
7. Recommended Path & Timeline
8. Open Architecture Questions

### Process Change Recommendation
1. Problem Summary & Impact
2. Root Cause Analysis
3. Proposed Process Recommendation
4. Step-by-Step Implementation Map
5. Success Metrics
6. Risks & Change Management
7. Supporting Software Needs

### Strategic Recommendation
1. Strategic Question Explored
2. Context & Timing Triggers
3. Confirmed Facts & Empirical Evidence
4. Unresolved Uncertainties
5. Alternatives & Tradeoffs
6. Preferred Path with Rationale
7. Implementation Milestones

---

## Anti-Hallucination & Traceability Rules

- Do NOT invent requirements or rules not present in input sources.
- Trace major constraints back to their specific source capture.
- Differentiate confirmed decisions from optimistic assumptions.
