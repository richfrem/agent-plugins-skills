# Acceptance Criteria: create-skill

**Purpose**: Verify the system generates Microsoft-compliant Skill architectures.

## 1. Directory Structure
- **[PASSED]**: Skill generates `scripts/`, `references/`, and `assets/` folders. It places an `acceptance-criteria.md` inside `references/`.
- **[FAILED]**: Skill fails to create subdirectories, leaving a massive root `SKILL.md` vulnerable to bloating.

## 2. Shell Enforcement
- **[PASSED]**: Skill uses `.py` Python scripts inside the `scripts/` folder.
- **[FAILED]**: Skill generates legacy bash `.sh` execution scripts.
