# Pre-Flight Environment Check

Run this check silently at the start of every new exploration session (Block 0 of the workflow). Do not surface results to the expert unless something is missing that affects the session.

## Checks

### 1. Isolation capability
- Confirm the `os-control-worktree` skill resolves in the current host.
- **If missing and the session type is Greenfield:** warn once and continue in `direct` mode (no isolated workspace). See the isolation rules in the Phase 3 reference of `building-interactive-prototypes`.
- **If missing and the session type is Brownfield:** stop before any Phase 3 work and tell the expert that building into an existing codebase needs an isolated workspace.
- **If missing and the session type is Analysis/Docs or Spike:** warn once, then continue; isolation is not required for non-build sessions.

### 2. Dispatch strategy availability
Check the chosen strategy (the dashboard's `**Dispatch Strategy:**`):
- `cli-agent` backends (copilot, agy, claude, codex, local): confirm through the `cli-agent` skill that the backend you intend to use is installed and authorized.
- `claude-subagents`, `direct`: always available.
- If the chosen strategy is unavailable, fall back to `direct` and tell the expert: "The [strategy] strategy isn't available in this environment. I'll handle everything directly in this session."

### 3. Exploration directory
- Check that `exploration/` exists or can be created. If the project root is not writable, stop and report.

## Outcome

All checks pass: proceed silently. Any check fails: surface one clear message, then stop or fall back as specified. Record the resolved dispatch strategy in the dashboard `**Dispatch Strategy:**` field.
