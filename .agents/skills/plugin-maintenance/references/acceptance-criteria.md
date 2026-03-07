# Acceptance Criteria: Plugin Maintenance

The plugin-maintenance skill must meet the following criteria to be considered operational:

## 1. Discovery Gate
- [ ] The agent NEVER executes any script without first asking which operation the user wants (Audit / Sync / README).
- [ ] The agent presents a Recap-Before-Execute summary listing the operation, target, and expected impact before generating any commands.

## 2. Audit Operation
- [ ] The agent correctly classifies all 8 file types (SKILL.md, commands, references, scripts, README, CONNECTORS.md, plugin.json, diagrams).
- [ ] The agent evaluates all 7 structural dimensions and produces a checklist output with severity labels (CRITICAL / HIGH / MEDIUM / LOW).
- [ ] If `audit_structure.py` is unavailable, the agent performs the manual audit using the checklist in SKILL.md without skipping.

## 3. Sync Operation
- [ ] The agent proposes a `--dry-run` pass before any live sync.
- [ ] The agent NEVER deletes project-specific (non-vendor) plugins during a sync.
- [ ] If the vendor inventory is missing, the agent halts and reports rather than guessing which plugins to delete.

## 4. Escalation Discipline
- [ ] The agent correctly identifies and reports all CRITICAL findings before any others.
- [ ] The agent halts with a clear explanation on encountering `shell=True`, hardcoded credentials, or accidental deletion of a custom plugin.
