# Acceptance Criteria: ADR Manager

The adr-management skill must meet the following criteria to be considered operational:

## 1. Directory Awareness and Numbering
- [ ] The agent correctly checks the target directory (default: `ADRs/` at the project root) for existing ADRs.
- [ ] The agent accurately increments the highest existing ADR numbering to assign the next chronological ID (e.g., ADR-0004 to ADR-0005).

## 2. Template Formatting
- [ ] Any generated ADR strictly follows the 5-section template (Status, Context, Decision, Consequences, Alternatives).
- [ ] Filenames use standard kebab-case formatting with a 4-digit zero-padded prefix (e.g., `0005-use-postgres.md`).

## 3. Maintenance Logic
- [ ] If instructed that a new decision supersedes an old one, the agent modifies the legacy ADR's state to "Superseded".
- [ ] The agent successfully creates the `ADRs/` directory (or custom target) if it does not already exist during its first run.
