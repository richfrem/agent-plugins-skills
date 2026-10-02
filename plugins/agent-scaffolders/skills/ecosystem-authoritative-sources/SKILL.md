---
name: ecosystem-authoritative-sources
plugin: agent-scaffolders
description: Provides information about how to create, structure, install, and audit Agent Skills, Plugins, Antigravity Workflows, and Sub-agents. Trigger this when specifications, rules, or best practices for the ecosystem are required.
allowed-tools: Bash, Read, Write
---

# Ecosystem Authoritative Sources (`ecosystem-authoritative-sources`)

Official standards, structural specifications, and reference library for agent skills, plugins, and workflows.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Hub-first**: Shared scripts and references belong in plugin root hub, symlinked into skills.
- **File-level symlinks only**: Directory symlinks violate repository policy.
- **Progressive disclosure**: `SKILL.md` stays lean (<80 lines target); deep specs live in `references/`.
- **Constitutional precedence**: Repository root instructions (`AGENTS.md`) take precedence over local references.

## Quick start

```bash
# Query the canonical skill authoring contract
cat plugins/agent-scaffolders/references/skill-authoring-contract.json | head -n 30
```

## Workflow

1. **Locate Standard**: Identify the target primitive (plugin, skill, hook, agent, rule).
2. **Review Specifications**: Consult corresponding reference documents in `references/`.
3. **Verify Compliance**: Apply canonical templates and constraints to new or modified primitives.
4. **Audit**: Run `audit-plugin` or `audit-skill` to verify compliance with ecosystem standards.

## Verification

```bash
# Verify references directory index integrity
ls -la plugins/agent-scaffolders/references/
# Check that contract json conforms to schema
python3 -c "import json; json.load(open('plugins/agent-scaffolders/references/skill-authoring-contract.json'))"
```

## References

- [skills-research.md](references/skills-research.md) — Skill architecture and progressive disclosure.
- [plugins.md](references/plugins.md) — Plugin specification and layout standards.
- [workflows.md](references/workflows.md) — Deterministic multi-step execution workflows.
- [sub-agents.md](references/sub-agents.md) — Sub-agent configuration and invocation boundaries.
- [hooks.md](references/hooks.md) — Event-driven lifecycle hooks.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Ecosystem authoritative sources acceptance criteria.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution for missing or conflicting specifications.
