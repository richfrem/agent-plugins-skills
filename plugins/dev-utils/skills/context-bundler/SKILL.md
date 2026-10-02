---
name: context-bundler
plugin: dev-utils
description: Interactively creates targeted code and documentation bundles (Markdown or ZIP) for review and sub-agent task delegation.
allowed-tools: Bash, Read, Write, Glob, Grep
---

# Context Bundler (`context-bundler`)

Compiles codebase files, documentation, and persona prompts into portable payloads for AI chat interfaces, sub-agents, or external review.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Execution Modes](#execution-modes)
- [Workflow](#workflow)
- [Persona Template Library](#persona-template-library)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Gitignored Storage**: All manifests and bundles MUST be generated inside a gitignored `temp/` subfolder (e.g. `temp/bundles/`). Never write payloads to repo root.
2. **First File Entry**: For persona-driven reviews, `prompt.md` must be listed as the first file entry in the manifest.

## Quick start

Generate a Markdown bundle from a file manifest:

```bash
python3 scripts/bundle.py --manifest temp/bundles/file-manifest.json --bundle temp/bundles/payload.md
```

## Execution Modes

1. **Standard Bundle**: Custom file/folder selection for general context sharing.
2. **Persona Review**: Injects review persona prompts (`prompt.md`) ahead of codebase files.
3. **Monorepo Segmented**: Domain-partitioned packaging (`/skills`, `/agents`, `/scripts`, `/docs`).
4. **Multi-Persona Fan-Out**: Parallel packaging for the Graph Planning Fan-Out Trio (Architecture, Security, TDD).

## Workflow

1. **Discovery**: Select mode (Standard, Persona, Fan-Out), format (`.md` or `.zip`), and targets.
2. **Manifest Generation**: Write `file-manifest.json` in `temp/context-bundle-[name]/`.
3. **Execute Compiler**: Run `scripts/bundle.py` or `scripts/bundle_zip.py` to compile the payload.
4. **Handoff**: Present generated payload path to user or dispatch to sub-agents.

## Persona Template Library

Templates in `assets/templates/`:
- `structural-architecture-reviewer.md` — C4 model, SOLID, interface abstraction.
- `adversarial-security-auditor.md` — OWASP, injection vectors, exploit scenarios.
- `tdd-contract-reviewer.md` — Test fixtures, assertion contracts, testability.
- `agent-task-delegator.md` — Turnkey sub-agent handoffs with tool gates.
- `refactoring-quality-specialist.md` — Complexity reduction and clean diffs.

## Verification

Confirm generated bundle exists and contains valid aggregated content:

```bash
test -f temp/bundles/payload.md && wc -l temp/bundles/payload.md
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for context bundling and schema validation.
- [fallback-tree.md](references/fallback-tree.md) — Fallback protocol when files or bundle paths are missing.