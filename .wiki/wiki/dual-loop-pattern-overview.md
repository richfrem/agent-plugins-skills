---
concept: dual-loop-pattern-overview
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/exploration-workflow/references/dual-loop-architecture.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.087321+00:00
cluster: inner
content_hash: 72766534916abace
---

# Dual-Loop — Pattern Overview

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Dual-Loop — Pattern Overview

**Industry standard**: Sequential Agent / Agent as Tool
**Diagram**: [dual_loop_architecture.mmd](../assets/diagrams/dual_loop_architecture.mmd)
**Full skill reference**: [triple-loop-skill.md](triple-loop-skill.md)

---

## What It Is

The Dual-Loop is an inner/outer agent delegation pattern. An Outer Loop agent (strategic
controller) scopes work, generates a tightly-constrained packet, and hands it to an Inner Loop
agent (tactical executor). The Outer Loop then verifies the result and either commits or
generates a correction packet and re-delegates.

Use it for: delegating well-defined, bounded tasks to a worker agent with verification and
correction cycles.

---

## Structure

```
Outer Loop (Strategy & Protocol)
  Scout & Plan -> Define Work Packages -> Generate Strategy Packet
                                               |
                                           Handoff (spawn CLI / API call)
                                               |
                                        Inner Loop (Execution)
                                          Read Packet -> Write Code & Tests -> Signal Done
                                               |
                                        Completion signal
                                               |
  Verify Result
    Pass  -> Seal & Commit
    Fail  -> Generate Correction Packet -> Handoff again
```

---

## Roles

| Role | Responsibility | Constraints |
|---|---|---|
| **Outer Loop** | Strategy, architecture decisions, git, human interaction | Does not write implementation code |
| **Inner Loop** | Write code, run tests, signal done | NO git commits, no scope creep beyond packet |

---

## Strategy Packet Requirements

The packet handed to the Inner Loop must contain:
- The exact goal (no ambiguity)
- A Pre-Execution Workflow Commitment Diagram (ASCII box of steps)
- Only the specific file paths the Inner Loop needs
- Strict "NO GIT" constraint
- Clear Acceptance Criteria

Minimal packets prevent the Inner Loop from being overwhelmed with irrelevant context.

---

## Verification Protocol

On **Pass**: accept changes, update task tracker to Done.

On **Fail** — Correction Packet severity tiers:
- **CRITICAL**: code fails to compile, tests fail, feature entirely missing
- **MODERATE**: feature works but violates architecture or ADRs
- **MINOR**: feature works, minor naming or style issues

Loop back to handoff with the correction packet. Repeat until pass.

---

## When to Use in the Exploration Cycle

- **Requirements capture passes**: dispatch requirements-doc-agent as Inner Loop for cheap,
  isolated document generation (Copilot CLI, many invocations per session)
- **When work is well-defined**: scope is clear, acceptance criteria are writeable
- **When isolation matters**: Inner Loop runs in a sandboxed context with no git access

---

## Workspace Note

Dual-Loop does not manage workspaces. It receives an isolated directory from the Orchestrator.
Workspace creation (worktrees, branches) is the Orchestrator's responsibility.

See [learning-loop-architecture.md](learning-loop-architecture.md) for the containing
cognitive continuity pattern that wraps the Dual-Loop during full exploration sessions.


## See Also

- [[learning-loop-pattern-overview]]
- [[learning-loop-pattern-overview]]
- [[triple-loop-learning-system---architecture-overview]]
- [[loop-scheduler-and-heartbeat-pattern]]
- [[autoresearch-overview-applying-the-karpathy-loop-to-any-target]]
- [[triple-loop-learning-system---architecture-overview]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/exploration-workflow/references/dual-loop-architecture.md`
- **Indexed:** 2026-04-17T06:42:10.087321+00:00
