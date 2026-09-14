# Acceptance Criteria: GitHub Issue Prioritizer

## Functional Criteria
1. **Priority Ranking Calculation**: Correctly computes P0-P3 based on friction tier, blocking status, and frequency.
2. **Projects v2 Payload**: Generates valid GraphQL mutation payload for updating single select priority field.
3. **Deterministic Output**: Label mapping produces consistent `priority:P0` through `priority:P3`.

## Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md under 80 lines routing to references.
2. **Zero Hard Failures**: Missing labels default safely to P3 without throwing unhandled exceptions.
