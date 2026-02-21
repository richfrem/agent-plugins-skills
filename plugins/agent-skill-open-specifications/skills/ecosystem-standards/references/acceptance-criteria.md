# Acceptance Criteria: ecosystem-standards

**Purpose**: Ensure the active auditing logic detects legacy layout structures against the Anthropic/Microsoft plugin standards.

## 1. Error Emitting
- **[PASSED]**: The ecosystem auditor outputs distinct error codes enabling programmatic CI/CD blocking when plugins violate the 500-line skill rule or miss `.claude-plugin/plugin.json`.
- **[FAILED]**: The standard review script crashes or fails to recursively check all local directories.
