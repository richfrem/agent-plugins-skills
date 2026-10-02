---
name: memory-management
plugin: agent-memory
description: Zero-dependency, filesystem-native 3-Layer Memory Engine based on Google WikiSkill and Stanford graph-planning principles.
allowed-tools: Read, Write, Bash
---

# Memory Management (`memory-management`)

Zero-dependency memory system providing high-speed cognitive continuity across agent sessions without external vector databases or daemon processes.

## Contents

- [Critical Constraints](#critical-constraints)
- [3-Layer Architecture](#3-layer-architecture)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Inference Restriction**: Historical raw execution traces and multi-page wiki dossiers are barred during active task execution to eliminate context window bloat.
2. **Confidence Decay**: Knowledge not re-verified within 30 days decays from `CONFIRMED` to `OBSERVED`.
3. **Asymmetric Persistence Rule**: When an evolution attempt fails, code mutations are rolled back, but wiki insights, edge-case discoveries, and failure logs are NEVER rolled back.
4. **Standard Library Only**: Evolution scripts and core memory lookups must never depend on external database daemons or third-party vector libraries.

## 3-Layer Architecture

- **Layer 1 (Runtime Context)**: Lean `SKILL.md` files (budget <= 100 lines) loaded strictly on-demand.
- **Layer 2 (Compounding Wiki)**: Permanent Markdown in `wiki/` and plugin `references/` (`CONFIRMED`, `OBSERVED`, `HYPOTHESIS`).
- **Layer 3 (Safe Audit Layer)**: Append-only traces in `.agent/learning/traces/cycle_manifests.jsonl` audited via `verify_evolution_receipt.py`.

## Quick start

Execute a native filesystem query across Layer 2 knowledge:

```bash
rg "Status: CONFIRMED" wiki/ references/
```

## Workflow

1. **Session Boot**: Inspect `references/map-debt.md` and relevant domain playbooks in `wiki/` before starting tasks.
2. **Execute & Learn**: Perform task under Layer 1 procedural guidance.
3. **Asymmetric Recording**: On unexpected friction or failure, record findings to `references/map-debt.md` and Layer 2 playbooks before any rollback.
4. **Audit Trace**: Log cycle metadata into Layer 3 audit manifests.

## Verification

Run the memory layer test suite to verify line budgets and native sub-50ms retrieval latency:

```bash
pytest plugins/agent-memory/tests/test_memory_layers.py
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance criteria for memory layers and boot sequencing.
- [fallback-tree.md](references/fallback-tree.md) — Fallback protocol when memory files or cache targets are missing.
