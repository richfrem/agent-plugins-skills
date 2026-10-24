> Retired skill `create-sub-agent`, kept as the **create-sub-agent** mode of `authoring-subagents`. Body unchanged apart from link targets, the scaffolder command and the model-field wording. Frontmatter removed.
>
> Original description: Scaffolds a new autonomous sub-agent with its own prompt, system instructions, and tool permissions. Enforces modern architectural guidance: sub-agents are reserved for isolated execution contexts, strict tool sandboxing, or adversarial personas. NOT for simple procedural skills (use `authoring-skills`) and NEVER for pointer-wrapper stubs that merely delegate to a skill.

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
Never create pointer-wrapper stubs that merely delegate to a procedural skill (use `authoring-skills`).
Declare explicit tool bounds and denial rules. Plugin agents reside as flat `.md` files in
`plugins/<plugin>/agents/<name>.md` without nested folders; project agents reside in `.claude/agents/<name>.md`.
Keep the agent definition self-contained; installed agents must not depend on source checkouts.

## Quick start

Run from this skill root with caller-supplied output paths:

```bash
# 1. Scaffold new sub-agent markdown file
python3 scripts/scaffold_subagent.py --name <agent-name> --path /path/to/plugin/agents --desc "<use-case>"

# 2. Validate structural and frontmatter compliance
python3 scripts/validate_agent.py /path/to/plugin/agents/<agent-name>.md
```

## Workflow

1. **Pre-Design Gate**: Run the 5-question diagnostic interview in [skills-vs-agents-decision-framework.md](../skills-vs-agents-decision-framework.md). Verify the task genuinely requires context isolation, sandboxed tool restrictions, or an independent/adversarial review stance. If the capability requires interactive back-and-forth (`AskUserQuestion`) or is a procedural workflow, author it as a skill instead.
2. **Contract & Frontmatter**: Specify `name` (3–50 chars), `model` (optional, default `inherit`; model names and tiers are owned by the `cli-agent` skill), `color`,
   tool allowances (`tools`), and description with 2–4 `<example>` few-shot blocks. Optional: preload shared skills via `skills:`.
3. **System Prompt Formulation**: Author in second person ("You are..."). Structure with core responsibilities,
   process steps, quality standards, expected output format, and edge-case handling.
4. **Scaffold & Refine**: Run `scaffold_subagent.py`, then customize the prompt using [system-prompt-design.md](../system-prompt-design.md).
5. **Evaluate**: Test at least three positive and negative triggering prompts against intended models.
6. **Publish**: Verify with `validate_agent.py` and register platform visibility per [agent-discovery-and-publication.md](../agent-discovery-and-publication.md).

## Verification

```bash
python3 scripts/validate_agent.py plugins/<plugin>/agents/<agent-name>.md
python3 scripts/audit_sub_agent.py plugins/<plugin>/agents/<agent-name>.md --strict
```

Ensure validation reports zero errors before publishing. Review [acceptance criteria](../acceptance-criteria.md).

## References

- [skills-vs-agents-decision-framework.md](../skills-vs-agents-decision-framework.md) — The 5-question diagnostic decision tree, tool sandboxing vs. pre-approval, and Anthropic refinements.
- [system-prompt-design.md](../system-prompt-design.md) — System prompt structure, second-person persona formulation, and boundary enforcement.
- [agent-discovery-and-publication.md](../agent-discovery-and-publication.md) — Trigger configuration, platform visibility, and manifest registration.
- [sub-agents-spec.md](../sub-agents-spec.md) — Complete sub-agent schema specification.
- [acceptance-criteria.md](../acceptance-criteria.md) — Structural gates, frontmatter, and triggering rules.
- [fallback-tree.md](../fallback-tree.md) — Resolution for invalid schemas and naming collisions.
