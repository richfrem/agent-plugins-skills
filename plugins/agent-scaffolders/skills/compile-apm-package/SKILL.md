---
name: compile-apm-package
description: >-
  Activate when the user wants to compile an APM package into top-level context
  documents such as AGENTS.md, CLAUDE.md, or GEMINI.md, especially for Codex,
  Gemini, OpenCode, or agents-protocol style hosts. Do not use when the user
  only needs per-skill installation; use install-apm-package instead.
allowed-tools: Bash, Read, Glob
---

# Compile APM Package (`compile-apm-package`)

Compiles APM package primitives into top-level unified context documents (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) for single-file context hosts.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Artifact Status**: Compiled files (`AGENTS.md`, `GEMINI.md`) are generated outputs. Never edit compiled files directly when `.apm/` sources exist.
2. **Conditional Compilation**: Do not compile if target harness supports native directory skills; use `install-apm-package` instead.
3. **Pre-Compile Validation**: Verify package validity via validation scripts before compiling fragments into authoritative files.

## Quick start

Compile package primitives into the default top-level context document:

```bash
apm compile --verbose
```

## Workflow

1. **Verify Source**: Confirm `apm.yml` exists and package passes validation checks.
2. **Identify Target**: Determine required client format (e.g. `--target gemini` for `GEMINI.md`, `--target codex` for `AGENTS.md`).
3. **Execute Compile**: Run `apm compile [--target <slug>]`.
4. **Report Outputs**: Display generated file paths and verify merged fragment completeness.

## Verification

Validate compiled document structure and freshness against source primitives:

```bash
python3 scripts/validate_apm_package.py --check-compiled
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and compilation verification rules.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution for compilation errors and missing fragment mappings.
