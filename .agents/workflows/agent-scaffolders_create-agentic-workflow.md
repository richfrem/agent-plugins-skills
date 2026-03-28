---
name: create-agentic-workflow
description: Scaffold a GitHub agentic workflow from an existing skill
argument-hint: "[skill-dir] [mode: ide|cicd|both]"
allowed-tools: Bash, Read, Write
---

Follow the `create-agentic-workflow` skill workflow to convert a local skill into a
GitHub-native agentic workflow.

## Inputs

- `$1` — path to the existing skill directory to convert
- `$2` — optional mode: `ide` (Copilot Chat slash command), `cicd` (autonomous quality gate),
  or `both`. Defaults to guided selection if omitted.

## Steps

1. Run the Phase 0 complexity gate — confirm the task warrants agent complexity
2. If `$1` provides a skill directory, resolve and validate the path; otherwise ask
3. Follow the create-agentic-workflow discovery phase: select workflow pattern
   (Sequential / Orchestrator-Workers / Evaluator-Optimizer / Stateful), agent type,
   trigger events for CI/CD, and orchestration design for parallel patterns
4. Run `scaffold_agentic_workflow.py` with the gathered parameters
5. Provide post-scaffold next steps (secrets, `gh aw compile`, etc.)

## Output

Generated GitHub workflow YAML and/or Copilot agent definition files, with implementation
notes for the chosen agent type and pattern.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with Phase 0 complexity gate, then guided discovery
- If the skill directory does not exist: ask for the correct path
- If the task is better served by a simple command: recommend it and stop (Phase 0 gate)
- Subagents in Orchestrator-Workers do not inherit parent permissions — remind user to
  configure each worker's permissions or use a PermissionRequest hook
