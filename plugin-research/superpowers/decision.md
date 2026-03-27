# Decision Brief: Superpowers Hybrid Integration

**Status:** Pending approval
**Branch:** feat/superpowers-hybrid-integration
**Date:** 2026-03-27
**Supporting research:** `capabilities-matrix.md`, `strengths-and-gaps.md`, `supercharge-recommendations.md`, `quick-wins.md`

---

## Problem Statement

The `agent-agentic-os` and `exploration-cycle-plugin` plugins handle long-horizon,
stateful agentic work well (memory hierarchy, eval-gated learning loop, structured
requirements capture) but have critical execution gaps: no verification-before-completion
enforcement, no TDD discipline, no systematic debugging protocol, no code review
workflow, and no safe git worktree lifecycle management.

The `superpowers` project (github.com/obra/superpowers) solves these execution gaps
well. It has three architectural advantages over the richfrem plugins:
- Zero-friction workflow enforcement via session-start hook injection
- Rigorous verification discipline (Iron Law, Common Failures table)
- Self-contained, well-tested skill files with evidence-based design decisions

The question is whether to pivot to superpowers, supercharge the richfrem plugins
with superpowers patterns, or pursue a targeted hybrid.

---

## Options

### Option A: Pivot to superpowers

Replace `agent-agentic-os` and `exploration-cycle-plugin` with superpowers as the
primary plugin system.

| | |
|---|---|
| **Gains** | Complete dev workflow (brainstorm -> plan -> execute -> review -> merge); first-class multi-platform support (Cursor, Codex, Windows); verification, TDD, debugging, code review out of the box; active community and regression testing |
| **Losses** | Three-tier persistent memory; eval-gated self-improvement loop; friction event capture and improvement ledger; exploration-cycle structured requirements capture (BRD, user stories, cheap-CLI dispatch); spec-kitty SDD lifecycle integration; cross-repo agent coordination (AGENT_COMMS pattern) |
| **Migration cost** | High. Memory infrastructure has no equivalent in superpowers and would need to be rebuilt from scratch |
| **When this makes sense** | Primary pain is unreliable software delivery; project is short-horizon (days not weeks); multi-platform portability is a hard requirement; no need for spec-kitty integration |

**Verdict: Not recommended.** The richfrem plugins solve problems superpowers does not
plan to solve. Pivoting discards a working learning flywheel and structured exploration
infrastructure with no replacement path.

---

### Option B: Keep richfrem plugins, supercharge them

Keep all richfrem plugins unchanged. Selectively import superpowers patterns into
the existing plugin structures.

| | |
|---|---|
| **Gains** | All richfrem capabilities preserved; execution gaps closed incrementally |
| **Risk** | Skills duplicated across `agent-agentic-os` and `exploration-cycle-plugin` if not architecturally disciplined - violates ADR-002, ADR-003, ADR-004 |
| **ADR constraint** | New execution-discipline skills must NOT be copied into two plugins. ADR-001 mandates plugin self-containment and Agent Skill Delegation as the cross-plugin coordination mechanism |

**Verdict: Correct strategic direction but needs architectural discipline.** Without
a dedicated plugin to own the new skills, Option B degrades into copy-paste duplication
within a session.

---

### Option C: Hybrid - New Dedicated Plugin + Selective Imports (Recommended)

Create a new `agent-execution-disciplines` plugin as the canonical home for all
ported superpowers execution skills. Richfrem plugins reference these skills by
name via Agent Skill Delegation (ADR-001 layer 3) rather than embedding copies.

**Architecture:**
```
plugins/agent-execution-disciplines/   <- NEW (this work)
  skills/
    verification-before-completion/    <- from superpowers
    systematic-debugging/              <- from superpowers
    test-driven-development/           <- from superpowers
    using-git-worktrees/               <- from superpowers
    finishing-a-development-branch/    <- from superpowers
    requesting-code-review/            <- from superpowers
  agents/
    code-reviewer.md                   <- from superpowers

plugins/agent-agentic-os/              <- UNCHANGED structure
  hooks/                               <- HARDENED session-start bash wrapper
  skills/writing-skills/               <- NEW (superpowers TDD methodology)
  (existing skills reference agent-execution-disciplines by name in prose)

plugins/exploration-cycle-plugin/      <- UNCHANGED structure
  (existing skills reference agent-execution-disciplines by name in prose)
```

| | |
|---|---|
| **Gains** | All richfrem capabilities preserved; all superpowers execution disciplines added; zero duplication in source tree; ADR-compliant; one install gives all new skills to both plugins |
| **ADR compliance** | One canonical file per skill (ADR-003); skills self-contained at deploy time (ADR-004); cross-plugin coordination via Agent Skill Delegation not script paths (ADR-001) |
| **Migration cost** | Low. New plugin only; existing plugins are additive-only changes (hook hardening, prose cross-references) |
| **Risks** | See section below |

**Verdict: Recommended.**

---

## Recommendation

**Proceed with Option C.**

Execute in priority order per `quick-wins.md`:
1. Scaffold `agent-execution-disciplines` plugin + verification-before-completion (highest impact, zero dependencies)
2. Harden SessionStart hook in `agent-agentic-os` (POSIX-safe bash wrapper, --resume guard, platform detection)
3. Port systematic-debugging, TDD, git worktrees, code review into the new plugin
4. Embed process flow diagrams into existing complex skills
5. Port writing-skills TDD methodology into `agent-agentic-os`

Success metric: after 10 sessions with the new plugin installed, `events.jsonl`
should show fewer `verification_failure` and `false_completion_claim` friction
events than the pre-integration baseline.

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `agent-execution-disciplines` grows to be a catch-all plugin | Limit scope to execution discipline skills (verification, testing, debugging, review, branching). Exploration and memory skills stay in their home plugins |
| Hook hardening breaks existing memory injection | Dry-run the hook rewrite on a test project before committing; keep Python orchestrator intact (bash wrapper only) |
| ported superpowers skills go stale as superpowers evolves | Add a note in each skill's frontmatter referencing the superpowers source file and version. Track superpowers releases in CHANGELOG |
| New plugin not installed in existing projects | Document in `agent-execution-disciplines/README.md` that it is a companion to `agent-agentic-os` and must be installed alongside it |

---

## Out of Scope (for this work)

- Brainstorming -> writing-plans -> execution pipeline (Priority 4 in Decision B) -
  this requires deeper integration with spec-kitty SDD lifecycle and is a separate feature
- Requesting-code-review integration with the kernel event bus - deferred until
  agent-execution-disciplines is stable and the simpler standalone version is validated
- Multi-platform testing (Cursor, Codex) - not blocked on this work but would
  benefit from the hook hardening in QW2
