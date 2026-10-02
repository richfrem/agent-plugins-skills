---
name: self-evolution
plugin: agent-agentic-os
version: 2.0.0
description: "Deterministic graph-planned self-evolution engine. Enforces 6-node state transitions, worktree isolation, verifier sovereignty, and asymmetric Layer 2 knowledge persistence."
allowed-tools: Read, Write, Edit, Bash
---

# Self-Evolution

Deterministic self-healing engine enforcing 6-node state transitions, worktree isolation, verifier sovereignty, and asymmetric Layer 2 persistence mediated by `scripts/evolution_state.py`.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **4-Box Qualification Gate**: Failure must be structural/recurring, verified by objective programmatic command (`exit 0`), bounded by max 3 attempts, and captured in Layer 2 persistence (`wiki/`, [map-debt.md](references/map-debt.md)).
2. **Proposal Mode Invariant**: Planning (`TRIAGE` -> `PLAN` -> `AWAITING_APPROVAL`) is strictly read-only. No repo mutations or worktree creation until human authorization.
3. **Verifier Sovereignty**: Acceptance gate is locked by SHA256 pre-execution hash; the mutation candidate cannot edit its own verifier.
4. **Asymmetric Persistence**: On pass, merge fix and promote learnings (`CONFIRMED`). On 3rd failure, rollback code but preserve failure insights and negative constraints in `wiki/` and [map-debt.md](references/map-debt.md) before teardown.

## Quick start

Check prior art and debt records before proposing an evolution cycle:

```bash
python3 scripts/audit_map_debt.py
```

## Workflow

1. **Phase 0: Prior Art & Debt Scan**: Scan [map-debt.md](references/map-debt.md) for `Repeat: YES` (escalate immediately if found) and `wiki/` for architectural constraints.
2. **Stage 1: Proposal & Approval**: Draft transaction manifest (files, verifier argv, baseline hashes). Transition to `AWAITING_APPROVAL` and halt for human confirmation.
3. **Stage 2: Sandboxed Execution**: Authorize via `evolution_state.py authorize`, create worktree sandbox (`evolution/<cid>`), apply surgical fix, and execute verifier.
4. **Stage 3: Verification & Persistence Gate**: Run controller verification (`evolution_state.py verify`). If pass, persist knowledge and merge. If 3rd attempt fails, export learnings and rollback code.
5. **Stage 4: Receipt & Completion**: Emit `EVO-INTEGRITY-...` cryptographic receipt and transition state to `COMPLETED` or `ESCALATED`.

## Verification

Verify evolution receipt integrity and cycle trace:

```bash
python3 scripts/verify_evolution_receipt.py --cycle-id <cycle-id>
```

## References

- [evolution-graph-nodes.md](references/evolution-graph-nodes.md) — Node specifications and transitions.
- [detailed-reference.md](references/detailed-reference.md) — Stage-by-stage command execution reference.
- [acceptance-criteria.md](references/acceptance-criteria.md) — Qualification criteria and gate requirements.
- [fallback-tree.md](references/fallback-tree.md) — Rollback and escalation tree.
- [map-debt.md](references/map-debt.md) — Repository friction and repeat-failure register.
