# Acceptance Criteria: Agent Swarm

## 1. Execution Boundary Constraints
- [ ] Orchestrator does NOT execute the payload commands itself. It strictly maps the jobs and invokes `./swarm_run.py`.
- [ ] The swarm partition strategy ensures that no two workers are modifying the same source code file simultaneously.

## 2. Resiliency & Scale
- [ ] The orchestrator implements the `--resume` flag on large batches to protect against partial system failures.
- [ ] The orchestrator strictly limits Copilot workers to `2` to prevent throttling, while allowing higher limits for Gemini/Claude.

## 3. Protocol Fidelity
- [ ] Target logic relies purely on injected shell post-commands and input passing without depending on the sub-agents having complex filesystem context.
