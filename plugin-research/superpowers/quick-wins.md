# Quick Wins: Concrete Improvements Inspired by superpowers

> **ADR Constraints Applied (revised after antigravity review)**
> All implementation paths comply with ADR-002 (hub-and-spoke scripts),
> ADR-003 (zero duplication / file-level symlinks only), and ADR-004
> (self-contained plugins at deploy time, cross-plugin symlinks in source).
> "Copy" only happens at install time via bridge_installer.py / npx skills add.

---

## Quick Win 1: Add verification-before-completion as a Canonical Skill

**What to build/change:**
Create a new dedicated plugin `plugins/agent-execution-disciplines/` to own
universal workflow execution skills canonically (verification, TDD, debugging,
code review). Canonicalize the first skill there:

```
plugins/agent-execution-disciplines/
  plugin.json
  skills/
    verification-before-completion/
      SKILL.md              <- single authoritative source
```

Do NOT put this SKILL.md inside `agent-agentic-os` or `exploration-cycle-plugin`.
Do NOT create a cross-plugin SKILL.md symlink -- ADR-001 Rule 1 restricts
cross-plugin symlinks to scripts that resolve inside the plugin's own boundary;
SKILL.md is an agent instruction file, not a script.

The correct multi-plugin access pattern per ADR-001 layer 3 is Agent Skill
Delegation: once `agent-execution-disciplines` is installed, any other installed
skill can reference `verification-before-completion` by name in its agent
instructions (e.g., "trigger the verification-before-completion skill") without
any cross-plugin symlinks at all.

Bridge-install the new plugin:
```bash
python ./bridge_installer.py --plugin plugins/agent-execution-disciplines
```

Also add a line to `agents/os-learning-loop.md` Phase 2: friction events of type
`false_completion_claim` trigger this skill. Register in `plugins/tool_inventory.json`.

**Inspired by:** `superpowers/skills/verification-before-completion/SKILL.md` -
the Iron Law table, Common Failures table, and rationalization prevention block.

**Effort:** Small (under 2 hours - new plugin scaffold is minimal)

**Expected impact:** High. The most common failure in long-horizon agentic workflows
is agents claiming success without running verification commands. This skill closes
that gap, and the new `agent-execution-disciplines` plugin becomes the home for
QW3, QW4, QW5, and QW6 as well - one install gives all of them.

---

## Quick Win 2: Harden the SessionStart Hook (POSIX-safe wrapper around Python kernel)

**What to build/change:**
Do NOT replace `update_memory.py` with a bash script. The Python event bus
(`kernel.py`) must remain the state orchestrator. Instead, rewrite the bash
wrapper in `plugins/agent-agentic-os/hooks/` to be POSIX-safe and then invoke
the Python orchestrator with the resolved platform context:

1. Add platform detection (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback)
2. Add a trigger guard: fire only on `startup|clear|compact`, skip `--resume`
   (currently missing - causes re-injection on resumed sessions)
