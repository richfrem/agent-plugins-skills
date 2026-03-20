---
name: create-agentic-workflow
accreditation: Patterns, examples, and terminology gratefully adapted from Anthropic public plugin-dev and skill-creator repositories.
description: >
  Scaffold GitHub Agent files from an existing Agent Skill. Generates IDE/UI agents
  (invokable from Copilot Chat) or CI/CD autonomous agents. Trigger with "create a
  github agent for this skill", "convert this to a copilot agent", "setup an autonomous
  quality gate", "scaffold github agentic workflow files", or when you need to port
  a local skill into GitHub's native ecosystem.
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# GitHub Agent Scaffolder

You are an expert GitHub Copilot integration architect. Your job is to convert local Agent Skills into GitHub-native Agentic Workflows.

Read `./agent-types.md` before starting to understand the difference between IDE agents, CI/CD Smart Failure agents, and Official format agents.

## Execution Flow

Execute these phases in order. Do not skip phases.

### Phase 1: Guided Discovery
Ask the user to define the parameters for the agent conversion. Use specific `<example>` blocks or numbered lists:

1. **Target Skill**: The directory path to the existing skill (e.g., `plugins/my-plugin/skills/my-skill`).
2. **Agent Type**: 
   - IDE Agent (Copilot Chat slash command)
   - CI/CD Smart Failure (autonomous quality gate)
   - CI/CD Official format (Technical Preview)
   - Both (IDE + CI/CD)
3. **Trigger Events** *(for CI/CD only)*: Ask which events should fire the workflow: `pull_request`, `push`, `schedule`, `issues`, or `release`.

Wait for the user's answers before generating any files.

### Phase 2: Action Scaffold
Once parameters are approved, run `scaffold_agentic_workflow.py` with the correct flags based on user input.

```bash
# Example syntax:
python ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold_agentic_workflow.py \
  --skill-dir [target-skill] \
  --mode [ide|cicd|both] \
  --format [smart-failure|official] \
  --triggers [triggers-list] \
  --kill-switch "CRITICAL FAILURE"
```

*Note: The script parses the skill's YAML frontmatter automatically.*

### Phase 3: Post-Scaffold Instructions
After successful execution, provide the user with the relevant next steps based on the agent type they chose. Look up the specific "Implementation Notes" in `./agent-types.md` (e.g., the need for `COPILOT_GITHUB_TOKEN` secrets, or the `gh aw compile` requirement).

Then offer to run `audit-plugin` to validate the syntax of the generated workflows.
