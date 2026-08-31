# Evolution Graph State Machine: Node Operational Specifications

Authoritative reference guide for deterministic state transitions governed by `scripts/evolution_state.py`.

---

## Node 1: TRIAGE (Proposal Mode)
- **Objective:** Qualify evolution trigger under the 4-Box Automation Gate.
- **Inference Restriction:** Do NOT read historical raw execution traces or monolithic wikis into runtime context.
- **Spinlock Acquisition:** Invokes directory spinlock (`.agent/learning/evolution.lock`) with PID liveness check.
- **Deterministic Crash Recovery Decision Tree:**
  1. If `cycle_manifests.jsonl` contains only `cycle.initialized` with no mutations: clean reset to `TRIAGE`.
  2. If `mutation.completed` exists and worktree clean: resume directly from `VERIFY_GATE`.
  3. If uncommitted changes exist not recorded in manifest: transition to `RECOVERY_REQUIRED` and halt.
- **CLI Commands:**
  ```bash
  python3 scripts/evolution_state.py init --cycle-id "<cid>" --tier "<tier>"
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node TRIAGE --event-type cycle.initialized --exit-code 0
  python3 scripts/evolution_state.py transition --to PLAN
  ```

---

## Node 2: PLAN (Proposal Mode)
- **Objective:** Formulate immutable Transaction Manifest and surgical 3-5 point repair plan.
- **Verifier Sovereignty Guard:** Records pre-execution SHA256 hashes of verifier scripts (`evaluate.py`, tests, policies) and locks them. Bans trivial verifiers (`true`, `exit 0`).
- **Proposal Mode Invariant:** Zero git mutations or worktree creations permitted in this node.
- **CLI Commands:**
  ```bash
  python3 scripts/evolution_state.py plan --manifest <path/to/manifest.json>
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node PLAN --event-type plan.completed --exit-code 0
  python3 scripts/evolution_state.py transition --to AWAITING_APPROVAL
  ```
- **Hard Halt:** Halts at `AWAITING_APPROVAL` for human authorization.

---

## Node 3: AUTHORIZED & CREATE_WORKTREE (Authorized Execution Mode)
- **Objective:** Transition into authorized mode and create isolated workspace.
- **Authorization Gate:** Requires explicit user approval ("Proceed", "Go", "Execute").
- **3-Tier Isolation Fallback:**
  - Tier 1: `git worktree add -b evolution/<cid> ../worktree-evolution-<cid> <initial_git_head>`
  - Tier 2 (Fallback): In-tree feature branch with git stash guard.
  - Tier 3 (CI / Container): In-place execution.
- **CLI Commands:**
  ```bash
  python3 scripts/evolution_state.py authorize --cycle-id "<cid>" --operations create_worktree,mutate,verify,write_layer2,commit
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node AUTHORIZED --event-type authorization.granted --exit-code 0
  python3 scripts/evolution_state.py transition --to CREATE_WORKTREE
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node CREATE_WORKTREE --event-type worktree.created --exit-code 0
  python3 scripts/evolution_state.py transition --to EXECUTE
  ```

---

## Node 4: EXECUTE (Authorized Execution Mode)
- **Objective:** Apply surgical mutations strictly within the authorized target list.
- **Single-Attempt Scope:** One declared mutation transaction followed by verification.
- **CLI Commands:**
  ```bash
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node EXECUTE --event-type attempt.started --attempt-id "att-<n>"
  # Apply code edits...
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node EXECUTE --event-type mutation.completed --paths-affected "plugins/..."
  python3 scripts/evolution_state.py transition --to VERIFY_GATE
  ```

---

## Node 5: VERIFY_GATE (Automated Proof Check)
- **Objective:** Execute objective verifier and record proof.
- **Sovereignty Invariant:** Verifies verifier scripts are unchanged from baseline (abort with exit code 2 if tampered).
- **Non-Mutating Verification:** Executes verifier in `--decision-only` mode (evaluator must NOT run `git checkout`).
- **CLI Commands:**
  ```bash
  python3 scripts/evaluate.py --skill <skill-path> --decision-only
  python3 scripts/evolution_state.py record-verification --exit-code <code>
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node VERIFY_GATE --event-type verification.completed --exit-code <code>
  ```
- **Branching Decision:**
  - If `exit 0`: `python3 scripts/evolution_state.py transition --to PRE_COMMIT_RECEIPT`
  - If `exit != 0` and attempts < 3: `python3 scripts/evolution_state.py transition --to PLAN`
  - If `exit != 0` and attempts == 3: `python3 scripts/evolution_state.py transition --to ROLLBACK`

---

## Node 6A: PRE_COMMIT_RECEIPT & COMMIT (Pass Branch)
- **Objective:** Bind staged git tree, generate receipt, and commit.
- **Asymmetric Knowledge Persistence First:**
  1. Tag new playbooks in `wiki/` with `Status: CONFIRMED`.
  2. Append `Status: RESOLVED` entry in `references/map-debt.md`.
  3. Append entry in `references/evolution-log.md`.
- **Pre-Commit Cryptographic Receipt:**
  ```bash
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node PRE_COMMIT_RECEIPT --event-type knowledge.persisted --exit-code 0
  git add <authorized-files>
  TREE_SHA=$(git write-tree)
  python3 scripts/verify_evolution_receipt.py --stage pre-commit --cycle-id "<cid>" --tree-sha "$TREE_SHA"
  python3 scripts/evolution_state.py transition --to COMMIT
  git commit -m "feat(evolution): verified repair for <cid>"
  python3 scripts/record_trace.py append --cycle-id "<cid>" --node COMMIT --event-type commit.completed --exit-code 0
  python3 scripts/evolution_state.py transition --to FINAL_RECEIPT
  ```

---

## Node 6B: ROLLBACK (3rd Failure Asymmetric Rollback)
- **Objective:** Discard broken code mutations while permanently retaining knowledge.
- **Worktree Transfer Protocol (R1 Invariant):**
  1. Record negative constraints, reproduction notes, and failure insights in `wiki/` (`Status: REJECTED` or `Status: OPEN`).
  2. Append `Status: OPEN, Repeat: YES` in `references/map-debt.md`.
  3. Export Layer 2 artifacts from temporary worktree to main repository checkout before teardown:
     ```bash
     python3 scripts/evolution_state.py export-layer2 --from-worktree <path> --to-main <main-repo-path>
     ```
  4. Tear down temporary worktree and delete feature branch:
     ```bash
     git worktree remove --force <worktree-path>
     git branch -D evolution/<cid>
     ```
  5. Code is clean in main checkout; Layer 2 insights are durably preserved.
  6. Transition:
     ```bash
     python3 scripts/evolution_state.py transition --to FINAL_RECEIPT
     ```

---

## Node 7: FINAL_RECEIPT & Optional Upstream PR Dry-Run
- **Objective:** Final receipt generation and terminal completion.
- **Final Integrity Receipt:**
  ```bash
  python3 scripts/verify_evolution_receipt.py --stage final --cycle-id "<cid>"
  python3 scripts/evolution_state.py transition --to COMPLETED  # or ESCALATED
  ```
- **Optional Upstream Export Hook:**
  ```bash
  python3 scripts/export_upstream_pr.py --dry-run
  ```
  *(Requires separate explicit human gate for any remote execution).*
