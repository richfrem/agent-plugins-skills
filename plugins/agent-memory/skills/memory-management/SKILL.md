---
name: memory-management
plugin: agent-memory
description: "Zero-dependency, filesystem-native 3-Layer Memory Engine based on Google WikiSkill and Stanford graph-planning principles."
allowed-tools: Read, Write, Bash
---

# Memory Management (3-Layer Filesystem Engine)

Zero-dependency memory system providing high-speed cognitive continuity across agent sessions without external vector databases or daemon processes.

## The 3 Filesystem Layers

1. **Layer 1: Runtime Context (Lean Procedural Core)**
   - Lean `SKILL.md` files (target <= 100 lines).
   - Loaded strictly on-demand.
   - **Inference Restriction:** Historical raw execution traces and multi-page wiki dossiers are barred during active task execution to eliminate context window bloat.

2. **Layer 2: Compounding Wiki Layer (Permanent Knowledge)**
   - Permanent Markdown documents stored in `wiki/` and plugin `references/`.
   - Contains: domain playbooks, known edge cases, negative constraints, `map-debt.md`, and `evolution-log.md`.
   - **Knowledge Status Taxonomy:** Entries are tagged with explicit confidence (`OBSERVED`, `HYPOTHESIS`, `CONFIRMED`, `REJECTED`, `OPEN`).
   - **Confidence Decay:** Knowledge not re-verified within 30 days decays from `CONFIRMED` to `OBSERVED`.
   - **Asymmetric Persistence Rule:** When an evolution attempt fails, code mutations are rolled back, but wiki insights, edge-case discoveries, and failure logs are NEVER rolled back.

3. **Layer 3: Safe Audit Layer (Append-Only Manifests)**
   - Stored in `.agent/learning/traces/cycle_manifests.jsonl`.
   - Tracked audit log capturing event sequences, hashes, exit codes, and affected paths (zero raw terminal text or credentials).
   - Audited exclusively via `verify_evolution_receipt.py`.

## Standardized Retrieval Protocol

All memory lookups use native filesystem tools:
1. **Targeted Exact Match:** `rg "<symbol-or-pattern>" <dir>` or `grep_search`.
2. **Playbook Inspection:** Direct file read of `references/<topic>-playbook.md` or `wiki/<topic>.md`.
3. **Map Debt Audit:** Scan `references/map-debt.md` for existing open friction items before starting tasks.
