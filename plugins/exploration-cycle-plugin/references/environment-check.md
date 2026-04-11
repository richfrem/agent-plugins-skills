# Pre-Flight Environment Check

Run this check silently at the start of every new exploration session (Block 0 in `exploration-workflow`).
Do not surface results to the SME unless something is missing that affects the session.

## Checks

### 1. superpowers plugin availability
- Confirm `superpowers:using-git-worktrees` resolves via the Skill tool.
- **If missing AND session type is Greenfield or Brownfield:**
  > "The orba/superpowers plugin is required for prototype isolation and TDD validation.
  > It looks like it isn't installed. Run: `uvx --from git+https://github.com/richfrem/agent-plugins-skills plugin-add richfrem/agent-plugins-skills`
  > Then restart the session."
  Stop. Do not proceed with Phase 3 work without superpowers.
- **If missing AND session type is Analysis/Docs or Spike:** Warn once, then continue — superpowers is not required for non-build sessions.

### 2. Dispatch strategy availability
- Check the chosen dispatch strategy (from dashboard `**Dispatch Strategy:**`):
  - `copilot-cli` → confirm `copilot` CLI is on the PATH (run `which copilot`)
  - `claude-subagents` → always available
  - `direct` → always available
- If chosen strategy is unavailable: fall back to `direct` mode and inform the SME:
  > "The [strategy] strategy isn't available in this environment. I'll handle everything directly in this session."

### 3. Exploration directory
- Check that `exploration/` exists or can be created.
- If the project root is not writable, stop and report.

## Outcome

If all checks pass: proceed silently with no output.
If any check fails: surface a single clear message, then either stop or fall back as specified above.
Record the resolved dispatch strategy in the dashboard `**Dispatch Strategy:**` field.
