> Retired skill `ecosystem-authoritative-sources`, kept as the **ecosystem-authoritative-sources** mode of `authoring-skills`. Body unchanged apart from link targets, retired-skill names (now the new skills) and the corrected commands. Frontmatter removed.
>
> Original description: Provides information about how to create, structure, install, and audit Agent Skills, Plugins, Antigravity Workflows, and Sub-agents. Trigger this when specifications, rules, or best practices for the ecosystem are required.

# Ecosystem Authoritative Sources (`ecosystem-authoritative-sources`)

Official standards, structural specifications, and reference library for agent skills, plugins, and workflows.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Self-contained**: scripts and references live inside the skill that uses them; no plugin-root hub, no symlinks, no copy manifest.
- **Progressive disclosure**: `SKILL.md` stays lean (<80 lines target); deep specs live in `references/`.
- **Constitutional precedence**: Repository root instructions (`AGENTS.md`) take precedence over local references.

## Quick start

```bash
# Query the canonical skill authoring contract
cat plugins/agent-extension-authoring/references/skill-authoring-contract.json | head -n 30
```

## Workflow

1. **Locate Standard**: Identify the target primitive (plugin, skill, hook, agent, rule).
2. **Review Specifications**: Consult corresponding reference documents in `references/`.
3. **Verify Compliance**: Apply canonical templates and constraints to new or modified primitives.
4. **Audit**: Run `authoring-plugins` or `audit-skill` to verify compliance with ecosystem standards.

## Verification

```bash
# Verify references directory index integrity
ls -la plugins/agent-extension-authoring/references/
# Check that contract json conforms to schema
python3 -c "import json; json.load(open('plugins/agent-extension-authoring/references/skill-authoring-contract.json'))"
```

## References

- [skills-research.md](../skills-research.md) — Skill architecture and progressive disclosure.
- [plugins.md](../plugins.md) — Plugin specification and layout standards.
- [workflows.md](../workflows.md) — Deterministic multi-step execution workflows.
- Sub-agent configuration and invocation boundaries: the `authoring-subagents` skill (its sub-agents-spec reference).
- Event-driven lifecycle hooks: the `authoring-instructions` skill (its hooks-spec reference).
- [acceptance-criteria.md](../acceptance-criteria.md) — Ecosystem authoritative sources acceptance criteria.
- [fallback-tree.md](../fallback-tree.md) — Fallback resolution for missing or conflicting specifications.
