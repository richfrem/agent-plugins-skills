# Acceptance Criteria: managing-github-issues

## `log` mode
### Functional Criteria
1. **Dry-Run by Default**: All issue operations default to payload generation (`execute=False`).
2. **Secret Redaction**: Any payload containing tokens, API keys, or private keys fails validation.
3. **Taxonomy Enforcement**: Requires valid `type`, `tier`, `source`, `risk`, and `location` labels.
4. **Body Structure**: Enforces mandatory headers (`Summary`, `Observed Behavior`, `Expected Behavior`, `Evidence`, `Impact`).

### Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md under 80 lines routing to references.
2. **Deterministic CLI**: Clear JSON output and predictable exit codes on failure.

## `backlog` mode
### Functional Criteria
1. **Payload Generation**: Without `--execute`, outputs preview JSON of the issue title, body, and labels.
2. **Taxonomy Conformance**: Verifies labels match taxonomy rules before attempting live execution.
3. **Task Parsing**: Accurately parses task markdown files and maps sections to GitHub issue format.
4. **Safety Scans**: Blocks files containing unredacted credentials or secrets.

### Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md under 80 lines routing to references.
2. **Clear Error Reporting**: Reports missing files or validation failures with clear messages and non-zero exit codes.

## `prioritize` mode
### Functional Criteria
1. **Priority Ranking Calculation**: Correctly computes P0-P3 based on friction tier, blocking status, and frequency.
2. **Projects v2 Payload**: Generates valid GraphQL mutation payload for updating single select priority field.
3. **Deterministic Output**: Label mapping produces consistent `priority:P0` through `priority:P3`.

### Non-Functional Criteria
1. **Progressive Disclosure**: SKILL.md under 80 lines routing to references.
2. **Zero Hard Failures**: Missing labels default safely to P3 without throwing unhandled exceptions.

## `propose-refactor` mode
### ✅ Scenarios that must trigger
- "Synthesize a refactoring proposal from the friction hotspots."
- "What's the systemic fix for this recurring friction cluster?"
- "We keep hitting the same bug pattern — propose a real fix, not a patch."

### ❌ Scenarios that must NOT trigger
- "Open a PR for this fix." (requires human confirmation first, then `issue-pr-lifecycle-agent`)
- "Just patch this one line." (Tier 0 inline fix, not a systemic proposal)
- "Prioritize the github issue backlog." (use the `prioritize` mode)

## `review-resolution` mode
### ✅ Scenarios that must trigger
- "Audit the issues we closed last week for resolution quality."
- "Was this issue actually fixed or did it just get relabeled?"
- "Review issue resolution quality for the resolution:fixed label."

### ❌ Scenarios that must NOT trigger
- "Close this issue." (use the `log` mode)
- "File a new github issue for this bug." (use the `log` mode)
- "Prioritize the open issue backlog." (use the `prioritize` mode)
