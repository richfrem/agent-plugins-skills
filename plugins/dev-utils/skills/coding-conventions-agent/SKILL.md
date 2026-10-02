---
name: coding-conventions-agent
plugin: dev-utils
description: Enforces codebase coding conventions, file headers, type hints, Google docstrings, and naming standards across languages.
allowed-tools: Read, Write, Bash
---

# Coding Conventions Agent (`coding-conventions-agent`)

Enforces project-wide coding policy alignment across Python, TypeScript/JavaScript, and C#/.NET.

## Contents

- [Critical Constraints](#critical-constraints)
- [Header Templates](#header-templates)
- [Naming Conventions](#naming-conventions)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Dual-Layer Docs**: External comment above + internal docstring inside every non-trivial function/class.
2. **File Headers**: Every source file must begin with a standardized purpose header.
3. **Type Annotations**: All Python function signatures require complete type annotations.
4. **Refactor Threshold**: Functions exceeding 50+ lines or 3+ nesting levels must be refactored into helpers.
5. **Zero Stubs**: Reject placeholder tokens (`TODO`, `TBD`, `[NEEDS INPUT]`) in completed code.

## Header Templates

Use templates located in `assets/templates/`:
- [Python Template](assets/templates/python-tool-header-template.py)
- [JavaScript / TypeScript Template](assets/templates/js-tool-header-template.js)
- [React TSX Template](assets/templates/tsx-tool-header-template.tsx)
- [Bash Tool Template](assets/templates/bash-tool-header-template.sh)

## Naming Conventions

| Language | Functions/Vars | Classes | Constants | Private Fields |
|---|---|---|---|---|
| **Python** | `snake_case` | `PascalCase` | `UPPER_SNAKE_CASE` | `_leading_underscore` |
| **TS/JS** | `camelCase` | `PascalCase` | `UPPER_SNAKE_CASE` | `_leading_underscore` |
| **C#** | `PascalCase` (public) | `PascalCase` | `PascalCase` | `_camelCase` |

## Quick start

Execute the workspace conventions auditor across the project:

```bash
python3 scripts/workspace_conventions_auditor.py
```

## Workflow

1. **Language Detection**: Identify target file languages and load corresponding header templates.
2. **Standard Enforcement**: Apply dual-layer documentation and type annotations to new/modified code.
3. **Threshold Check**: Extract any function exceeding 50 lines or 3 nesting levels into named helpers.
4. **Audit Execution**: Run `workspace_conventions_auditor.py` to confirm full compliance.

## Verification

Review audit findings in generated report:

```bash
python3 scripts/workspace_conventions_auditor.py && test -f temp/workspace_conventions_report.md
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Compliance gates and indexing checks.
- [coding-conventions.md](references/coding-conventions.md) — Authoritative codebase coding standards.
- [fallback-tree.md](references/fallback-tree.md) — Fallback protocol when templates or threshold limits are encountered.
- [graph-planning-superpowers-policy.md](references/graph-planning-superpowers-policy.md) — Graph planning and code quality rules.
- [map-debt.md](references/map-debt.md) — Technical debt and friction log.
