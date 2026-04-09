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
| `dispatching-parallel-agents` | (Internal, borrow as-is for swarm dispatch) |
| `writing-skills` | (Internal quality) |
| `using-superpowers` | (Not applicable—developer only) |

---

## Gap Analysis

### Gap 1: No Rigorous Discovery Plan Phase (Critical)
**Current State:** The plugin jumps straight into capturing business requirements and framing.  
**Superpowers Benchmark:** Before ANY work begins, `brainstorming` enforces an entire design-first planning checklist: explore context, offer visual companion, one-question-at-a-time dialogue, propose 2-3 approaches, get approval, write spec, self-review, user review gate.  
**Required Addition:** A new `discovery-planning` skill (or major enhancement to `exploration-workflow`) that enforces this full upfront rigour before dispatching any domain-capture agents.

### Gap 2: No Visual Companion Integration (High)
**Current State:** Prototype-companion-agent exists but is minimal. No structured visual-companion/wireframe-first step.  
**Superpowers Benchmark:** `brainstorming` explicitly offers the visual companion as a distinct step before clarifying questions. Separate protocol for when to use browser (visual) vs terminal (conceptual).  
**Required Addition:** Borrow `visual-companion.md` wholesale and adapt it. Add the visual-confirm step into `exploration-workflow` as Phase 1 of the ladder.

### Gap 3: Prototype Builder Produces Wireframes Only (Critical)
**Current State:** `prototype-builder` is deferred and scoped to functional prototypes but not fully implemented.  
**Superpowers Benchmark:** visual-companion generates wireframes but stops there.  
**Required Addition:** Promote `prototype-builder` out of deferred. It must generate fully working, runnable, interactive software—not just wireframes. The SME must be able to click through real business flows.

### Gap 4: No HARD-GATE Protocol (High)
**Current State:** Nothing explicitly prevents the orchestrator from dispatching business-rule writers before the Discovery Plan is approved.  
**Superpowers Benchmark:** `brainstorming` has an explicit `<HARD-GATE>` block preventing any implementation action until the user approves the design.  
**Required Addition:** Add `<HARD-GATE>` constraint to `exploration-workflow` and `exploration-cycle-orchestrator-agent.md` preventing any domain-capture subagents from firing until the Discovery Plan has explicit SME approval.

### Gap 5: No Spec Self-Review (Placeholder Scanning) (Medium)
**Current State:** No analog to the `writing-plans` Placeholder Scan and the `brainstorming` Spec Self-Review.  
**Superpowers Benchmark:** After writing the spec, the agent scans for TBD, TODO, contradictions, ambiguity—and fixes them before handing to the human.  
**Required Addition:** Build this into `exploration-handoff` as the pre-handoff self-review gate.

### Gap 6: Missing subagent-driven-prototyping Workflow (High)
**Current State:** `prototype-companion-agent.md` is a placeholder. No structured multi-subagent dispatch for prototype generation.  
**Superpowers Benchmark:** `subagent-driven-development` isolates each implementation task to a fresh, blank-slate subagent with two-stage review (spec compliance + code quality).  
**Required Addition:** Create `subagent-driven-prototyping` skill—adapted language, same mechanics. Each prototype component is built by a blank-slate subagent against the business spec.

### Gap 7: Opp 4 Handoff Format Adapters (Medium)
**Current State:** `exploration-handoff` and `handoff-preparer-agent.md` exist but don't produce format-specific outputs for Spec-Kitty, superpowers, or OpenSpec.  
**Required Addition:** Add a format selection step to `handoff-preparer-agent.md`—choose between Spec-Kitty `spec.md/plan.md`, superpowers `docs/superpowers/specs/` format, or generic OpenSpec format.

---

## Resultant Recommended Plugin Architecture

### Skills

| Skill Name | Source | Action |
|---|---|---|
| `discovery-planning` | **NEW** (based on superpowers `brainstorming`) | The full planning ritual: context explore, one-question dialogue, multi-option proposals, HARD-GATE, spec write, self-review, SME approval |
| `visual-companion` | **BORROW** from superpowers (adapt language) | Visual wireframe/layout confirmation step; decides browser vs terminal per question |
| `prototype-builder` | **PROMOTE + ENHANCE** (existing deferred) | Full functional prototype builder, not wireframes; uses subagent-driven-prototyping |
| `subagent-driven-prototyping` | **NEW** (adapted from superpowers `subagent-driven-development`) | Blank-slate subagent per prototype component; two-stage review (spec compliance + code quality) |
| `exploration-session-brief` | **KEEP** (existing) | SME intake and problem framing |
| `business-requirements-capture` | **KEEP** (existing) | Business requirements extraction |
| `business-workflow-doc` | **KEEP** (existing) | Workflow and process mapping |
| `user-story-capture` | **KEEP** (existing) | Agile user story translation |
| `exploration-workflow` | **ENHANCE** (existing) | Add HARD-GATE + Discovery Plan phase + visual companion routing |
| `exploration-handoff` | **ENHANCE** (existing) | Add Opp 4 format adapters + placeholder scan self-review |
| `exploration-orchestrator` | **PROMOTE** (existing deferred) | Top-level workflow driver once routing fully defined |
| `exploration-optimizer` | **DEFER** (existing deferred) | Keep for later |

