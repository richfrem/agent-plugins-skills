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

# Create Sub-Agent

Scaffolds a specialized autonomous sub-agent with focused system prompt, permissions, and tool bounds.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

Reserve sub-agents for isolated execution contexts, sandboxed tool bounds, or adversarial personas.
Never create pointer-wrapper stubs that merely delegate to a procedural skill (use `create-skill`).
Declare explicit tool bounds and denial rules. Plugin agents reside as flat `.md` files in
`plugins/<plugin>/agents/<name>.md` without nested folders; project agents reside in `.claude/agents/<name>.md`.
Keep the agent definition self-contained; installed agents must not depend on source checkouts.

## Quick start

Run from this skill root with caller-supplied output paths:

```bash
# 1. Scaffold new sub-agent markdown file
python3 scripts/scaffold.py --type sub-agent --name <agent-name> --path /path/to/plugin/agents --desc "<use-case>"

# 2. Validate structural and frontmatter compliance
python3 scripts/validate_agent.py /path/to/plugin/agents/<agent-name>.md
```

## Workflow

1. **Pre-Design Gate**: Verify the task requires an autonomous persona, isolated context, or tool sandboxing.
2. **Contract & Frontmatter**: Specify `name` (3–50 chars), `model` (`inherit`, `sonnet`, `haiku`), `color`,
   tool allowances (`tools`), and description with 2–4 `<example>` few-shot blocks.
3. **System Prompt Formulation**: Author in second person ("You are..."). Structure with core responsibilities,
   process steps, quality standards, expected output format, and edge-case handling.
4. **Scaffold & Refine**: Run `scaffold.py`, then customize the prompt using [system-prompt-design.md](references/system-prompt-design.md).
5. **Evaluate**: Test at least three positive and negative triggering prompts against intended models.
6. **Publish**: Verify with `validate_agent.py` and register platform visibility per [agent-discovery-and-publication.md](references/agent-discovery-and-publication.md).

## Verification

```bash
# Validate schema, frontmatter fields, tool bounds, and system prompt structure
python3 scripts/validate_agent.py /path/to/plugin/agents/<agent-name>.md
```

Ensure validation reports zero errors before publishing. Review [acceptance criteria](references/acceptance-criteria.md).

## References

- [System prompt design](references/system-prompt-design.md): persona patterns, responsibilities, and structure.
- [Discovery and publication](references/agent-discovery-and-publication.md): multi-agent platform visibility.
- [Acceptance criteria](references/acceptance-criteria.md): structural gates, frontmatter, and triggering rules.
- [Fallback protocol](references/fallback-tree.md): resolution for invalid schemas and naming collisions.
