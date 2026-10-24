---
name: authoring-github-workflows
plugin: agent-extension-authoring
description: >-
  Scaffolds GitHub automation files. Use when the user wants a deterministic GitHub Actions CI/CD workflow (test, build, lint, deploy, release, security), or wants to turn an existing skill into a Copilot custom agent, a GitHub Agentic Workflow (gh-aw), or a CI/CD smart-failure agent. Not for local event-driven hooks (use the hooks reference in authoring-instructions) or for packaging with APM (use packaging-with-apm).
argument-hint: "[action|agent] [category or skill-dir]"
allowed-tools: Bash, Read, Write
---

# Authoring GitHub Workflows (`authoring-github-workflows`)

Generates `.github/workflows/*.yml` CI/CD workflows and GitHub-native agent configurations (`.github/agents/*.agent.md`, gh-aw workflows) without hand-editing generated frontmatter.

## Contents

- [Constraints](#constraints) • [Modes](#modes) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Deterministic vs agentic**: a plain Action has no runtime LLM; anything prompt-driven is an agent or gh-aw workflow.
2. **Least privilege**: every workflow sets an explicit minimal `permissions:` block and `timeout-minutes`; pin third-party actions to a major version or SHA.
3. **Secrets** only via `${{ secrets.NAME }}`; never hardcode or log them.
4. **Generated frontmatter is never hand-edited**: run `scaffold_github_agent.py`; the gh-aw `.lock.yml` comes only from `gh aw compile`.
5. **Kill switch integrity** (smart-failure agents): the phrase appears verbatim in the `.agent.md` body and in the runner's grep condition.

## Modes

| Mode | Use when | Entry point | Reference |
|---|---|---|---|
| `action` | Plain CI/CD workflow YAML | `scripts/scaffold_github_action.py` | [create-github-action.md](references/modes/create-github-action.md) |
| `agent` | Skill to Copilot agent (A), gh-aw workflow (B) or smart-failure agent (C) | `scripts/scaffold_github_agent.py` | [create-agentic-workflow.md](references/modes/create-agentic-workflow.md) |

`scripts/scaffold_agentic_workflow.py` is an older generator for IDE (`.prompt.md`, handoffs) and CI/CD agents; use it only when you need those outputs.

## Quick start

```bash
python3 scripts/scaffold_github_action.py --category test --platform python --name "CI"
python3 scripts/scaffold_github_agent.py --skill-dir plugins/<plugin>/skills/<skill> --target B
```

## Workflow

1. Pick the mode and read its reference before running anything.
2. Gather triggers, platform or target, engine and tools; for agents, show a recap and get confirmation.
3. Run the entry point; for target B run `gh aw compile`.
4. Validate (below). On failure follow that mode's section in [fallback-tree.md](references/fallback-tree.md).

## Verification

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/<name>.yml'))"
python3 scripts/validate_github_agent.py --file .github/agents/<name>.agent.md --target A
```

Tests: `python3 -m pytest tests`. Check the mode's section in [acceptance-criteria.md](references/acceptance-criteria.md).

## References

- Modes: [create-github-action.md](references/modes/create-github-action.md) • [create-agentic-workflow.md](references/modes/create-agentic-workflow.md)
- Detail: [action-types.md](references/action-types.md) • [agent-types.md](references/agent-types.md) • [workflow-templates.md](references/workflow-templates.md) • [github-agentic-workflows.md](references/github-agentic-workflows.md)
- Gates: [acceptance-criteria.md](references/acceptance-criteria.md) • [fallback-tree.md](references/fallback-tree.md)
