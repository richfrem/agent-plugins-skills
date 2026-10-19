# Acceptance Criteria: Graph Execution

## 1. Trigger Verification
- [ ] Triggers on requests to run, execute, or resume a compiled `graph-manifest.json`.
- [ ] Does **not** trigger for designing a new graph (that is `graph-planner`), single-agent delegation, or swarm batch jobs.

## 2. Startup Gates
- [ ] Runner validates schema and topology before any node executes; invalid manifests exit 1 with no side effects.
- [ ] Mutation or irreversible graphs under `--approval none` require `--expect-manifest-sha256` and a leading `role: "approval"` verifier gate.
- [ ] Mutation graphs refuse `--no-workspace` and run only in `--worktree` / `--create-worktree` with a clean tree.

## 3. Execution Invariants
- [ ] Parallel reads never change HEAD or `git status`; any change fails the batch.
- [ ] Mutations run one at a time, touch only `mutation_targets`, never `forbidden_paths`, and never self-commit.
- [ ] The runner commits once per mutation that changed files; a no-op mutation succeeds without a commit.
- [ ] `verifier_hash` mismatches fail the node before it runs.

## 4. Failure Handling
- [ ] Retries reset mutation debris to the node's pre-run HEAD.
- [ ] Fallbacks run only when their own dependencies are complete and are recorded in `state.json` as `substituted_nodes`.
- [ ] Worktree runs roll back to the start SHA on unrecovered failure; `--no-workspace` runs halt without touching the checkout.

## 5. Evidence
- [ ] `receipts.jsonl` holds one line per attempt and survives rollback (anchored in `<git-common-dir>/graph-run/`).
- [ ] `state.json` records terminal status: `success`, `rolled_back`, or `halted`.
- [ ] The runner never pushes, merges, or deletes worktrees.
