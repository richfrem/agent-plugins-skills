---
name: create-agentic-workflow
plugin: agent-scaffolders
description: >
  Scaffolds a Copilot GitHub agent, an agent that runs in GitHub Actions, a GitHub workflow agent, or a GitHub Agentic Workflow (gh-aw) from an existing skill. Supports three target configurations: Target A (Custom Copilot agent), Target B (GitHub Agentic Workflow), and Target C (CI/CD Smart Failure agent).
argument-hint: "[skill-dir] [--target A|B|C] [--name name] [--engine copilot|claude|codex] [--tools tools]"
allowed-tools: Bash, Read, Write
disable-model-invocation: false
---

# Create Agentic Workflow (`create-agentic-workflow`)

Scaffolds GitHub-native agent configurations from skills, targeting Custom Copilot Agents (Target A), GitHub Agentic Workflows (Target B), or CI/CD Smart Failure agents (Target C).

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Poka-Yoke Frontmatter Invariant**: Never hand-author or hand-edit `.github/agents/*.agent.md` or `.github/workflows/*.md` frontmatter. All generation must run through `scaffold_github_agent.py`.
2. **Target B Lockfile Compilation**: The companion `.github/workflows/<name>.lock.yml` is never authored directly; it must be generated via `gh aw compile`.
3. **Target C Kill Switch Integrity**: The custom Kill Switch phrase must appear verbatim in both the `.agent.md` body and the workflow runner's grep condition.

## Quick start

Scaffold a GitHub Agentic Workflow from an existing skill:

```bash
python3 scripts/scaffold_github_agent.py --skill-dir plugins/<plugin>/skills/<skill-name> --target B
```

## Workflow

1. **Resolve Input Skill**: Confirm source skill directory contains a valid `SKILL.md`.
2. **Interactive Configuration**: Select Target (A: Copilot Agent, B: gh-aw workflow, C: CI/CD Failure Agent), trigger events, AI engine (`copilot`, `claude`, `codex`), and allowed tools/write operations.
3. **Recap Gate**: Present configuration summary to user and obtain confirmation.
4. **Scaffolder Execution**: Run `scaffold_github_agent.py` to generate GitHub-native artifacts.
5. **Compilation & Validation**: Validate generated schema and run `gh aw compile` for Target B.

## Verification

Validate generated agent/workflow schema compliance:

```bash
python3 scripts/validate_github_agent.py --path .github/agents/<name>.agent.md
```

## References

- [agent-types.md](references/agent-types.md) — Architectural overview of Target A, B, and C configurations.
- [workflow-templates.md](references/workflow-templates.md) — Workflow templates and trigger matrices.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and validation criteria.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution for compilation failures and schema drift.
