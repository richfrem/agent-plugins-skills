---
name: install-apm-package
description: >-
  Activate when the user wants to install, deploy, test, or materialize an APM
  package into runtime directories such as .agents/, .github/, .claude/,
  .cursor/, .gemini/, .codex/, .opencode/, or .windsurf/. Use after creating
  or converting an APM package.
allowed-tools: Bash, Read, Glob
---

# install-apm-package Skill 🚀

## Overview
This skill manages the safe deployment of APM primitives into their respective runtime environments. It enforces validation and target discovery to ensure byte-identical reproducibility across environments.

## 🚫 Non-Negotiables
1. **Source Integrity** — Never edit files in `.agents/`, `.github/`, or `.claude/` directly. Always edit the source in `.apm/` and re-install.
2. **Lockfile Persistence** — `apm.lock.yaml` MUST be committed after any install change.
3. **Validation First** — Always run `validate_apm_package.py` before executing the install.
4. **Project Root Discipline** — Run `apm install` from the **project root** to ensure converged skills land in the authoritative `.agents/` folder. Running inside a package directory creates local, isolated artifacts.

## Decision Tree
1. **Global Activation?** -> Run `apm install ./path-to-package` from the **project root**.
2. **Isolated Testing?** -> Run `apm install` from within the package directory.
3. **Target Inferred?** -> (e.g., `.claude/` exists) -> Run `apm install`.
4. **Ambiguous Target?** -> (No signals) -> `apm install` will exit with code 2; ask user for explicit `--target` (e.g., `agent-skills`, `claude`, `all`).
3. **Converged Skills?** -> (Standard) -> Deploys to `.agents/skills/`. Use `--target agent-skills` for explicit skill deployment.
4. **Legacy Skills?** -> (Per-client paths) -> Use `--legacy-skill-paths` flag.
5. **Production/CI?** -> Use `--frozen` flag to ensure lockfile compliance.

## Workflow
1. Verify `apm.yml` existence (locally or at root).
2. Execute `python scripts/validate_apm_package.py`.
3. **Select Execution Context**: 
   - For project-wide use: `cd <repo-root>`
   - For local test: `cd <package-dir>`
4. Preview with `apm install [--target <slug>] --dry-run --verbose`.
5. Run `apm install [./relative-path-to-pkg] [--target <slug>] [--legacy-skill-paths]`.
   - Use `--target all,agent-skills` to deploy to all harnesses AND converged skills.
6. Verify `apm.lock.yaml` update at the execution root.

## Duplicate Visibility Guardrail
Before recommending `all,agent-skills`, check whether the user is doing:
1. a routing smoke test, or
2. an actual day-to-day runtime install.

For smoke tests, `all,agent-skills` is appropriate. For real use, prefer the smallest target list that matches the runtime. Installing both converged and target-specific skills may cause duplicate skill visibility in runtimes that scan multiple skill locations.

## Anti-Patterns
- **Manual Materialization**: Moving files into `.github/agents/` by hand instead of using `apm install`.
- **Ignoring the Lockfile**: Failing to commit `apm.lock.yaml` after adding a dependency.
- **Editing Artifacts**: Modifying the generated runtime output instead of the `.apm/` source.
