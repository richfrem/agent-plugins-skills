# Acceptance Criteria: coding-conventions

**Purpose**: Verifies the enforcement of universal coding standards using Progressive Disclosure references.

## 1. Documentation Indexing
- **[PASSED]**: The agent successfully reads the installed `coding-conventions` rule (`.agent/rules/coding-conventions.md`) to determine the correct sub-domain standard (React, Python, etc) needed for its current task without loading everything.
- **[FAILED]**: The agent guesses syntax styles or attempts to load the entire conventions library into context at once.
