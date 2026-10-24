---
name: authoring-subagents
plugin: agent-extension-authoring
description: >-
  Creates and audits sub-agent definitions (agents/*.md): focused system prompt, frontmatter, tool sandbox and trigger examples. Use when the user wants to write, check or fix a sub-agent that needs an isolated context, strict tool bounds or an adversarial persona (reviewer, auditor, red team). Not for interactive or multi-turn wizards (those are skills, use authoring-skills), simple procedures, or pointer stubs that only delegate to a skill.
argument-hint: "[create|audit] [agent-name or path]"
allowed-tools: Bash, Read, Write
---

# Authoring Sub-Agents (`authoring-subagents`)

Scaffolds sub-agent files and audits them against the authoring contract. Sub-agents are the exception, not the default.

## Contents

- [Constraints](#constraints) • [Modes](#modes) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Three reasons justify a sub-agent**: context isolation, sandboxed tool restrictions, or independent/adversarial review; persona alone is never sufficient justification ([skills-vs-agents-decision-framework.md](references/skills-vs-agents-decision-framework.md)). Interactive facilitators and procedures belong in skills in the main thread.
2. **No pointer wrappers**: an agent that merely says "please run skill X" must not exist; however, a subagent that controls its own prompt and tool bounds may preload skills via `skills:`.
3. **Explicit tool bounds** and denial rules; the definition is self-contained and never depends on a source checkout.
4. **Model choices are not made here**: the `model` field defaults to `inherit`; model names and tiers belong to the `cli-agent` skill.
5. Plugin agents are flat files at `plugins/<plugin>/agents/<name>.md`; project agents live in `.claude/agents/<name>.md`.
6. Audits are read-only.

## Modes

| Mode | Use when | Entry point | Reference |
|---|---|---|---|
| `create` | New sub-agent | `scripts/scaffold_subagent.py`, then `scripts/validate_agent.py` | [create-sub-agent.md](references/modes/create-sub-agent.md) |
| `audit` | Check one agent or a whole plugin | `scripts/audit_sub_agent.py` | [audit-sub-agent.md](references/modes/audit-sub-agent.md) |

## Quick start

```bash
python3 scripts/scaffold_subagent.py --name <agent-name> --path plugins/<plugin>/agents --desc "<use-case>"
python3 scripts/validate_agent.py plugins/<plugin>/agents/<agent-name>.md
python3 scripts/audit_sub_agent.py plugins/<plugin> --all --json
```

## Workflow

1. Run the pre-design gate: does one of the three reasons apply? If not, create a skill instead.
2. Scaffold, then write the system prompt in second person using [system-prompt-design.md](references/system-prompt-design.md); add 2-4 `<example>` trigger blocks.
3. Validate and audit until zero errors; test at least three positive and three negative trigger prompts.
4. Publish per [agent-discovery-and-publication.md](references/agent-discovery-and-publication.md). On failure follow [fallback-tree.md](references/fallback-tree.md).

## Verification

```bash
python3 scripts/audit_sub_agent.py plugins/<plugin>/agents/<agent-name>.md --strict
```

Tests: `python3 -m pytest tests`. Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Modes: [create-sub-agent.md](references/modes/create-sub-agent.md) • [audit-sub-agent.md](references/modes/audit-sub-agent.md)
- Detail: [skills-vs-agents-decision-framework.md](references/skills-vs-agents-decision-framework.md) • [system-prompt-design.md](references/system-prompt-design.md) • [agent-discovery-and-publication.md](references/agent-discovery-and-publication.md) • [agent-creation-prompt.md](references/agent-creation-prompt.md) • [complete-agent-examples.md](references/complete-agent-examples.md) • [sub-agents-spec.md](references/sub-agents-spec.md)
- Gates: [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
- Template: [agent.md.jinja](assets/templates/agent.md.jinja)
