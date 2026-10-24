# Lab Setup (the `setup` mode)

Bootstrap lab environments for skill improvement runs, copying plugin files as real files (no symlinks) and configuring `eval-instructions.md`.

## When to use

Carried over from the description of the former skill, so its trigger phrases and exclusions stay on record:

> Bootstraps an isolated lab repo for a skill improvement run: initializes git, copies the plugin as real files, renders eval-instructions.md, commits the baseline and offers manual or autonomous launch options. Trigger with "set up an eval lab", "bootstrap the eval repo", "prepare the test repo for skill evaluation", "create an eval environment for this skill", "set up the lab space for this skill", or when starting a new skill optimization run that needs a standalone test environment. DO NOT USE to run the improvement loop (use the `loop` mode), to score a change (use the `score` mode), to plan what to improve (use the `plan` mode), or to backport lab results to master (use the `backport` mode).

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
5. **Launch Options**: Provide the user with manual instructions or an autonomous CLI launcher command (for `agy`-based launches, see `cli-agent` with `--cli agy`). Hand the run itself to the `loop` mode.

## Verification

Confirm lab repo contains materialized files and valid `eval-instructions.md`:

```bash
test -f "<lab-repo-path>/eval-instructions.md" && echo "Lab setup valid"
```

## References

- [detailed-reference.md](../setup-detailed-reference.md) — Intake questions, option tables, and exact bootstrap commands.
- [acceptance-criteria.md](../acceptance-criteria.md#mode-setup) — Verification criteria for bootstrapped lab environments.
- [fallback-tree.md](../fallback-tree.md#mode-setup) — Remediation pathways if lab initialization or generation fails.
