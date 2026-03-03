# Acceptance Criteria: conventions-agent

**Purpose**: Verify the sub-agent properly scopes itself to stylistic reviews.

## 1. Context Isolation
- **[PASSED]**: When invoked, the conventions sub-agent reviews a diff and rejects any logic that violates the core `coding-conventions` rules instead of fixing functional bugs.
- **[FAILED]**: The sub-agent rewrites the entire file or engages in architectural planning instead of strict formatting analysis.
