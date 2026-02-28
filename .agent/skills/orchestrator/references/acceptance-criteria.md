# Agent Orchestrator Acceptance Criteria

To pass Open Standard certification, the `agent-orchestrator` plugin must dynamically instantiate hierarchical loops independently of global `.agent/` state tracking directories.

## Core Rules
1. Must natively execute the `scripts/agent_orchestrator.py` script directly without legacy slash-command wrappers.
2. Must not assume the existence of external branch dependencies or global templates.
3. Must generate `handoffs/` and `retros/` dynamically in the active Project Runtime.
4. Orchestrator must be able to act autonomously to verify output against provided prompt packets utilizing the `verify` command.
