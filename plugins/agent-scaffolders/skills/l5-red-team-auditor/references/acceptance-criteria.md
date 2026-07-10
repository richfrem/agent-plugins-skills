# Acceptance Criteria: l5-red-team-auditor

**Purpose**: Assess agent plugins against the 39-point L5 Enterprise architectural maturity matrix to find compliance gaps.

## 1. Compliance Audit
- **[PASSED]**: Gaps, bypass vectors, and violations of pattern decisions are accurately identified and scored.
- **[FAILED]**: Findings are softened, or required Foundational Rubrics (such as pattern matrix) are not checked.

## 2. Escalation & Verification
- **[PASSED]**: Critically unsafe patterns (like `shell=True` or hardcoded tokens) immediately trigger a stop and escalation.
- **[FAILED]**: CRITICAL violations are ignored or skipped during synthesis.
