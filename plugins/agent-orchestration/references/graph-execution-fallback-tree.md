# Procedural Fallback Tree: Graph Execution

## 1. Manifest Rejected at Startup
If the runner exits 1 with `Manifest schema validation failed` or `Manifest topology validation failed`:
- **Action**: Do not edit the manifest to force it through. Return it to `graph-planner` with the exact error lines.
- **Guardrail**: A manifest edited after approval changes its SHA256; the old `--expect-manifest-sha256` value must then be re-approved, never recomputed by the executing agent.

## 2. Manifest SHA Mismatch
If the runner reports `Manifest SHA256 mismatch`:
- **Action**: Halt. The manifest on disk is not the one that was approved. Escalate to the human who approved it.

## 3. Approval Prompt Rejected in a Non-Interactive Shell
If `--approval prompt` prints `Non-interactive stdin detected`:
- **Action**: Expected when an agent runs the command. Ask the human to run it in their own terminal (`! <command>`), or use `--approval none` with a human-approved manifest SHA and an approval gate.
- **Guardrail**: Never pipe `y` into the runner or fabricate approval.

## 4. Barrier or Immutability Failure
If a read node `modified tracked or untracked files` or `moved HEAD`:
- **Action**: The node is not read-only. Send it back to planning as a `sequential_mutation` with `mutation_targets`, or move its writes into `$GRAPH_SCRATCH_DIR`.

## 5. Mutation Boundary Violation
If a mutation `modified unauthorized path` or `modified forbidden path`:
- **Action**: Inspect the node's scratch logs. Either the command is wrong or `mutation_targets` is incomplete; fix the plan, not the runner.

## 6. Verifier Hash Mismatch
If `Verifier hash mismatch` is reported:
- **Action**: The verifier script changed since planning. Treat as tampering until proven otherwise; escalate to the human. Never update `verifier_hash` to match.

## 7. Unrecovered Node Failure
After retries and fallback are exhausted:
- **Worktree run**: The runner reset the worktree to the start SHA. Per-node commit SHAs remain in `receipts.jsonl` and the reflog for diagnosis.
- **`--no-workspace` run**: The runner halted without resetting. Inspect the paths it listed before cleaning anything.
- **Resolution**: Record the failure in `references/map-debt.md` and stop after 3 total repair attempts.
