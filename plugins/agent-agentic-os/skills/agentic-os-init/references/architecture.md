# Agentic OS Initialization Architecture

The initialization sequence uses the Sub-Agent Orchestration pattern (specifically `agentic-os-setup.md`) to manage the complexity of scaffolding an OS.

## Why a Sub-Agent?
The `agentic-os-init` skill is dense. If a user asks "setup an OS", loading the full scaffolding logic into the primary context window is wasteful. Instead, we use `agentic-os-setup` to create an isolated context.

## State Transitions
1. **Discovery**: The agent interviews the user, understanding the project environment (Python, Node, generic).
2. **Merge vs Overwrite**: If `CLAUDE.md` exists, the agent MUST use a safe append strategy. The architecture strictly forbids destructively overwriting pre-existing user prompt logic.
3. **Hook Wiring**: `hooks.json` mapping is mandatory. The architecture relies on `SessionStart` and `PostToolUse` firing `update_memory.py` to bridge stateless sessions. Init is responsible for making sure this is wired cleanly.