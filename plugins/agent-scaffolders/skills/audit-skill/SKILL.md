---
name: audit-skill
plugin: agent-scaffolders
description: Audits and aligns individual agent skills and sub-agents against ecosystem evolution standards, verifying line budgets, evals schemas, and hub-and-spoke isolation.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# audit-skill: Skill Alignment & Evolution Auditor

Audits an individual skill against the 6 ecosystem evolution invariants and 4-tier severity rubric.

## Quick Start

### 1. Audit Single Skill
```bash
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name>
```

### 2. Auto-Repair Fixable Schema Issues
```bash
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name> --fix
```

### 3. Machine-Readable JSON Output
```bash
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name> --json
```

## Progressive Disclosure & References

- **4-Tier Review Rubric**: See `references/review-rubric.md` for Blocking/High/Medium/Low criteria and context efficiency standards.
- **Acceptance Criteria**: See `references/acceptance-criteria.md` for structural invariants.
- **Fallback Protocol**: See `references/fallback-tree.md` for remediation steps.
