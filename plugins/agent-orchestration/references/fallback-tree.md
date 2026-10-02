# Procedural Fallback Tree: Agent Orchestration Loops

## 1. Sub-Agent Execution Timeout or Unresponsive CLI Engine
If an invoked sub-agent or CLI backend process (`claude`, `codex`, `copilot`, `agy`) hangs or times out:
- **Action**: Terminate the hanging process. Check connection and local daemon health. Fall back to the next available tier engine or reduce batch size.
- **Guardrail**: Never leave orphaned background child processes running after timeout.

## 2. Structured Output or Evaluation Parsing Failure
If the downstream agent or evaluator fails to produce expected JSON, YAML, or evaluation schema:
- **Action**: Do not guess or fabricate structured results. Re-prompt with strict schema validation instructions or trigger fallback extractor script.
- **Guardrail**: If two consecutive retries fail parsing, halt and escalate to human supervisor.

## 3. Loop Convergence Stagnation (Oscillation / Max Iterations)
If iterative loops (`dual-loop`, `learning-loop`, `co-pilot-loop`) oscillate between identical revisions without converging:
- **Action**: Enforce hard iteration limit (max 3 cycles). Break execution loop immediately upon 3rd failure.
- **Resolution**: Record failure state and diffs in Map Debt and escalate for architectural clarification.

## 4. Context Window Saturation
If prompt expansion causes token exhaustion during recursive orchestration or swarm fan-out:
- **Action**: Trim conversational transcript. Retain only invariant rules, task specification, and lean verification contract before re-dispatching.

## 5. Security & Isolation Violation (Autonomous Git Operation)
If an inner loop sub-agent attempts autonomous git commit, branch checkout, or destructive operations:
- **Action**: Terminate sub-agent immediately. Strip tool access and re-dispatch in isolated read-only mode (`--isolated`).