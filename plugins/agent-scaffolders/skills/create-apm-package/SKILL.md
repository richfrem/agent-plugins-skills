---
name: create-apm-package
description: >-
  Activate when the user wants to create a new APM-native package from scratch 
  for reusable agent skills, agents, commands, hooks, MCP configuration, 
  prompts, or governance-managed agent assets. Do not use this for existing 
  plugin migration; use convert-plugin-to-apm instead.
allowed-tools: Bash, Read, Write
---

# create-apm-package Skill 🏗️

## Overview
This skill scaffolds a new APM-native package using the "Source in .apm/" pattern. It is used for greenfield projects where APM is the primary distribution format from day one.

## 🚫 Non-Negotiables
1. **Source in .apm/** — Primitives MUST be authored inside the `.apm/` directory.
2. **Kebab-case** — Package names must be lowercase with hyphens.
3. **No Overwrites** — Never overwrite an existing directory without explicit confirmation.
4. **Governance Docs** — Every package must include `docs/governance.md`.

## Decision Tree
1. **New Package?** -> Proceed with `scripts/scaffold_apm.py`.
2. **Existing Plugin?** -> Route to `convert-plugin-to-apm`.
3. **Hybrid needed?** -> Use `--allow-hybrid` flag in scaffold script.

## Generated Structure
```text
<package-name>/
  apm.yml
  README.md
  .gitignore
  .apm/
    skills/
    agents/
    instructions/
    prompts/
    hooks/
    mcp/
    scripts/
    tests/
  docs/
    governance.md
    attribution.md
    package-lifecycle.md
  scripts/
  tests/
```

## Validation Steps
After scaffolding, always run:
```bash
python scripts/validate_apm_package.py --path ./<package-name>
```

## Anti-Patterns
- **Duplicate Roots**: Creating `.apm/skills` while also having `skills/` in the same package.
- **Missing Docs**: Skipping the `docs/` folder in a `team` or `enterprise` lane.
- **Absolute Paths**: Using machine-specific paths in `apm.yml`.
