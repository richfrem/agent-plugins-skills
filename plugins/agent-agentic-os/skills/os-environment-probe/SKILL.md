---
name: os-environment-probe
plugin: agent-agentic-os
description: >
  Discovers and persists the user's available AI environments (Claude, Copilot CLI,
  Agy CLI, Cursor, etc.) to context/memory/environment.md. Run once after OS setup
  or whenever the environment changes. os-architect and os-evolution-planner read this
  file to select the right delegation backend and cheapest brainstorm model automatically.
  Invoked by os-architect on first run if environment.md is absent.
model: inherit
color: cyan
tools: ["Bash", "Read", "Write"]
---

# Environment Probe (`os-environment-probe`)

Discovers, verifies, and records available local AI CLI environments (Copilot CLI, Agy CLI, Claude, Cursor) into `context/memory/environment.md` for automated backend dispatch.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Verification Before Recording**: Only record environments that pass active probe execution. Never write an unverified claimed environment.
2. **Safe Idempotent Overwrite**: Re-probing safely refreshes `context/memory/environment.md` without destructive side-effects.
3. **Fallback Priority**: Downstream routing defaults to Claude-only mode if `environment.md` is absent.

## Quick start

Probe the local system for active CLI tools:

```bash
python3 scripts/probe_environments.py --check
```

## Workflow

1. **Environment Interview**: Ask which AI tools are active (Claude Code, Copilot CLI, Agy CLI, Cursor).
2. **Execute Probes**: Verify each claimed tool:
   - Copilot CLI: `gh copilot explain "test" 2>&1 | head -3`
   - Agy CLI: `agy --version 2>&1 | head -1`
   - Cursor: `cursor --version 2>&1 | head -1`
3. **Persist State**: Write verified profiles to `context/memory/environment.md`.
4. **Downstream Integration**: Notify caller (`os-architect` or `os-evolution-planner`) of confirmed backends and model tier preferences.

## Verification

Confirm environment profile file exists and contains valid Markdown formatting:

```bash
python3 scripts/probe_environments.py --validate
```

## References

- [detailed-reference.md](references/detailed-reference.md) — Output schema, probe timeouts, and error handling.
- [cheapest_models.md](references/cheapest_models.md) — Model cost tiers and backend prioritization rules.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Verification checklist and gate requirements.
- [gemini-detection-example.md](references/gemini-detection-example.md) — Gemini detection output format and probe examples.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution when probe binaries fail or timeout.
