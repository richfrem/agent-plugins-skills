---
name: authoring-skills
plugin: agent-extension-authoring
description: >-
  Creates, audits and improves agent skills (SKILL.md folders). Use when the user wants to scaffold a new skill (instructional, executable, or stateful), audit or align an existing skill or skill inventory against authoring standards, add a Docker runtime environment or Azure AI Foundry deployment to a skill, set up an MCP server integration (.mcp.json, stdio, sse, or http), or explore the Agent Skills specification and 64-pattern catalog. Not for whole plugins (use authoring-plugins), sub-agents (use authoring-subagents), rules, AGENTS.md or hooks (use authoring-instructions), GitHub workflows (use authoring-github-workflows) or APM packaging (use packaging-with-apm).
argument-hint: "[create|stateful|audit|docker|azure|mcp|standards] [skill-name or path]"
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Authoring Skills (`authoring-skills`)

Scaffolds skills from templates, audits them against `references/skill-authoring-contract.json`, and holds the specifications and pattern catalog the other authoring skills point to.

## Contents

- [Constraints](#constraints) • [Modes](#modes) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Self-contained**: a skill's scripts, references and assets live inside it; no plugin-root hub, symlinks or copy manifest. Other skills are referred to by name.
2. **Lean router**: `SKILL.md` is 100 lines or fewer; detail goes to `references/` linked directly from it, and long references open with a contents list.
3. **Interactive work is a skill**: multi-turn wizards and stateful flows are skills; use `authoring-subagents` only for isolated, sandboxed or adversarial roles.
4. **Gerund names**, directory name equals frontmatter `name`, third-person description that says what and when.
5. Audits are read-only; run both `--mode source` and `--mode installed` before declaring a skill compliant.
6. Model names and tiers belong to the `cli-agent` skill.

## Modes

| Mode | Use when | Entry point | Reference |
|---|---|---|---|
| `create` | New skill, instructional or executable | `scripts/scaffold.py` | [create-skill.md](references/modes/create-skill.md) |
| `stateful` | Interactive skill with persistent state | `scripts/scaffold.py` + template | [create-stateful-skill.md](references/modes/create-stateful-skill.md) |
| `audit` | Check or align one skill or an inventory | `scripts/audit_skill.py` | [audit-skill.md](references/modes/audit-skill.md) |
| `docker` | Skill with a Docker runtime | template guidance | [create-docker-skill.md](references/modes/create-docker-skill.md) |
| `azure` | Skill as an Azure AI Foundry hosted agent | `scripts/scaffold_azure_agent.py` | [create-azure-agent.md](references/modes/create-azure-agent.md) |
| `mcp` | MCP server integration | guidance only | [create-mcp-integration.md](references/modes/create-mcp-integration.md) |
| `standards` | Look up the spec, patterns and sources | reference lookup | [ecosystem-standards.md](references/modes/ecosystem-standards.md), [ecosystem-authoritative-sources.md](references/modes/ecosystem-authoritative-sources.md) |

## Quick start

```bash
python3 scripts/scaffold.py --type skill --name <name> --path plugins/<plugin>/skills --desc "<what it does. Use when ...>" [--variant executable]
python3 scripts/audit_skill.py plugins/<plugin>/skills/<name> --mode source
python3 scripts/audit_skill.py plugins/<plugin> --all --mode source --json
```

## Workflow

1. Pick the mode and read its reference before running anything.
2. Create: choose the variant and the observable success contract first, scaffold, then replace generic steps with real knowledge, commands and validation loops; add evals.
3. Audit: run the audit in both modes and fix findings as reviewed edits.
4. For decisions about structure use [pattern-decision-matrix.md](references/pattern-decision-matrix.md) and the [pattern catalog](references/patterns). On failure follow [fallback-tree.md](references/fallback-tree.md).

## Verification

```bash
python3 scripts/audit_skill.py plugins/<plugin>/skills/<name> --mode installed
```

Tests: `python3 -m pytest tests`. Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Modes: [create](references/modes/create-skill.md) • [stateful](references/modes/create-stateful-skill.md) • [audit](references/modes/audit-skill.md) • [docker](references/modes/create-docker-skill.md) • [azure](references/modes/create-azure-agent.md) • [mcp](references/modes/create-mcp-integration.md) • [standards](references/modes/ecosystem-standards.md) • [sources](references/modes/ecosystem-authoritative-sources.md)
- Authoring: [skill-authoring-guide.md](references/skill-authoring-guide.md) • [skill-authoring-contract.json](references/skill-authoring-contract.json) • [authoring-acceptance.md](references/authoring-acceptance.md) • [skill-authoring-fallback.md](references/skill-authoring-fallback.md) • [anthropic-skill-authoring-best-practices.md](references/anthropic-skill-authoring-best-practices.md) • [discovery-interview.md](references/discovery-interview.md) • [hitl-interaction-design.md](references/hitl-interaction-design.md) • [language-review.md](references/language-review.md) • [review-rubric.md](references/review-rubric.md) • [skill-evaluation-and-testing.md](references/skill-evaluation-and-testing.md) • [skill-creator-schemas.md](references/skill-creator-schemas.md) • [skills-research.md](references/skills-research.md)
- Platform: [platform-primitives.md](references/platform-primitives.md) • [plugins.md](references/plugins.md) • [workflows.md](references/workflows.md) • [tool-usage.md](references/tool-usage.md) • [npx-skills.md](references/npx-skills.md) • [github-prompts.md](references/github-prompts.md) • [index.md](references/index.md)
- MCP and Azure: [authentication.md](references/authentication.md) • [server-types.md](references/server-types.md) • [azure-foundry-agents.md](references/azure-foundry-agents.md) • [stdio-server.json](references/stdio-server.json) • [http-server.json](references/http-server.json) • [sse-server.json](references/sse-server.json)
- Patterns referenced by modes: [client-side-compute-sandbox-constraint.md](references/patterns/client-side-compute-sandbox-constraint.md) • [cyclical-state-propagation-contract.md](references/patterns/cyclical-state-propagation-contract.md) • [persistent-plugin-configuration.md](references/patterns/persistent-plugin-configuration.md)
- Templates: [skill-layout.md](assets/templates/skill-layout.md)
- Gates: [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
