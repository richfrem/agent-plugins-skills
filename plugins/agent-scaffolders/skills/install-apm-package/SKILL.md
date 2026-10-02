---
name: install-apm-package
description: >-
  Activate when the user wants to install, deploy, test, or materialize an APM
  package into runtime directories such as .agents/, .github/, .claude/,
  .cursor/, .gemini/, .codex/, .opencode/, or .windsurf/. Use after creating
  or converting an APM package.
allowed-tools: Bash, Read, Glob
---

# Install APM Package (`install-apm-package`)

Manages the safe deployment and materialization of APM package primitives into target client runtimes (.agents/, .claude/, .github/, etc.) with lockfile reproducibility.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Source Integrity**: Never edit deployed files in `.agents/`, `.github/`, or `.claude/` directly. Always edit the source package and re-install.
2. **Lockfile Enforcement**: `apm.lock.yaml` must be committed after install modifications. Use `--frozen` in CI.
3. **Validation Pre-Condition**: Always run `validate_apm_package.py` before executing installations.
4. **Project Root Discipline**: Run `apm install` from project root for converged skills (`.agents/skills/`).

## Quick start

Preview deployment targets and actions without mutating files:

```bash
apm install --dry-run --verbose
```

## Workflow

1. **Pre-Check**: Verify `apm.yml` exists and run validation helper.
2. **Select Context**: Choose project root (for standard converged skills) or package directory (for isolated testing).
3. **Execute Installation**: Run `apm install [./path-to-pkg] [--target <slug>]`.
   - Prefer minimal target lists for real use to avoid duplicate skill visibility in multi-client runtimes.
4. **Persist Lockfile**: Ensure `apm.lock.yaml` is updated and staged.

## Verification

Validate installed package integrity and lockfile compliance:

```bash
python3 scripts/validate_apm_package.py --check-lockfile
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and target verification criteria.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution for installation failures and target collisions.
