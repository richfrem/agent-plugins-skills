---
description: Compile an APM package into top-level context files such as AGENTS.md, CLAUDE.md, or GEMINI.md.
argument-hint: "[package-path] [--target codex|gemini|opencode|claude]"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
---

# compile-apm-package

Validate the APM package and generate top-level context documents for harnesses that require them.

## Usage

```bash
/compile-apm-package ./packages/my-skill --target gemini
```

## Workflow

1. **Validation**: Verifies package integrity before compilation.
2. **Evaluation**: Determines if compilation is necessary (required for Gemini/Codex; optional for Copilot/Claude).
3. **Execution**: Invokes `apm compile` to generate merged context files.
4. **Handoff**: Identifies the generated files (e.g., `AGENTS.md`, `GEMINI.md`).

> [!NOTE]
> `apm compile` is distinct from `apm install`. Use compile when your target harness requires a single authoritative context document rather than a directory-based skill structure.
