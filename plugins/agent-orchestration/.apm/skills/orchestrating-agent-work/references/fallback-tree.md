# Procedural Fallback Tree: orchestrating-agent-work

## General
### 1. Sub-Agent Execution Timeout or Unresponsive CLI Engine
If an invoked sub-agent or CLI backend process (`claude`, `codex`, `copilot`, `agy`) hangs or times out:
- **Action**: Terminate the hanging process. Check connection and local daemon health. Fall back to the next available tier engine or reduce batch size.
- **Guardrail**: Never leave orphaned background child processes running after timeout.

### 2. Structured Output or Evaluation Parsing Failure
If the downstream agent or evaluator fails to produce expected JSON, YAML, or evaluation schema:
- **Action**: Do not guess or fabricate structured results. Re-prompt with strict schema validation instructions or trigger fallback extractor script.
- **Guardrail**: If two consecutive retries fail parsing, halt and escalate to human supervisor.

### 3. Loop Convergence Stagnation (Oscillation / Max Iterations)
If iterative loops (`dual-loop`, `red-team-review`) oscillate between identical revisions without converging:
- **Action**: Enforce hard iteration limit (max 3 cycles). Break execution loop immediately upon 3rd failure.
- **Resolution**: Record failure state and diffs in Map Debt and escalate for architectural clarification.

### 4. Context Window Saturation
If prompt expansion causes token exhaustion during recursive orchestration or swarm fan-out:
- **Action**: Trim conversational transcript. Retain only invariant rules, task specification, and lean verification contract before re-dispatching.

### 5. Security & Isolation Violation (Autonomous Git Operation)
If an inner loop sub-agent attempts autonomous git commit, branch checkout, or destructive operations:
- **Action**: Terminate sub-agent immediately. Strip tool access and re-dispatch in isolated read-only mode (`--isolated`).

## Routing and closure
### 1. Ambiguous Routing Signal
If the user's prompt (e.g., "Fix it") does not map cleanly to Research (Pattern 1), Review (Pattern 2), Execution (Pattern 3), or Parallelism (Pattern 4):
- **Action**: Do not guess. Default to Pattern 1 (Learning Loop) to synthesize the requirement. Ask the user 1 clarifying question to determine if code execution or review is actually needed.

### 2. Inner Loop Crashes (Timeout/Dependency)
If the delegated inner loop (whether dual-loop or swarm) crashes abruptly without returning a completed artifact or a status:
- **Action**: The Orchestrator reclaims control. It does NOT enter an infinite wait. It assesses the terminal output or log of the crash, generates a Correction Packet containing the crash trace, and attempts to re-delegate.

### 3. Sub-Agent Process Fails to Start
If `agent_orchestrator.py` or the environment fails to spawn the requested CLI subagent:
- **Action**: Present the generated Task Packet to the user directly in chat. Ask the user to instantiate the environment (e.g., another terminal window) and act as the bridge manually. 

### 4. Retrospective Cannot Be Generated
If the loop completes but the friction logs are empty or the agent lacks memory of what actually happened during the execution:
- **Action**: Generate an explicit 'Null Retrospective' noting that execution traces were lost. Prompt the user to confirm closure before passing control to the Primary Agent for the seal sequence.

## Dual-loop
### 1. Inner Loop Refuses NO GIT Constraint
If the inner loop agent (e.g., Copilot or a sub-process) repeatedly attempts to commit code or run git commands despite instructions:
- **Action**: The Orchestrator (Outer Loop) must intervene, revert the git state, and generate a Correction Packet explicitly citing a Protocol Violation. Instruct the Inner Loop to only edit the files and STOP.

### 2. Inner Loop Modifies Out-of-Scope Files
If delta verification shows the Inner Loop modified files unlisted in the Strategy Packet:
- **Action**: Fail the verification gate. Revert the out-of-scope files. Generate a Correction Packet warning the Inner Loop of scope creep. The Outer Loop must never auto-merge unauthorized filesystem modifications.

### 3. Test Suite Missing or Broken
If the Outer Loop attempts to mechanical verify via tests, but the repository has no tests or they were already broken:
- **Action**: The Outer Loop must manually run the code or instantiate a new, minimal regression test specific to the Strategy Packet to verify the behavior before merging.

### 4. Inner Loop Stuck in Correction Loop (Max Iterations)
If the Inner Loop has received 3+ Correction Packets and is still failing the acceptance criteria:
- **Action**: Break the loop. The Orchestrator reclaims the task. Refactor the Strategy Packet (it was likely too broad or ambiguous) or swap the Inner Loop engine for a higher reasoning model (e.g., Opus instead of Haiku).

