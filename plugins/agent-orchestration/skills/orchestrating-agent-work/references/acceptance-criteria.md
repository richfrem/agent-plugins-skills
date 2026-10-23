# Acceptance Criteria: orchestrating-agent-work

## Strategy selection
- [ ] Known dimensions are derived from the caller's brief; at most 4 diagnostic questions, one per turn, each with a recommended option.
- [ ] `scripts/select_strategy.py` makes the selection deterministically from the answers.
- [ ] The decision is written to `select-loop-strategy-decision.json` (and `.md`) in the task directory, confirmed or overridden by the human, with any override recorded.
- [ ] Selection never starts execution by itself; it names the next step and its input path.

## Routing and closure
To pass Open Standard certification, the `agent-orchestrator` plugin must dynamically instantiate hierarchical loops independently of global `.agents/` state tracking directories.

### Core Rules
1. Must natively execute the `./agent_orchestrator.py` script directly without legacy slash-command wrappers.
2. Must not assume the existence of external branch dependencies or global templates.
3. Must generate `handoffs/` and `retros/` dynamically in the active Project Runtime.
4. Orchestrator must be able to act autonomously to verify output against provided prompt packets utilizing the `verify` command.

## Dual-loop
### 1. Strategy Packet Fidelity
- [ ] Outer Loop ALWAYS generates an explicit, written markdown Strategy Packet containing constraints, file paths, and the "NO GIT" mandate before delegating.
- [ ] The Inner Loop is only fed the packet and necessary files, drastically isolating its context window.

### 2. Anti-Simulation Checks
- [ ] Outer Loop NEVER marks a task "Done" without manually checking the file deltas and mechanically running lint/test commands.
- [ ] "Assume it works" behavior results in an immediate audit failure.

### 3. Structured Correction
- [ ] Failed verifications are NEVER manually patched by the Outer Loop without feedback, unless tagged as `MINOR` (naming/style).
- [ ] Critical and Moderate failures are routed back to the Inner Loop via structured Markdown Correction Packets citing the exact failure logs.

## Agent swarm
### 1. Execution Boundary Constraints
- [ ] Orchestrator does NOT execute the payload commands itself. It strictly maps the jobs and invokes `../scripts/swarm_run.py`.
- [ ] The swarm partition strategy ensures that no two workers are modifying the same source code file simultaneously.

### 2. Resiliency & Scale
- [ ] The orchestrator implements the `--resume` flag on large batches to protect against partial system failures.
- [ ] The orchestrator strictly limits Copilot workers to `2` to prevent throttling, while allowing higher limits for Gemini/Claude.

### 3. Protocol Fidelity
- [ ] Target logic relies purely on injected shell post-commands and input passing without depending on the sub-agents having complex filesystem context.

## Graph planning
### 1. Trigger Verification
- [ ] Triggers on requests to design, architect, or compile a multi-step DAG, execution graph, or `graph-manifest.json`.
- [ ] Does **not** trigger for executing an existing manifest (that is graph execution ([graph-execution.md](graph-execution.md))), single-file fixes, or strategy selection (strategy selection ([strategy-selection.md](strategy-selection.md))).

### 2. Interview Discipline
- [ ] Reads caller briefs, specs, and any `--decision <path>` record before asking questions.
- [ ] Asks only about unresolved topology gaps: fan-out candidates, join barriers, verifier scripts, mutation targets, failure escalation.

### 3. Manifest Correctness
- [ ] Manifest passes `python3 scripts/validate_manifest.py <manifest>` with zero errors.
- [ ] Manifests intended for `--approval none` also pass with `--check-approval-none`.
- [ ] Every `command_or_eval` is an executable shell command (model tiers are invoked through a CLI inside the command, never as a bare prompt).
- [ ] Every `sequential_mutation` declares `mutation_targets`; no bare `*` or `**` targets.
- [ ] Mutations form one linear chain; fallbacks have the same type as their primary and the same preceding mutations.
- [ ] External or irreversible actions set `reversible: false` and depend on the approval gate.
- [ ] `verifier_hash` values are computed from the script file named in the command (or the command string when it names no file).

### 4. Handoff
- [ ] A Mermaid diagram of the DAG is presented alongside the manifest.
- [ ] Handoff states the manifest SHA256 for `--expect-manifest-sha256` and the intended `--approval` mode and workspace flag.

## Graph execution
### 1. Trigger Verification
- [ ] Triggers on requests to run, execute, or resume a compiled `graph-manifest.json`.
- [ ] Does **not** trigger for designing a new graph (that is graph planning ([graph-planning.md](graph-planning.md))), single-agent delegation, or swarm batch jobs.

### 2. Startup Gates
- [ ] Runner validates schema and topology before any node executes; invalid manifests exit 1 with no side effects.
- [ ] Mutation or irreversible graphs under `--approval none` require `--expect-manifest-sha256` and a leading `role: "approval"` verifier gate.
- [ ] Mutation graphs refuse `--no-workspace` and run only in `--worktree` / `--create-worktree` with a clean tree.

### 3. Execution Invariants
- [ ] Parallel reads never change HEAD or `git status`; any change fails the batch.
- [ ] Mutations run one at a time, touch only `mutation_targets`, never `forbidden_paths`, and never self-commit.
- [ ] The runner commits once per mutation that changed files; a no-op mutation succeeds without a commit.
- [ ] `verifier_hash` mismatches fail the node before it runs.

### 4. Failure Handling
- [ ] Retries reset mutation debris to the node's pre-run HEAD.
- [ ] Fallbacks run only when their own dependencies are complete and are recorded in `state.json` as `substituted_nodes`.
- [ ] Worktree runs roll back to the start SHA on unrecovered failure; `--no-workspace` runs halt without touching the checkout.

### 5. Evidence
- [ ] `receipts.jsonl` holds one line per attempt and survives rollback (anchored in `<git-common-dir>/graph-run/`).
- [ ] `state.json` records terminal status: `success`, `rolled_back`, or `halted`.
- [ ] The runner never pushes, merges, or deletes worktrees.

## Red-team review
### 1. Bundle Discipline
- [ ] Agent relies entirely on `bundling-context` and `manifest.json` to compile review packets, rather than manually `cat`ing files into prompts.
- [ ] Packets always include an explicit "Prompt" guiding the reviewer's focus.

### 2. Iteration Mandate
- [ ] Agent automatically parses the reviewer's verdict and correctly triggers the next loop iteration (Research vs Approval) based on that verdict.
- [ ] Agent refuses to manually override a negative or pending verdict to force an approval.

### 3. Delegation Limits
- [ ] As a specialized loop, it only manages the review cycle. It does not execute the actual implementation or dictate global repo state updates post-approval.
