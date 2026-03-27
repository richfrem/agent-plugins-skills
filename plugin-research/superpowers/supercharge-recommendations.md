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

Build requesting-code-review and receiving-code-review skills modeled on superpowers' patterns. The code-reviewer.md agent, spec-reviewer-prompt.md, and code-quality-reviewer-prompt.md are all portable. The two-stage review (spec compliance first, then quality) with independent reviewers that read code themselves addresses a real gap in the richfrem plugin set. This can run on top of the existing dual-loop coordination primitives in agent-agentic-os.

**Priority 4 - Brainstorming -> Writing-Plans -> Execution Pipeline (3-4 weeks)**

Build a connected skill pipeline modeled on superpowers' workflow: brainstorming with HARD-GATE, writing-plans with "No Placeholders" enforcement, subagent-driven-development with TodoWrite tracking. These skills can be authored using agent-agentic-os' skill-improvement-eval to gate quality, creating a virtuous cycle where the new skills benefit from the existing eval infrastructure.

**Priority 5 - TDD Enforcement Skill (1-2 days)**

Port `skills/test-driven-development/SKILL.md` and `testing-anti-patterns.md` directly. The Iron Law ("delete code written before tests"), the Red-Green-Refactor cycle with verification, and the anti-patterns reference are all self-contained and language-agnostic. This fills the gap where neither richfrem plugin currently enforces testing discipline.

**Priority 6 - Git Worktree Management (1-2 days)**

Port `skills/using-git-worktrees/SKILL.md` and `skills/finishing-a-development-branch/SKILL.md`. These are self-contained and complement the spec-kitty worktree protocol. using-git-worktrees' directory priority logic (.worktrees vs worktrees), .gitignore safety verification, and integration with branch completion are directly useful for the richfrem plugin ecosystem.

**Priority 7 - Writing-Skills with TDD Methodology (2-3 days)**

Port `skills/writing-skills/SKILL.md` and adapt it to use agent-agentic-os' skill-improvement-eval as the eval mechanism. The RED-GREEN-REFACTOR mapping (test case = pressure scenario, RED = agent violates rule without skill, GREEN = agent complies) is more rigorous than the current autoresearch keyword heuristic. Adding actual integration test scripts (modeling tests/claude-code/) would give the eval gate a harder objective signal.

### New Skills to Build

- **systematic-debugging** equivalent: a 4-phase root-cause-first debugging skill that enforces "no fixes without root cause investigation." Currently absent from both richfrem plugins.
- **dispatching-parallel-agents** formalization: agent-agentic-os' concurrent-agent-loop covers this but at the architecture level. A practical skill focused on "here are 3 independent test failures, dispatch one agent per domain" would be immediately usable.

---

## Decision C: Hybrid Approach

### Adopt from superpowers As-Is

| Component | Rationale |
|---|---|
| `skills/verification-before-completion/SKILL.md` | Zero dependencies, high value, closes dangerous gap immediately |
| `skills/test-driven-development/SKILL.md` + `testing-anti-patterns.md` | Self-contained, language-agnostic, complementary to existing eval loop |
| `skills/receiving-code-review/SKILL.md` | Self-contained, addresses behavior gap not covered by richfrem plugins |
| `skills/systematic-debugging/SKILL.md` + reference files | Self-contained, fills a genuine missing capability |
| `hooks/session-start` shell script pattern (adapt for richfrem) | Better platform handling, POSIX-safe, --resume guard |
| `skills/using-git-worktrees/SKILL.md` | Self-contained, complements spec-kitty worktree protocol |
| `skills/finishing-a-development-branch/SKILL.md` | Self-contained, complements worktree management |

### Keep from richfrem Plugins

| Component | Rationale |
|---|---|
| `agent-agentic-os` memory hierarchy (all three tiers) | No equivalent in superpowers; critical for long-horizon work |
| `agent-agentic-os` eval-gated self-improvement loop | Unique architectural differentiator; superpowers has nothing like it |
| `agent-agentic-os` concurrent-agent-loop + kernel.py | Best multi-agent coordination protocol in the set |
| `agent-agentic-os` improvement ledger + longitudinal tracking | Provides flywheel data that superpowers cannot generate |
| `exploration-cycle-plugin` cheap-CLI dispatch + dispatch.py | Correct architecture for high-volume structured capture |
| `exploration-cycle-plugin` multi-modal requirements capture | No equivalent in superpowers; brainstorming is too shallow for BRDs/stories |
| `exploration-cycle-plugin` exploration-handoff with Reader Testing | Unique audience-targeted validation mechanism |
| `exploration-cycle-plugin` real evals/results.tsv | Ground truth for the exploration workflow that superpowers lacks |

### Build to Fill Remaining Gaps

- **writing-plans equivalent** that integrates with spec-kitty SDD lifecycle rather than replacing it.
- **requesting-code-review + code-reviewer subagent** modeled on superpowers' pattern but hooked into agent-agentic-os' eval infrastructure.
- **brainstorming equivalent** that connects to exploration-cycle-plugin's handoff artifacts rather than being a standalone design session.

---

## Clear Opinionated Recommendation

**Decision C: Hybrid approach, with selective imports from superpowers.**

Here is the reasoning.

**Do not pivot to superpowers.** The pivot loses things that superpowers cannot replace and does not plan to build. A project running long-horizon, multi-session agentic workflows across days or weeks without memory persistence, without a self-improvement loop, and without an audit trail will degrade silently. agent-agentic-os' memory hierarchy and eval-gated improvement loop are the right infrastructure for that class of problem. exploration-cycle-plugin's real iteration data (evals/results.tsv) represents genuine empirical grounding for the exploration workflow that would be expensive to recreate from scratch.

**Do not stand pat.** The gaps in the richfrem plugins are real and the superpowers solutions for them are good. Verification-before-completion, TDD enforcement, systematic debugging, git worktree management, and two-stage code review are well-designed, self-contained, and portable. There is no reason to build these from scratch when they exist and work.

**Execute the hybrid in this order:**

1. Import verification-before-completion immediately. It closes the most dangerous operational gap - agents claiming success without evidence - and has no dependencies on any other migration step.

2. Adopt the session-start hook architecture from superpowers (platform detection, POSIX-safe bash, --resume guard). This improves the existing richfrem hook infrastructure without changing skill content.

3. Import TDD enforcement and systematic debugging. These are self-contained skill files that improve implementation quality for all workflows.

4. Import using-git-worktrees and finishing-a-development-branch. These complement spec-kitty's worktree protocol and give agents a complete branch lifecycle.

5. Build requesting-code-review and receiving-code-review modeled on superpowers but integrated with agent-agentic-os' eval loop and event infrastructure.

6. Build brainstorming -> writing-plans -> execution pipeline as richfrem-native skills that chain into the existing memory and eval infrastructure, connecting to exploration-cycle-plugin handoffs rather than bypassing them.

The resulting system will have: superpowers' development workflow discipline applied on top of richfrem's memory, learning loop, and exploration infrastructure. It will be more complex than superpowers alone, but it will handle long-horizon work that superpowers cannot. It will be more complete than the richfrem plugins alone, but it will have enforcement and verification mechanisms that they currently lack.

The test for whether the hybrid is working: after 10 sessions, the improvement ledger should show eval scores trending up on the imported skills, and the events.jsonl should show fewer verification failures and incomplete completions than before the imports.
