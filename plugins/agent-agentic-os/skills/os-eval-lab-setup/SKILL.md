---
name: os-eval-lab-setup
plugin: agent-agentic-os
description: >
  Bootstraps a skill evaluation lab repo for an autoresearch improvement run. Trigger with
  "set up an eval lab", "bootstrap the eval repo", "prepare the test repo for skill evaluation",
  "create an eval environment for this skill", "set up the lab space for this skill",
  or when starting a new skill optimization run that needs a standalone test environment.
argument-hint: "[lab-repo-path] [skill-path] [github-url]"
allowed-tools: Bash, Read, Write
---

# Eval Lab Setup (`os-eval-lab-setup`)

Bootstrap evaluation lab environments for autoresearch improvement runs, copying plugin files as real files (no symlinks) and configuring `eval-instructions.md`.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Resolve Symlinks on Copy**: Always use `cp -RL` so the lab repo contains independent, standalone files.
2. **Clean Slate**: Remove `.agent .agents .gemini .claude` directories in the lab repo before installing.
3. **Workspace Permissions**: Confirm directory permissions before creating or mutating lab repositories.

## Quick start

Generate evaluation instructions for a target skill in a lab repo:

```bash
python3 scripts/generate_eval_instructions.py --skill <skill-name> --lab-repo <path>
```

## Workflow

1. **Intake**: Gather lab repo path, target plugin path, skill name, and GitHub repository URL.
2. **Bootstrap Lab Repo**: Initialize git repository, clean slate, and copy plugin files via `cp -RL`.
3. **Generate Instructions**: Render `eval-instructions.md` from `assets/templates/eval-instructions.template.md`.
4. **Seed Commit**: Commit baseline state in lab repo and push to origin.
5. **Launch Options**: Provide user with Manual instructions or Autonomous CLI launcher command.

## Verification

Confirm lab repo contains materialized files and valid `eval-instructions.md`:

```bash
test -f "<lab-repo-path>/eval-instructions.md" && echo "Lab setup valid"
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Intake questions, option tables, and exact bootstrap commands.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Verification criteria for bootstrapped lab environments.
- [fallback-tree.md](references/fallback-tree.md) — Remediation pathways if lab initialization or generation fails.
