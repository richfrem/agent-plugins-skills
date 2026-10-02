---
name: create-sub-agent
plugin: agent-scaffolders
description: >
  Scaffolds a new autonomous sub-agent with its own prompt, system instructions, and tool permissions.
  Enforces modern architectural guidance: sub-agents are reserved for isolated execution contexts,
  strict tool sandboxing, or adversarial personas. NOT for simple procedural skills (use `create-skill`)
  and NEVER for pointer-wrapper stubs that merely delegate to a skill.
argument-hint: "[agent-name or use-case description]"
allowed-tools: Bash, Read, Write
---

# Create Sub-Agent (`create-sub-agent`)

Scaffolds a specialized autonomous sub-agent with focused system prompt, permissions, and tool bounds.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Placement](#placement)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Architectural purpose**: Reserve sub-agents for isolated execution contexts, sandboxed tool bounds, or adversarial personas.
- **No pointer wrappers**: Never create pointer-wrapper stubs that merely delegate to a skill.
- **Flat directory structure**: Plugin agents reside as flat `.md` files in `plugins/<plugin>/agents/` without nested subdirectories.
- **Explicit tool permissions**: Always declare tool bounds and denial rules (`permissions.deny`).

## Quick start

```bash
# Validate existing agent definition or scaffold new agent template
python3 scripts/validate_agent.py plugins/<plugin>/agents/<agent-name>.md
```

## Workflow

1. **Pre-Design Gate**: Verify the task requires an autonomous persona rather than a procedural skill (`create-skill`).
2. **Design Interview**: Extract intent, contract, tool allowances, model tier, and system prompt.
3. **Scaffold**: Write flat agent markdown file to `plugins/<plugin>/agents/<agent-name>.md`.
4. **Validation**: Run `validate_agent.py` to ensure schema conformance and tool constraint sanity.
5. **Publication**: Mirror to target platform (`.github/agents/` or `.claude/agents/`).

## Placement

- **Plugin Agents**: Flat `.md` file at `plugins/<plugin-name>/agents/<agent-name>.md`.
- **Project Agents**: Flat `.md` file at `.claude/agents/<agent-name>.md`.

## Verification

```bash
# Run structural validator on the agent definition
python3 scripts/validate_agent.py plugins/<plugin>/agents/<agent-name>.md
```

## References

- [agent-discovery-and-publication.md](references/agent-discovery-and-publication.md) — Multi-agent platform visibility.
- [system-prompt-design.md](references/system-prompt-design.md) — Persona crafting and constraints.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and structural requirements.
- [fallback-tree.md](references/fallback-tree.md) — Escalation protocol for sub-agent authoring.