3. Use `printf` instead of heredoc to avoid the bash 5.3+ hang (confirmed bug
   in superpowers RELEASE-NOTES.md v5.0.3 fix #572)
4. Emit `hookSpecificOutput.additionalContext` vs `additional_context` based on
   detected platform
5. Pass the resolved `PLUGIN_ROOT` as an argument to `update_memory.py` / `kernel.py`
   so the Python layer is platform-aware without doing its own shell detection

**Inspired by:** `superpowers/hooks/session-start` (POSIX-safe bash, platform
detection, --resume guard, printf fix all documented in RELEASE-NOTES.md v5.0.3).

**Effort:** Small (2-4 hours)

**Expected impact:** Medium. Prevents double context injection on --resume (silent
corruption). Adds multi-platform portability as a foundation for Cursor/Codex support.

---

## Quick Win 3: Add Systematic Debugging Skill to agent-agentic-os

**What to build/change:**
Port `superpowers/skills/systematic-debugging/SKILL.md` and its reference files
(`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`,
`find-polluter.sh`) into the `agent-execution-disciplines` plugin scaffolded in
QW1, following ADR-003 structure:

```
plugins/agent-execution-disciplines/
  skills/systematic-debugging/
    SKILL.md
    references/
      root-cause-tracing.md        <- file-level symlink -> ../../../references/...
      defense-in-depth.md          <- file-level symlink -> ../../../references/...
      condition-based-waiting.md   <- file-level symlink -> ../../../references/...
    scripts/
      find-polluter.sh             <- file-level symlink -> ../../../scripts/...
  references/
    root-cause-tracing.md          <- real file (canonical source)
    defense-in-depth.md            <- real file
    condition-based-waiting.md     <- real file
  scripts/
    find-polluter.sh               <- real file (canonical source)
```

Register in `plugins/tool_inventory.json`. Optionally add friction event type
`debugging_without_root_cause` to `post_run_metrics.py` in `agent-agentic-os`
so the improvement loop detects when agents skip root cause investigation.

**Inspired by:** `superpowers/skills/systematic-debugging/SKILL.md` (4-phase
structure, Iron Law, reference files).

**Effort:** Small (2-4 hours)

**Expected impact:** Medium. Fills a genuine missing capability for debugging
long-horizon workflows. The friction event creates a learning signal for the loop.

---

## Quick Win 4: Add TDD Skill to agent-agentic-os

**What to build/change:**
Port `superpowers/skills/test-driven-development/SKILL.md` and
`testing-anti-patterns.md` into the `agent-execution-disciplines` plugin (QW1)
following ADR-003 (SKILL.md in skill dir, `testing-anti-patterns.md` at plugin root
with file-level symlink from the skill dir).

Adapt the trigger description: emit a `friction` event if the agent finds itself
writing implementation code without a failing test. Register evals in
`skills/test-driven-development/evals/evals.json` using the autoresearch eval
format already established in agent-agentic-os. Run `skill-improvement-eval` to
establish a baseline before shipping.

**Inspired by:** `superpowers/skills/test-driven-development/SKILL.md` (Iron Law,
RED-GREEN-REFACTOR cycle, anti-patterns reference).

**Effort:** Small (2-4 hours to port; allow 1 additional week to establish eval
baseline via `skill-improvement-eval`)

**Expected impact:** Medium. Closes the TDD enforcement gap. Friction event
integration makes TDD skips a first-class signal in the learning loop.

---

## Quick Win 5: Add Git Worktree Management Skills to agent-agentic-os

**What to build/change:**
Port `superpowers/skills/using-git-worktrees/SKILL.md` and
`superpowers/skills/finishing-a-development-branch/SKILL.md` into the
`agent-execution-disciplines` plugin (QW1). Each skill is prose-only (no scripts),
so ADR-003 structure is trivial: SKILL.md in skill dir, no symlinks needed.

Adapt `using-git-worktrees` to respect spec-kitty's `.worktrees/` convention.
Add a cross-reference in `agent-agentic-os/skills/agentic-os-guide/SKILL.md`
explaining that worktrees integrate with concurrent-agent-loop: each INNER_AGENT
work package can be isolated in its own worktree, with ORCHESTRATOR owning git
operations. This cross-reference is a prose instruction (ADR-001 layer 3), not
a cross-plugin script call.

**Inspired by:** `superpowers/skills/using-git-worktrees/SKILL.md` (directory
priority logic, .gitignore verification) and
`superpowers/skills/finishing-a-development-branch/SKILL.md` (4 completion options,
typed "discard" confirmation, cleanup logic).

**Effort:** Small (2-4 hours)

**Expected impact:** Medium. Agents currently have no structured guidance for
worktree lifecycle. These skills prevent orphaned worktrees and unsafe git ops.

---

## Quick Win 6: Add Two-Stage Code Review to agent-agentic-os

**What to build/change:**
Add `skills/requesting-code-review/SKILL.md` and `agents/code-reviewer.md` to the
`agent-execution-disciplines` plugin (QW1), modeled on the superpowers equivalents.
Both are prose-only, so no scripts / ADR-003 symlinks required.

Adapt the dispatch instruction to use agent-agentic-os' concurrent-agent-loop:
dispatch code-reviewer as a PEER_AGENT via the kernel event bus (emitting
`task.assigned`, receiving `task.complete`) rather than as a standalone Task call.
This integrates code review into the existing ORCHESTRATOR / INNER_AGENT /
PEER_AGENT topology. Add evals to validate routing accuracy.

**Inspired by:** `superpowers/skills/requesting-code-review/SKILL.md`,
`superpowers/agents/code-reviewer.md`,
`superpowers/skills/subagent-driven-development/spec-reviewer-prompt.md`, and
`superpowers/skills/subagent-driven-development/code-quality-reviewer-prompt.md`.

**Effort:** Medium (1-2 days)

**Expected impact:** High. Code review is currently absent from agent-agentic-os.
Routing via the event bus means the improvement loop can measure review quality
over time and propose targeted changes automatically.

---

## Quick Win 7: Embed Process Flow Diagrams in Existing Skills

**What to build/change:**
Add inline Graphviz dot diagrams to the most complex agent-agentic-os and
exploration-cycle-plugin skills that currently only have prose descriptions.
Priority targets:
- `skills/concurrent-agent-loop/SKILL.md` (Fast Cycle and Standard Cycle workflows)
- `skills/exploration-workflow/SKILL.md` (Phase A workflow already has an external
  .mmd file but it is not embedded)
- `agents/exploration-cycle-orchestrator-agent.md` (routing decision tree)

No scripts or reference files needed -- the digraph block lives inline in the
SKILL.md. No ADR-003 symlinks required.

**Inspired by:** `superpowers/skills/brainstorming/SKILL.md`,
`superpowers/skills/subagent-driven-development/SKILL.md`, and
`superpowers/skills/dispatching-parallel-agents/SKILL.md` -- all embed `digraph`
blocks directly in skill markdown, making decision trees machine-readable.

**Effort:** Small (2-4 hours)

**Expected impact:** Low-Medium. Improves skill router accuracy and reduces friction
for agents navigating complex conditional workflows.

---

## Quick Win 8: Port the writing-skills TDD Methodology to Skill Authoring

**What to build/change:**
Add `skills/writing-skills/SKILL.md` to agent-agentic-os, adapted to use the
existing `skill-improvement-eval` infrastructure as the GREEN verification step.
The TDD mapping table (test case = pressure scenario, RED = agent violates rule
without skill, GREEN = agent complies, refactor = close loopholes) becomes the
canonical skill authoring guide.

Add a requirement to the os-learning-loop agent: before proposing any new skill
or skill patch, generate one RED scenario (a prompt that currently produces wrong
behavior) and verify the patch produces GREEN behavior. This closes the gap between
the current keyword heuristic eval and actual behavior verification.

Prose-only skill. No scripts, no ADR-003 symlinks needed.

**Inspired by:** `superpowers/skills/writing-skills/SKILL.md` (TDD-for-documentation
mapping table, "run baseline scenario BEFORE writing skill" requirement) and
`superpowers/docs/testing.md` (integration test concept).

**Effort:** Medium (1-2 days to adapt; 1 week to add RED-scenario gate to
os-learning-loop and validate it)

**Expected impact:** High. The current eval gate uses keyword overlap heuristics
explicitly flagged as a Goodhart's Law risk. Adding RED-scenario verification gives
the improvement loop a harder objective signal and eliminates keyword-stuffed
descriptions that score well but route poorly.

---

*All recommendations are grounded in specific files observed in the source repositories.
Effort estimates assume one developer. Impact ratings are relative to the current
state of the richfrem plugin ecosystem.*
*Revised after antigravity architectural review to comply with ADR-002, ADR-003, ADR-004.*
