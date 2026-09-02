---
name: self-evolution
plugin: agent-agentic-os
version: 2.0.0
description: "Deterministic graph-planned self-evolution engine. Enforces 6-node state transitions, worktree isolation, verifier sovereignty, and asymmetric Layer 2 knowledge persistence."
allowed-tools: Read, Write, Edit, Bash
---

# Self-Evolution (Graph-Planned Procedural Dispatcher)

Deterministic self-healing engine based on Stanford graph-planning principles. Mediated exclusively by `scripts/evolution_state.py`. Detailed operational node specs live in `references/evolution-graph-nodes.md`.

## The 4-Box Qualification Gate
Before initiating an evolution cycle, verify:
1. Failure is structural/recurring (not a transient fluke).
2. An objective programmatic verifier command exists (`exit 0` proof).
3. Hard iteration ceiling of 3 attempts is enforced.
4. Permanent Layer 2 persistence sink is defined (`wiki/`, `references/map-debt.md`).

## State Machine Execution Flow

```
[TRIAGE] -> [PLAN] -> [AWAITING_APPROVAL] ===(Human Gate)===> [AUTHORIZED]
   -> [CREATE_WORKTREE] -> [EXECUTE] -> [VERIFY_GATE]
         |-- Pass --------------------> [PRE_COMMIT_RECEIPT] -> [COMMIT] -> [FINAL_RECEIPT] -> [COMPLETED]
         |-- Fail (attempts < 3) -----> [PLAN] (Loop)
         \-- Fail (attempts == 3) ----> [ROLLBACK] -> [FINAL_RECEIPT] -> [ESCALATED]
```

### Stage 1: Proposal Mode (Read-Only Planning)
1. **Initialize Cycle & Acquire Lock:**
   ```bash
   python3 scripts/evolution_state.py init --cycle-id "<cid>" --tier "<tier>"
   python3 scripts/record_trace.py append --cycle-id "<cid>" --node TRIAGE --event-type cycle.initialized --exit-code 0
   ```
2. **Draft Transaction Manifest & Plan:**
   - Record candidate files, objective verifier `argv`, and lock baseline verifier SHA256 hashes.
   - Zero repo/git mutations permitted in proposal mode.
   ```bash
   python3 scripts/evolution_state.py plan --manifest <path/to/manifest.json>
   python3 scripts/evolution_state.py transition --to AWAITING_APPROVAL
   ```
3. **Hard Halt:** Present proposal to user and await explicit approval ("Proceed").

### Stage 2: Authorized Execution & Verification
1. **Authorize & Create Worktree Sandbox:**
   ```bash
   python3 scripts/evolution_state.py authorize --cycle-id "<cid>" --operations create_worktree,mutate,verify,write_layer2,commit
   git worktree add -b evolution/<cid> ../worktree-evolution-<cid> HEAD
   python3 scripts/evolution_state.py transition --to CREATE_WORKTREE --worktree-path ../worktree-evolution-<cid>
   python3 scripts/evolution_state.py transition --to EXECUTE
   ```
2. **Apply Surgical Mutation & Verify:**
   - Apply edits inside worktree. Then execute verifier via controller:
   ```bash
   # Controller executes the declared verifier itself (from transaction_manifest.verifier_argv).
   # Exits non-zero if the verifier fails; provenance is stamped only on success.
   python3 scripts/evolution_state.py verify
   python3 scripts/record_trace.py append --cycle-id "<cid>" --node VERIFY_GATE \
     --event-type verification.completed --exit-code $?
   python3 scripts/evolution_state.py transition --to VERIFY_GATE
   ```

### Stage 3: Asymmetric Persistence Gate
- **If Pass (`exit 0`):**
  1. Persist Layer 2 knowledge: tag playbooks in `wiki/` as `CONFIRMED`; log `Status: RESOLVED` in `references/map-debt.md`.
  2. Stage and commit inside the worktree (design intent: the fix and the tree the receipt binds
     must be the same tree -- `git write-tree`/`git commit` must run against the worktree's own
     index, not the main checkout's), then land it on the calling branch:
     ```bash
     python3 scripts/evolution_state.py transition --to PRE_COMMIT_RECEIPT
     git -C ../worktree-evolution-<cid> add -A
     TREE_SHA=$(git -C ../worktree-evolution-<cid> write-tree)
     python3 scripts/verify_evolution_receipt.py --stage pre-commit --cycle-id "<cid>" --tree-sha "$TREE_SHA"
     python3 scripts/evolution_state.py transition --to COMMIT
     git -C ../worktree-evolution-<cid> commit -m "feat(evolution): verified repair for <cid>"
     python3 scripts/evolution_state.py transition --to FINAL_RECEIPT
     git merge --no-ff evolution/<cid> -m "merge(evolution): land verified repair for <cid>"
     git worktree remove --force ../worktree-evolution-<cid> && git branch -D evolution/<cid>
     ```
- **If Fail on 3rd Attempt (R1 Invariant):**
  1. Save failure insights and negative constraints in `wiki/` (`REJECTED`) and `references/map-debt.md` (`OPEN, Repeat: YES`).
  2. Export Layer 2 knowledge from worktree into dedicated knowledge branch before worktree teardown:
     ```bash
     python3 scripts/evolution_state.py export-layer2 --cycle-id "<cid>" --commit-knowledge \
       --from-worktree ../worktree-evolution-<cid> --to-main <main-repo-path>
     git worktree remove --force ../worktree-evolution-<cid> && git branch -D evolution/<cid>
     python3 scripts/evolution_state.py transition --to ROLLBACK
     python3 scripts/evolution_state.py transition --to FINAL_RECEIPT
     ```

### Stage 4: Final Receipt & Completion
1. Generate final receipt and complete cycle:
   ```bash
   python3 scripts/verify_evolution_receipt.py --stage final --cycle-id "<cid>"
   python3 scripts/evolution_state.py transition --to COMPLETED  # or ESCALATED
   ```
2. Output final `PRE-COMPLETION GATE` block including the `EVO-INTEGRITY-...` token.
3. Optional dry-run upstream export: `python3 scripts/export_upstream_pr.py --dry-run`.
