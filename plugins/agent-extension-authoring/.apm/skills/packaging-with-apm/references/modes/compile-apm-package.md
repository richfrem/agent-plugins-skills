> Retired skill `compile-apm-package`, kept as the **compile-apm-package** mode of `packaging-with-apm`. Body unchanged apart from link targets, moved script/test paths and the compile verification command (`apm compile --validate`). Frontmatter removed.
>
> Original description: Activate when the user wants to compile an APM package into top-level context documents such as AGENTS.md, CLAUDE.md, or GEMINI.md, especially for Codex, Gemini, OpenCode, or agents-protocol style hosts. Do not use when the user only needs per-skill installation; use install-apm-package instead.

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
apm compile --validate
```

## References

- [acceptance-criteria.md](../acceptance-criteria.md) — Acceptance gates and compilation verification rules.
- [fallback-tree.md](../fallback-tree.md) — Fallback resolution for compilation errors and missing fragment mappings.
