# Acceptance Criteria: path-reference-auditor

**Purpose**: Validate that path references in plugins and skills are resolvable and do not violate boundary constraints.

## 1. Boundary Checks
- **[PASSED]**: Skill references point only to local files within the skill folder boundary.
- **[FAILED]**: A skill reference points outside the skill folder boundary.

## 2. Resolvability
- **[PASSED]**: All `./` paths point to actual files or healthy symlinks.
- **[FAILED]**: Path reference auditor flags missing or broken references.
