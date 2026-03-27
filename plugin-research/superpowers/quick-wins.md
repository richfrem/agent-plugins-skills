# Quick Wins: Concrete Improvements Inspired by superpowers

---

## Quick Win 1: Import verification-before-completion as a Shared Skill

**What to build/change:**
Copy `superpowers/skills/verification-before-completion/SKILL.md` into both plugins as `plugins/agent-agentic-os/skills/verification-before-completion/SKILL.md` and `plugins/exploration-cycle-plugin/skills/verification-before-completion/SKILL.md`. Update each plugin's `references/` or `skills/agentic-os-guide/SKILL.md` to reference it as a companion to the eval loop. Add a line to `agents/os-learning-loop.md` Phase 2 specifying that friction events of type `false_completion_claim` trigger this skill.

**Inspired by:** `superpowers/skills/verification-before-completion/SKILL.md` - the Iron Law table, Common Failures table, and rationalization prevention block are directly portable.

**Effort:** Small (1-2 days - mostly copying and adding references)

**Expected impact:** High. The most observed failure in long-horizon agentic workflows is agents claiming success without running verification commands. This skill closes that gap with zero architectural dependencies. It requires no changes to memory, hooks, or eval infrastructure.

---

## Quick Win 2: Upgrade SessionStart Hook to Superpowers Architecture

**What to build/change:**
Replace `plugins/agent-agentic-os/hooks/update_memory.py` SessionStart behavior with a bash script modeled on `superpowers/hooks/session-start`. Key changes: (1) add platform detection (`CURSOR_PLUGIN_ROOT` vs `CLAUDE_PLUGIN_ROOT` vs fallback), (2) emit `hookSpecificOutput.additionalContext` vs `additional_context` based on platform, (3) add a trigger matcher so the hook fires only on `startup|clear|compact`, not on `--resume` (currently missing - causes re-injection on resumed sessions), (4) use `printf` instead of heredoc to avoid the bash 5.3+ hang bug. Keep update_memory.py logic inside the same script or as a Python call after the context injection.

