---
name: self-evolution
plugin: agent-agentic-os
version: 2.0.0
description: "Deterministic graph-planned self-evolution engine. Enforces 6-node state transitions, worktree isolation, verifier sovereignty, and asymmetric Layer 2 knowledge persistence."
allowed-tools: Read, Write, Edit, Bash
---

# Self-Evolution (Graph-Planned Procedural Dispatcher)

Deterministic self-healing engine based on Stanford graph-planning principles. Mediated exclusively by `scripts/evolution_state.py`. Detailed operational node specs live in `references/evolution-graph-nodes.md`. Exact commands for every stage below are in `references/detailed-reference.md`.

## The 4-Box Qualification Gate
Before initiating an evolution cycle, verify:
1. Failure is structural/recurring (not a transient fluke).
2. An objective programmatic verifier command exists (`exit 0` proof).
3. Hard iteration ceiling of 3 attempts is enforced.
4. Permanent Layer 2 persistence sink is defined (`wiki/`, `references/map-debt.md`).

## State Machine Execution Flow

```
[PRIOR ART & DEBT SCAN] (Mandatory Phase 0)
       |
       ▼
[TRIAGE] -> [PLAN] -> [AWAITING_APPROVAL] ===(Human Gate)===> [AUTHORIZED]
   -> [CREATE_WORKTREE] -> [EXECUTE] -> [VERIFY_GATE]
         |-- Pass ---------------------> [PRE_COMMIT_RECEIPT] -> [COMMIT] -> [FINAL_RECEIPT] -> [COMPLETED]
         |-- Fail (attempts < 3) ------> [PLAN] (Loop)
         \-- Fail (attempts == 3) -----> [ROLLBACK] -> [FINAL_RECEIPT] -> [ESCALATED]
```

### Phase 0: Prior Art & Debt Scan (Mandatory — EVOLUTION tasks only)

Before drafting any hypothesis or entering TRIAGE: read `references/map-debt.md` for
`Repeat: YES` entries (hard blockers — escalate, don't re-attempt), read `wiki/decisions/` for
architectural constraints that rule out candidate hypotheses, and check `wiki/playbook-*.md`
for confirmed patterns or previously rejected approaches. Log the scan result via
`agent_control.py log-prior-art` before advancing (command in `references/detailed-reference.md`).
If a matching `Repeat: YES` entry exists, escalate immediately rather than re-entering the loop.

### Stage 1: Proposal Mode (Read-Only Planning)

Initialize the cycle and acquire a lock, draft the transaction manifest (candidate files,
verifier `argv`, baseline verifier SHA256 hashes — zero repo/git mutations permitted), transition
to `AWAITING_APPROVAL`, then hard-halt and await explicit user approval ("Proceed").

### Stage 2: Authorized Execution & Verification

Authorize, create the worktree sandbox (`git worktree add -b evolution/<cid> ...`), transition
through `CREATE_WORKTREE` → `EXECUTE`, apply the surgical mutation inside the worktree, then run
the controller's verifier (`evolution_state.py verify` — exits non-zero on failure; provenance is
stamped only on success) and transition to `VERIFY_GATE`.

### Stage 3: Asymmetric Persistence Gate

- **If Pass**: persist Layer 2 knowledge (tag playbooks `CONFIRMED`, log `Status: RESOLVED` in
  map-debt), then stage/commit inside the worktree (the fix and the tree the receipt binds must
  be the same tree) and land it on the calling branch via `git merge --no-ff`, then remove the
  worktree.
- **If Fail on 3rd Attempt (R1 Invariant)**: save failure insights and negative constraints to
  `wiki/` (`REJECTED`) and map-debt (`OPEN, Repeat: YES`), export Layer 2 knowledge from the
  worktree into a dedicated knowledge branch before teardown, then transition to `ROLLBACK`.

### Stage 4: Final Receipt & Completion

Generate the final receipt, transition to `COMPLETED` or `ESCALATED`, output the final
`PRE-COMPLETION GATE` block including the `EVO-INTEGRITY-...` token, and optionally dry-run
`export_upstream_pr.py`.
