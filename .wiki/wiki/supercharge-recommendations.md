---
concept: supercharge-recommendations
source: research-docs
source_file: superpowers/supercharge-recommendations.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.466820+00:00
cluster: superpowers
content_hash: b9754c0671d82845
---

# Supercharge Recommendations

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Supercharge Recommendations

---

## Decision A: Pivot to superpowers

### What You Gain

- A complete, tested end-to-end development workflow (brainstorm -> plan -> subagent-driven execution -> review -> merge) that works out of the box for any software task.
- First-class multi-platform support: Cursor, Codex, OpenCode, Gemini CLI, Windows - all handled.
- Systematic debugging, TDD enforcement, and verification-before-completion as mandatory workflow disciplines applied to every task.
- Two-stage code review with independent spec-reviewer and quality-reviewer subagents that read code independently.
- A community (Discord, GitHub contributors, sponsor ecosystem) that is actively bug-testing and regressing real issues.
- git worktree management and branch completion as an integrated, safe workflow.
- The writing-skills TDD-for-documentation approach with actual integration tests that run real Claude Code sessions.

### What You Lose

- All of agent-agentic-os: three-tier persistent memory, eval-gated self-improvement loop, friction event capture, improvement ledger, background agent separation, multi-agent locking. The session-to-session learning flywheel disappears entirely.
- All of exploration-cycle-plugin: structured requirements capture (BRD, user stories, business workflows), cheap-CLI dispatch architecture, audience-targeted handoffs with Reader Testing, prototype-led discovery, real iteration data (evals/results.tsv).
- spec-kitty integration path: if the project already uses spec-kitty's SDD lifecycle, superpowers runs a parallel workflow that may conflict with or duplicate it.
- Cross-repo agent coordination (AGENT_COMMS.md pattern, UPSTREAM/LAB dual-session) has no equivalent in superpowers.

### Migration Path

1. Install superpowers alongside existing plugins (non-destructive).
2. Remove hooks/update_memory.py and hooks/session_start.py from richfrem plugins - they conflict with superpowers' session injection.
3. Port any project-specific CLAUDE.md conventions to superpowers' user instructions override mechanism.
4. Rebuild the exploration phase using only brainstorming skill (lossy: no BRD, no user stories, no cheap-CLI dispatch).
5. Accept that the learning flywheel disappears and skill improvement reverts to manual authoring.

### Conditions Where This Makes Sense

- The primary pain is "we can't build software reliably from idea to PR without deviating from the plan."
- The project is primarily single-session or short-horizon (days not weeks).
- Multi-platform portability is a hard requirement.
- The team does not need spec-kitty integration.
- The exploration phase is simple enough that brainstorming covers it.

---

## Decision B: Keep richfrem Plugins but Supercharge Them

### Which superpowers Patterns to Import (Priority Order)

**Priority 1 - Verification-Before-Completion (2-3 days)**

Import `skills/verification-before-completion/SKILL.md` verbatim or nearly verbatim into agent-agentic-os and exploration-cycle-plugin as a shared skill. This closes the most dangerous gap in both plugins immediately: agents claiming completion without evidence. The skill is self-contained, has no dependencies on other superpowers skills, and addresses a failure mode that is directly observable in long-horizon agentic workflows.

**Priority 2 - Session-Start Context Injection Pattern (1-2 days)**

Adopt the superpowers session-start hook architecture: read a using-superpowers equivalent at startup and inject it as additionalContext, with platform detection (Claude Code vs Cursor vs other) and --resume guard. Current richfrem hooks are simpler and more fragile. The bash script in `hooks/session-start` with proper JSON escaping, platform detection, and POSIX-safe implementation is a drop-in improvement for agent-agentic-os' hooks/update_memory.py approach.

**Priority 3 - Two-Stage Code Review Subagents (1-2 weeks)**

Build requesting-code-review and receiving-code-review skills modeled on superpowers' patterns. The code-

*(content truncated)*

## See Also

- [[open-recommendations-tracker]]
- [[sme-delivery-model-options-analysis-recommendations]]
- [[open-recommendations-tracker]]
- [[enhancement-recommendations-os-eval-runner-os-skill-improvement]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/supercharge-recommendations.md`
- **Indexed:** 2026-04-17T06:42:10.466820+00:00
