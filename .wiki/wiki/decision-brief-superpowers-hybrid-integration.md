---
concept: decision-brief-superpowers-hybrid-integration
source: research-docs
source_file: superpowers/decision.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.462739+00:00
cluster: plugin
content_hash: 58234738fad2c853
---

# Decision Brief: Superpowers Hybrid Integration

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
    finishing-

*(content truncated)*

## See Also

- [[implementation-plan-superpowers-hybrid-integration]]
- [[memory-promotion-decision-guide]]
- [[39-pattern-l4-architectural-decision-matrix]]
- [[39-pattern-l4-architectural-decision-matrix]]
- [[acceptance-criteria-create-mcp-integration]]
- [[procedural-fallback-tree-create-mcp-integration]]

## Raw Source

- **Source:** `research-docs`
- **File:** `superpowers/decision.md`
- **Indexed:** 2026-04-17T06:42:10.462739+00:00