## Agent swarm
### 1. Rate Limit / Authentication Failure (Copilot)
If `./swarm_run.py --engine copilot` throws repeated 429s or authentication errors despite having a valid token:
- **Action**: Check the `--workers` flag. Overriding concurrency past `2` triggers GitHub's abuse filters which manifest as random auth failures. Reduce to `--workers 2`.
- **Secondary Action**: Ensure the token was loaded via `source ~/.zshrc`, not `gh auth token` (which lacks Copilot scopes).

### 2. Shared Cache / Concurrent Write Corruption
If the parallel workers are writing to a single JSON file and it becomes malformed or misses entries:
- **Action**: The `post_cmd` script lacks atomic locking. Temporarily switch to `--workers 1` to run the batch sequentially. For a permanent fix, rewrite the writer script to use `fcntl.flock` for atomic file operations. 

### 3. Worker Timeout Reached
If the `scripts/swarm_run.py` script reports `Timeout` for specific files:
- **Action**: The work package is too large for the configured CLI agent. If using `haiku` or `gpt-5-mini`, re-run the job explicitly passing the failed files but bumping the `--timeout` parameter or switching to a heavier engine (`--engine claude`).

### 4. Checkpoint State File Corrupted
If the `--resume` flag fails because `.swarm_state_<job>.json` has phantom entries not matching the actual file system outputs:
- **Action**: Run the checkpoint reconciliation snippet from `./SKILL.md`. This clears the `completed` array of any files that aren't physically present in the output store, allowing the resume to proceed cleanly.

## Graph execution
### 1. Manifest Rejected at Startup
If the runner exits 1 with `Manifest schema validation failed` or `Manifest topology validation failed`:
- **Action**: Do not edit the manifest to force it through. Return it to graph planning ([graph-planning.md](graph-planning.md)) with the exact error lines.
- **Guardrail**: A manifest edited after approval changes its SHA256; the old `--expect-manifest-sha256` value must then be re-approved, never recomputed by the executing agent.

### 2. Manifest SHA Mismatch
If the runner reports `Manifest SHA256 mismatch`:
- **Action**: Halt. The manifest on disk is not the one that was approved. Escalate to the human who approved it.

### 3. Approval Prompt Rejected in a Non-Interactive Shell
If `--approval prompt` prints `Non-interactive stdin detected`:
- **Action**: Expected when an agent runs the command. Ask the human to run it in their own terminal (`! <command>`), or use `--approval none` with a human-approved manifest SHA and an approval gate.
- **Guardrail**: Never pipe `y` into the runner or fabricate approval.

### 4. Barrier or Immutability Failure
If a read node `modified tracked or untracked files` or `moved HEAD`:
- **Action**: The node is not read-only. Send it back to planning as a `sequential_mutation` with `mutation_targets`, or move its writes into `$GRAPH_SCRATCH_DIR`.

### 5. Mutation Boundary Violation
If a mutation `modified unauthorized path` or `modified forbidden path`:
- **Action**: Inspect the node's scratch logs. Either the command is wrong or `mutation_targets` is incomplete; fix the plan, not the runner.

### 6. Verifier Hash Mismatch
If `Verifier hash mismatch` is reported:
- **Action**: The verifier script changed since planning. Treat as tampering until proven otherwise; escalate to the human. Never update `verifier_hash` to match.

### 7. Unrecovered Node Failure
After retries and fallback are exhausted:
- **Worktree run**: The runner reset the worktree to the start SHA. Per-node commit SHAs remain in `receipts.jsonl` and the reflog for diagnosis.
- **`--no-workspace` run**: The runner halted without resetting. Inspect the paths it listed before cleaning anything.
- **Resolution**: Record the failure in the repository `map-debt.md` ledger and stop after 3 total repair attempts.

## Red-team review
### 1. Manifest Context is Too Large
If `bundling-context` generates a file too massive for the Red Team agent's context window:
- **Action**: Refine the `manifest.json`. Exclude massive unstructured logs or irrelevant boilerplate. Re-run the bundler. Adhere to the principle of "minimum viable context" for the reviewer.

### 2. Reviewer Persona is Missing
If instructed to use a specific persona but the file cannot be found, ask the user to
supply a system prompt directly or install an agent persona plugin.
The `qa-expert` and `security-auditor` persona stubs have been removed — supply your own
system prompt for specialized review agents.

### 3. Continuous Review Deadlock
If the Red Team agent rejects the research 3 or more times consecutively for the same core issue that cannot be resolved:
- **Action**: Break the loop. Bring the deadlocked specific disagreement to the Orchestrator/User for a tie-breaking executive decision. 

### 4. Unactionable Feedback
If the feedback returned from the reviewer is vague (e.g., "This isn't good enough"):
- **Action**: Do not loop back to research yet. Prompt the reviewer agent/human to quantify the failure using the Severity-Stratified schema (Critical/Moderate/Minor) with specific file/line references.