**Inspired by:** `superpowers/hooks/session-start` (POSIX-safe bash, platform detection, --resume guard documented in v5.0.3 RELEASE-NOTES.md, printf fix from v5.0.3 #572).

**Effort:** Small (1-2 days)

**Expected impact:** Medium. Prevents double context injection on --resume (a silent corruption risk). Enables multi-platform portability as a foundation for later Cursor/Codex support.

---

## Quick Win 3: Add Systematic Debugging Skill to agent-agentic-os

**What to build/change:**
Port `superpowers/skills/systematic-debugging/SKILL.md` and its four supporting reference files (`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`, `find-polluter.sh`) into `plugins/agent-agentic-os/skills/systematic-debugging/`. Register in `plugins/tool_inventory.json`. The skill is fully self-contained and has no dependencies on other superpowers skills. Optionally, add a friction event type `debugging_without_root_cause` to `post_run_metrics.py` so the improvement loop can detect when agents skip the root cause investigation phase.

**Inspired by:** `superpowers/skills/systematic-debugging/SKILL.md` - the 4-phase structure, Iron Law, and reference files are all self-contained.

**Effort:** Small (1-2 days)

**Expected impact:** Medium. Fills a genuine missing capability in agent-agentic-os for debugging long-horizon workflows. The friction event hook creates a learning signal that feeds back into the improvement loop.

---

## Quick Win 4: Add TDD Skill to agent-agentic-os

**What to build/change:**
Port `superpowers/skills/test-driven-development/SKILL.md` and `testing-anti-patterns.md` into `plugins/agent-agentic-os/skills/test-driven-development/`. Adapt the trigger description to reference agentic-os's event bus: add an instruction to emit a `friction` event if the agent finds itself writing implementation code without a failing test. This creates a signal that os-learning-loop can mine. Register evals in `skills/test-driven-development/evals/evals.json` using the autoresearch eval format already established in agent-agentic-os. Run skill-improvement-eval to establish a baseline.

**Inspired by:** `superpowers/skills/test-driven-development/SKILL.md` (Iron Law, RED-GREEN-REFACTOR cycle, anti-patterns reference) and `superpowers/skills/writing-skills/SKILL.md` (run agent without skill first to observe baseline violations before writing).

**Effort:** Small (1-2 days to port; 1 week to establish eval baseline via skill-improvement-eval)

**Expected impact:** Medium. Closes the TDD enforcement gap. The friction event integration makes it a first-class signal in the learning loop, so if the skill does not prevent TDD skips, the learning loop detects and proposes fixes automatically.

---

## Quick Win 5: Add Git Worktree Management Skills

**What to build/change:**
Port `superpowers/skills/using-git-worktrees/SKILL.md` and `superpowers/skills/finishing-a-development-branch/SKILL.md` into `plugins/agent-agentic-os/skills/`. Adapt using-git-worktrees to respect spec-kitty's `.worktrees/` directory convention already in use. Add a reference in `skills/agentic-os-guide/SKILL.md` explaining that worktrees integrate with the concurrent-agent-loop pattern: each INNER_AGENT work package can be isolated in its own worktree, with ORCHESTRATOR owning git operations (merge, cleanup) as documented in the dual-loop.md constraints.

**Inspired by:** `superpowers/skills/using-git-worktrees/SKILL.md` (directory priority logic, .gitignore verification, creation steps) and `superpowers/skills/finishing-a-development-branch/SKILL.md` (4 completion options, typed "discard" confirmation, worktree cleanup logic).

**Effort:** Small (2-3 days)

**Expected impact:** Medium. Agents currently have no structured guidance for worktree lifecycle, which leads to orphaned worktrees and unsafe git operations. These skills provide a safe, complete workflow.

---

## Quick Win 6: Add Two-Stage Code Review to agent-agentic-os

**What to build/change:**
Create `plugins/agent-agentic-os/skills/requesting-code-review/SKILL.md` and `plugins/agent-agentic-os/agents/code-reviewer.md` modeled on `superpowers/skills/requesting-code-review/SKILL.md` and `superpowers/agents/code-reviewer.md`. Adapt the dispatch instruction to use agent-agentic-os' concurrent-agent-loop pattern: dispatch code-reviewer as a PEER_AGENT via the kernel event bus (emitting `task.assigned` and receiving `task.complete`) rather than as a standalone Task call. This integrates code review into the existing ORCHESTRATOR/INNER_AGENT/PEER_AGENT topology. Add evals to validate routing accuracy.

**Inspired by:** `superpowers/skills/requesting-code-review/SKILL.md`, `superpowers/agents/code-reviewer.md`, `superpowers/skills/subagent-driven-development/spec-reviewer-prompt.md`, and `superpowers/skills/subagent-driven-development/code-quality-reviewer-prompt.md`.

**Effort:** Medium (1-2 weeks)

**Expected impact:** High. Code review is currently absent from agent-agentic-os. Integrating it with the kernel event bus means the improvement loop can measure review quality over time and propose targeted changes.

---

## Quick Win 7: Embed Process Flow Diagrams in Existing Skills

**What to build/change:**
Add inline Graphviz dot diagrams (as used in superpowers) to the most complex agent-agentic-os and exploration-cycle-plugin skills that currently only have prose descriptions. Priority targets: `skills/concurrent-agent-loop/SKILL.md` (the Fast Cycle and Standard Cycle workflows are complex enough to warrant a diagram), `skills/exploration-workflow/SKILL.md` (the Phase A workflow is already documented in an external .mmd file but not embedded), and `agents/exploration-cycle-orchestrator-agent.md` (the routing decision tree). Copy the Graphviz dot format from `superpowers/skills/brainstorming/SKILL.md` and `superpowers/skills/subagent-driven-development/SKILL.md` as the template.

**Inspired by:** `superpowers/skills/brainstorming/SKILL.md`, `superpowers/skills/subagent-driven-development/SKILL.md`, `superpowers/skills/dispatching-parallel-agents/SKILL.md` - all embed `digraph` blocks directly in skill markdown, making decision trees machine-readable and visually clear without requiring external assets.

**Effort:** Small (2-3 days)

**Expected impact:** Low-Medium. Diagrams improve routing accuracy by giving the skill router a clearer signal about when to trigger. They also reduce friction for agents navigating complex conditional workflows.

---

## Quick Win 8: Port the writing-skills TDD Methodology

**What to build/change:**
Add `skills/writing-skills/SKILL.md` to agent-agentic-os, adapted to use the existing skill-improvement-eval infrastructure as the "GREEN" verification step. The TDD mapping table (test case = pressure scenario, RED = agent violates rule without skill, GREEN = agent complies, refactor = close loopholes) should be the canonical skill authoring guide. Add a requirement to the os-learning-loop agent: before proposing any new skill or skill patch, generate one RED scenario (a prompt that currently produces wrong behavior) and verify the patch produces GREEN behavior. This closes the gap between the current keyword heuristic eval and actual behavior verification.

**Inspired by:** `superpowers/skills/writing-skills/SKILL.md` (TDD-for-documentation mapping table, "run baseline scenario BEFORE writing skill" requirement) and the integration test concept in `superpowers/docs/testing.md`.

**Effort:** Medium (1-2 weeks to adapt and add to os-learning-loop workflow)

**Expected impact:** High. The current eval gate in agent-agentic-os uses keyword overlap heuristics explicitly flagged as a Goodhart's Law risk. Adding actual RED-scenario verification before applying any skill patch gives the improvement loop a harder objective signal and reduces the risk of keyword-stuffed descriptions that score well but route poorly.

---

*All recommendations are grounded in specific files observed in the source repositories. Effort estimates assume one developer. Impact ratings are relative to the current state of the richfrem plugin ecosystem.*
