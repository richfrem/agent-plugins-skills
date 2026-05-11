---
description: Validate and install an APM package into target runtime directories (.agents/, .github/, .claude/, etc.)
argument-hint: "[package-path] [--target all,agent-skills|agent-skills|claude|cursor] [--frozen] [--legacy-skill-paths] [--dry-run]"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

# install-apm-package

Validate an APM package and run `apm install` safely to materialize primitives into runtime directories.

## Usage

```bash
/install-apm-package ./packages/my-skill --target agent-skills
/install-apm-package ./packages/my-skill --target all,agent-skills --verbose
```

## Workflow

1. **Validation**: Runs `scripts/validate_apm_package.py` to ensure the manifest and structure are sound.
2. **Target Discovery**: Inspects `apm.yml` and the local environment for harness signals.
3. **Execution**: Invokes `apm install` (with optional `--target` or `--frozen` flags).
4. **Reporting**: Lists the directories updated (e.g., `.agents/skills/`, `.claude/skills/`).
5. **Hygiene**: Reminds the user that source remains in `.apm/` and generated files should not be edited.

> [!IMPORTANT]
> Always commit your `apm.lock.yaml` after installation to ensure reproducibility.
