# Acceptance Criteria: GitHub Issue Agent

## Functional Criteria
1. **Dry-Run by Default**: All issue operations default to payload generation (`execute=False`).
2. **Secret Redaction**: Any payload containing tokens, API keys, or private keys fails validation.
3. **Taxonomy Enforcement**: Requires valid `type`, `tier`, `source`, `risk`, and `location` labels.
4. **Body Structure**: Enforces mandatory headers (`Summary`, `Observed Behavior`, `Expected Behavior`, `Evidence`, `Impact`).

## Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md under 80 lines routing to references.
2. **Deterministic CLI**: Clear JSON output and predictable exit codes on failure.
