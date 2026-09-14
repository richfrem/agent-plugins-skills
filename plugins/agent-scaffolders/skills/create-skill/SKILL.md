---
name: create-skill
plugin: agent-scaffolders
description: >
  Creates a new skill in an existing plugin. Skills are the universal capability primitive
  across modern AI platforms (callable as slash commands, agent skills, and prompt tools).
allowed-tools: Bash, Read, Write
---

# create-skill: Skill Scaffolding Executor

Scaffolds a complete, standards-compliant agent skill directory adhering to progressive disclosure and ADR-002/003.

## Scaffolding Workflow

### 1. Discovery Interview
Gather the skill name, purpose, target plugin, and trigger criteria:
- See `references/discovery-interview.md` for the interview questionnaire and slug validation rules.

### 2. Scaffold Skill Directory
Create the standard directory layout:
```bash
# Verify plugin root scripts and symlink shared utilities
python3 .agents/skills/symlink-manager/scripts/symlink_manager.py create \
  --src plugins/<plugin>/references/acceptance-criteria.md \
  --dst plugins/<plugin>/skills/<skill-name>/references/acceptance-criteria.md
```

### 3. Verify Alignment Gate
Audit the scaffolded skill against the 6 ecosystem invariants:
```bash
python3 plugins/agent-scaffolders/scripts/audit_skill.py plugins/<plugin>/skills/<skill-name>
```

## Progressive Disclosure & References

- **Interview Protocol**: See `references/discovery-interview.md` for phase-by-phase requirements.
- **Platform Architecture**: See `references/platform-primitives.md` for slash commands and tool primitives.
- **Acceptance Criteria**: See `references/acceptance-criteria.md` for structural quality gates.