### Sub-Agents

| Agent Name | Source | Action |
|---|---|---|
| `exploration-cycle-orchestrator-agent.md` | Keep | Top-level orchestrator |
| `intake-agent.md` | Keep | SME onboarding |
| `discovery-planning-agent.md` | **NEW** | Runs the full planning ritual before any domain agents fire |
| `requirements-doc-agent.md` | Keep | BA extraction (cheap sub-agent) |
| `problem-framing-agent.md` | Keep | Optional conversational alternative |
| `prototype-companion-agent.md` | **PROMOTE + REWRITE** | Full working prototype builder, not a wireframe stub |
| `business-rule-audit-agent.md` | Keep | Cross-reference prototype vs approved business rules |
| `handoff-preparer-agent.md` | **ENHANCE** | Add Opp 4 format selection + placeholder scan |
| `planning-doc-agent.md` | **ENHANCE** | Add Opp 4 format adapters |
| `requirements-scribe-agent.md` | Defer | Keep deferred |
| `exploration-loop-orchestrator.md` | Defer | Keep deferred |

### Hooks

| Hook | Action |
|---|---|
| `session_start.py` | Keep as-is |
| `event_subscriber.py` | Keep as-is |
| `hooks.json` | Keep as-is |

### New Supporting Files to Add

| File | Purpose |
|---|---|
| `skills/discovery-planning/SKILL.md` | Full SME-targeted planning ritual (adapted from superpowers brainstorming) |
| `skills/visual-companion/SKILL.md` | Adapted from superpowers visual-companion.md; browser/terminal routing |
| `skills/subagent-driven-prototyping/SKILL.md` | Adapted from superpowers subagent-driven-development; translated to business language |
| `skills/discovery-planning/spec-alignment-reviewer-prompt.md` | Adapted from superpowers spec-document-reviewer-prompt.md |

---

## The Resultant Workflow

```
Phase 0: Discovery Planning (NEW — adapted from superpowers brainstorming)
  ├── Load SME context
  ├── Offer Visual Companion (if visual questions ahead)
  ├── One question at a time → understand problem, constraints, goals
  ├── Propose 2-3 approaches, get SME approval
  ├── Write Discovery Plan (business language, not dev language)
  ├── Spec Self-Review (Placeholder scan, contradiction check)
  ├── SME Review Gate: wait for explicit approval
  └── <HARD-GATE> — no domain agents fire until here

Phase 1: Visual Confirm (BORROWED from superpowers visual-companion)
  ├── Render wireframe/layout options in browser
  ├── SME validates basic design direction
  └── Approve before prototype building begins

Phase 2: Subagent-Driven Prototyping (NEW — adapted from superpowers subagent-driven-development)
  ├── Dispatch blank-slate subagents per prototype component
  ├── Each subagent builds against the approved Discovery Plan
  ├── Spec Compliance Review (did it match what SME asked for?)
  ├── Code Quality Review (does the prototype actually work?)
  └── SME clicks through and validates the working prototype

Phase 3: Documentation Swarm (EXISTING skills, now sequenced after prototype)
  ├── requirements-doc-agent → business-requirements-capture artifacts
  ├── user-story-capture → Agile user stories from the prototype flow
  ├── business-workflow-doc → Process maps and rule ledgers
  └── business-rule-audit-agent → Verify all docs align to prototype

Phase 4: Handoff & Risk Gate (ENHANCED exploration-handoff)
  ├── Placeholder Scan self-review (adapted from superpowers writing-plans)
  ├── Format selection: Spec-Kitty / Superpowers / OpenSpec / Generic
  ├── Generate Opp 4 artifacts (spec.md, plan.md, task outlines)
  └── planning-doc-agent stages to exploration/planning-drafts/
```

---

## Key Language Translations (Developer → Business)

| Superpowers Term | Exploration Cycle Plugin Term |
|---|---|
| `brainstorming` | Discovery Planning Session |
| `writing-plans` | Discovery Plan |
| `subagent-driven-development` | Subagent-Driven Prototyping |
| `using-git-worktrees` | Prototype Sandbox |
| `spec-document-reviewer-prompt` | Spec Alignment Checker |
| `verification-before-completion` | Prototype Acceptance Check |
| `requesting-code-review` | Spec Compliance Review |
| Architecture Review | Business Rule Alignment Review |
| Implementation Tasks | Prototype Activities |
| TDD (Test-Driven Development) | Prototype Validation Loop |
| Commit | Save Checkpoint |
| Branch | Prototype Version |

---

## Summary

The guiding principle: **The mechanics of `superpowers` are near-perfect. The persona is completely wrong for SMEs.**

We borrow everything structural—the HARD-GATE, the planning-first discipline, the two-stage verification, the blank-slate subagent dispatch, the visual companion, the placeholder scan—and we translate every piece of developer vernacular into business-friendly language.

The result is a plugin where a non-technical Subject Matter Expert can walk in with a raw idea and walk out with a fully working prototype, a complete business requirements document, user stories, workflow diagrams, and a developer-ready specification package—all without ever seeing a command line, a Git log, or a subagent dispatch message.
