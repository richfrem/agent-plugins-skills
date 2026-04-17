---
concept: exploration-cycle-plugin-design-recommendation
source: plugin-code
source_file: exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/design-artifacts/exploration-cycle-plugin-design-plan.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.573537+00:00
cluster: keep
content_hash: 4d245de3b18fdc47
---

# Exploration Cycle Plugin: Design Recommendation

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Exploration Cycle Plugin: Design Recommendation

## Overview

This document is the definitive design recommendation for Opportunity 3's **Exploration Cycle Plugin**. It is based on:

1. The current state of the plugin at `plugins/exploration-cycle-plugin` (source of truth)
2. The superpowers harness (referenced from `temp/ReposToAnalyze/superpowers`)
3. The strategic vision of Opportunity 3: democratizing exploration for **non-technical SMEs**, not developers

The core thesis: **borrow the rigorous mechanics of superpowers, translate all developer language into business language, and add the tools a full product team would bring.**

---

## Current State Inventory

### exploration-cycle-plugin (Source of Truth)

**Skills (existing):**
| Skill | Status | Notes |
|---|---|---|
| `exploration-session-brief` | ✅ Keep | Core intake capability |
| `business-requirements-capture` | ✅ Keep | Core BA capability |
| `business-workflow-doc` | ✅ Keep | Core workflow mapping |
| `user-story-capture` | ✅ Keep | Core Agile translation |
| `exploration-handoff` | ✅ Keep + Enhance | Needs Opp 4 adapter outputs |
| `exploration-workflow` | ✅ Keep + Enhance | Main orchestration driver |
| `prototype-builder` | ⚠️ Deferred → Promote | Move out of deferred, needs major enhancement |
| `exploration-orchestrator` | ⚠️ Deferred → Promote | Move out of deferred |
| `exploration-optimizer` | ⚠️ Later Phase | Keep deferred for now |

**Agents (existing):**
| Agent | Status | Notes |
|---|---|---|
| `exploration-cycle-orchestrator-agent.md` | ✅ Keep | Top-level orchestrator |
| `intake-agent.md` | ✅ Keep | SME onboarding |
| `requirements-doc-agent.md` | ✅ Keep | Doc-extraction agent |
| `problem-framing-agent.md` | ✅ Keep | Optional interactive alternative |
| `prototype-companion-agent.md` | ⚠️ Enhance | Must become full-prototype builder not wireframer |
| `handoff-preparer-agent.md` | ✅ Keep + Enhance | Add Opp 4 format adapters |
| `planning-doc-agent.md` | ✅ Keep | Critical bridge to Opp 4 |
| `business-rule-audit-agent.md` | ✅ Keep | Cross-reference spec vs prototype |
| `exploration-loop-orchestrator.md` | ⚠️ Deferred | Keep deferred |
| `requirements-scribe-agent.md` | ⚠️ Deferred | Keep deferred |

**Hooks (existing):**
| Hook | Status | Notes |
|---|---|---|
| `session_start.py` | ✅ Keep | Session initialization |
| `event_subscriber.py` | ✅ Keep | Event-driven routing |
| `hooks.json` | ✅ Keep | Config |

---

## Superpowers Skills Inventory

**Superpowers Skills available for adoption/inspiration:**
| Superpowers Skill | Translates To in Opp 3 |
|---|---|
| `brainstorming` | **The Discovery Session** — borrow the full rigorous workflow: one question at a time, multi-option proposals, spec self-review, HARD-GATE |
| `visual-companion.md` | **The Visual Companion** — borrow entirely, use for wireframe confirm step |
| `spec-document-reviewer-prompt.md` | **The Spec Alignment Checker** — borrow as the TDD-of-specs self-review |
| `writing-plans` | **The Discovery Plan** — borrow the planning discipline; adapt language from dev-tasks to business-activities |
| `executing-plans` | **The Prototype Execution Plan** — the mechanical executor for subagent-driven-prototyping |
| `subagent-driven-development` | **subagent-driven-prototyping** — adapted from developer to SME context |
| `using-git-worktrees` | **The Prototype Sandbox** — borrow entirely, just rename the concept |
| `verification-before-completion` | **The Spec Alignment Verification** — verify prototype matches approved business rules |
| `requesting-code-review` | **Spec Compliance Review** — independent agent checks if prototype matches intent |
| `receiving-code-review` | (Borrow if needed for structured feedback loops) |
| `finishing-a-development-branch` | **Handoff Finalization** — prototype finalization before handoff |
| `systematic-debugging` | (Internal, borrows as-is when prototype breaks) |
| `test-driven-development` | (Internal, borrow as-is for prototype quality) |
| `d

*(content truncated)*

## See Also

- [[agent-execution-prompt-exploration-cycle-plugin-upgrade]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]
- [[exploration-cycle-plugin-upgrade-implementation-plan]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[copilot-proposer-prompt-exploration-cycle-plugin]]
- [[optimization-program-exploration-cycle-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/design-artifacts/exploration-cycle-plugin-design-plan.md`
- **Indexed:** 2026-04-17T06:42:09.573537+00:00
