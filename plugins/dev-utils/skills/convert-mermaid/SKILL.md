---
name: convert-mermaid
plugin: dev-utils
description: Translate .mmd diagram files into PNG images with configurable resolution, supporting binary linting and Puppeteer-based rendering.
allowed-tools: Bash, Read, Write
---

# Mermaid Diagram Converter (`convert-mermaid`)

Orchestrates the conversion of `.mmd` syntax files into high-resolution `.png` binary images with deterministic verification.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Never Write Binary Streams Directly**: LLMs cannot safely generate raw `.png` bitstreams in context.
2. **Never `cat` Binary Files**: Reading binary `.png` files into context corrupts agent memory; always use `scripts/verify_png.py`.
3. **Always Verify Output**: Immediately verify output files using `scripts/verify_png.py`.

## Quick start

Convert a diagram with 3x retina scaling and verify binary integrity:

```bash
python3 scripts/convert.py -i architecture.mmd -o architecture.png -s 3
python3 scripts/verify_png.py architecture.png
```

## Workflow

1. **Engine Execution**: Invoke `scripts/convert.py` with input and output paths. Set `-s 3` or `-s 4` for retina/HQ requests.
2. **Delegated Verification**: Run `scripts/verify_png.py` to confirm the generated output is a valid non-empty PNG binary.
3. **Outcome Resolution**:
   - `"status": "success"` -> Output verified. Proceed.
   - `"status": "errors_found"` -> Review JSON error logs and consult [Fallback Tree](references/fallback-tree.md).

## Verification

Run the verification script against the generated PNG:

```bash
python3 scripts/verify_png.py architecture.png
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Image generation standards and acceptance criteria.
- [fallback-tree.md](references/fallback-tree.md) — Failure triage and escalation tree for rendering errors.
