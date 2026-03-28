---
name: create-skill
description: Scaffold and optimize a new agent skill
argument-hint: "[skill-name or use-case description]"
allowed-tools: Bash, Read, Write
---

Follow the `create-skill` skill workflow to scaffold a new agent skill.

## Inputs

- `$ARGUMENTS` — optional skill name or brief use-case description passed as initial context
  to the discovery phase. Omit to start with open discovery.

## Steps

1. If `$ARGUMENTS` is provided, treat it as the starting context for skill name / purpose
2. Follow the create-skill phased workflow: discover use cases and trigger phrases, plan
   the directory structure, confirm the plan, scaffold the skill directory, write SKILL.md
   with supporting resources, then run evals and the trigger optimization loop
3. Run the skill-reviewer quality gate after generation
4. Report the created skill path and suggest next commands

## Output

Created skill directory containing `SKILL.md`, supporting `references/`, `scripts/`, `assets/`
as needed, `evals/evals.json`, with a summary of trigger phrases and eval baseline scores.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with Phase 1 discovery interview — do not skip to scaffolding
- If a skill with that name already exists: confirm before overwriting
- If the user wants to improve an existing skill, not create one: jump directly to the
  eval + iterate loop in the create-skill workflow
