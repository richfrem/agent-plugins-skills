---
concept: exploration-workflow-sme-orchestrator
source: plugin-code
source_file: exploration-cycle-plugin/skills/exploration-workflow/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.987966+00:00
cluster: phase
content_hash: 2fb087e951337912
---

# Exploration Workflow — SME Orchestrator

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: exploration-workflow
description: >
  SME-facing orchestrator for the Business Exploration Loop. Supports 4 session
  types (greenfield, brownfield, discovery-only, spike) with adaptive phase
  selection. Manages state via exploration-dashboard.md, enforces phase gates,
  and routes to child skills in sequence. Phases can be skipped based on session
  type. Single canonical entry point — invoke at the start of any exploration
  session or to resume an in-progress session.
  Trigger phrases: "start an exploration", "let's explore this idea",
  "resume my exploration", "where did we leave off", "start discovery".
allowed-tools: Read, Write
---

<example>
<commentary>SME starts a brand-new exploration session from scratch.</commentary>
user: "Let's explore this idea I have for a staff scheduling tool."
agent: [invokes exploration-workflow, bootstraps dashboard, asks for session type, begins Phase 1 discovery-planning]
</example>

<example>
<commentary>SME resumes an in-progress session after prior work.</commentary>
user: "Where did we leave off with the customer portal exploration?"
agent: [invokes exploration-workflow, reads dashboard, presents status summary, routes to active phase]
</example>

<example>
<commentary>Negative — user wants to start a new discovery plan only, not the full workflow.</commentary>
user: "Run a discovery planning session for my onboarding redesign."
agent: [invokes discovery-planning directly, NOT exploration-workflow]
</example>

# Exploration Workflow — SME Orchestrator

This skill is the single canonical entry point for the Business Exploration Loop. It manages all session state via `exploration-dashboard.md`, enforces phase gates, and routes work to the correct child skill at each phase. The SME never needs to invoke any other skill directly.

## Session Types

The workflow adapts to four session types, each with different phase requirements:

| Type | When to use | Active Phases |
|------|-------------|---------------|
| **Greenfield** | Building a new app or system from scratch | All 4 phases |
| **Brownfield** | Adding a feature to an existing codebase | Phase 1 required, Phases 2 & 4 optional, Phase 3 builds into real codebase |
| **Analysis/Docs** | Non-software output: requirements, process maps, legacy code analysis, policy, strategy, workflow design | Phases 1 & 4 required, Phase 2 optional (structure not layout), Phase 3 skipped |
| **Spike** | Investigating a question or technology | Phase 1 required (may repeat), all others flexible |

---

## Execution Disciplines (powered by orba/superpowers)

> **Required dependency:** The `orba/superpowers` plugin MUST be installed alongside this
> plugin. See the plugin README for installation instructions.

When Phase 3 is active, read `references/phase3-execution-discipline.md` for the full
execution discipline protocol (superpowers availability check, worktree isolation,
build delegation, TDD validation, branch finishing).

**Summary:** The orchestrator sets up isolation (worktrees), then delegates all build
work to `subagent-driven-prototyping`. That skill owns component decomposition, dispatch,
two-stage review, and TDD. When it signals complete, the orchestrator invokes
`finishing-a-development-branch` for merge/PR options.

---

## Block 0 — Pre-Flight & Dispatch Strategy (ask once during bootstrap)

> Dispatch strategy details: `references/dispatch-strategies.md`
> Environment check: `references/environment-check.md`

**Run the environment check silently first** (see `references/environment-check.md`). Only surface results if something is missing or needs a fallback. Do not mention the check to the SME unless action is needed.

**For Analysis/Docs sessions:** Skip the dispatch strategy question. Default to `direct`.

### Token Efficiency — Claude-only sessions

If the SME has no Copilot or Gemini CLI (strategy = `claude-subagents` or `direct`), apply these practices throughout:
- **Simple capture passes** (template filling, docum

*(content truncated)*

## See Also

- [[domain-patterns-exploration-cycle]]
- [[domain-patterns-exploration-session-failures]]
- [[exploration-cycle-plugin-hooks]]
- [[exploration-handoff-interactive-co-authoring]]
- [[orchestrator-loop-router-lifecycle-manager]]
- [[triple-loop-learning-system-outer-orchestrator-inner-execution]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/skills/exploration-workflow/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.987966+00:00
