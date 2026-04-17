---
concept: exploration-cycle-plugin-upgrade-implementation-plan
source: plugin-code
source_file: exploration-cycle-plugin/docs/superpowers/plans/2026-04-06-exploration-cycle-smr-upgrade.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.579765+00:00
cluster: step
content_hash: 98ebd257abf605eb
---

# Exploration Cycle Plugin: Upgrade Implementation Plan

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Exploration Cycle Plugin: Upgrade Implementation Plan

> **For agentic workers:** Use `superpowers:brainstorming` and `superpowers:subagent-driven-development` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the exploration-cycle-plugin to adopt the rigorous planning mechanics from the `superpowers` harness while translating all language and personas for non-technical Subject Matter Experts (SMEs), and adding full-prototype generation capability beyond static wireframes.

**Architecture:** The upgrade adds four new skills (`discovery-planning`, `visual-companion`, `subagent-driven-prototyping`, `spec-alignment-checker`), promotes `prototype-builder` from deferred to active, adds a `discovery-planning-agent.md`, enhances the orchestrator with a `<HARD-GATE>`, and adds Opportunity 4 format adapters to the handoff stack.

**Core Principle:** Every piece of developer language from `superpowers` must be translated into business-friendly SME language. The mechanics stay; the vocabulary changes.

**Source Reference:** The `superpowers` harness skills to reference and adapt are: `brainstorming/SKILL.md`, `brainstorming/visual-companion.md`, `brainstorming/spec-document-reviewer-prompt.md`, `writing-plans/SKILL.md`, `executing-plans/SKILL.md`, `subagent-driven-development/SKILL.md`, `using-git-worktrees/SKILL.md`, `verification-before-completion/SKILL.md`.

---

## Pre-Work: Set Up Worktree

- [ ] **Step 1: Create isolated worktree for this upgrade**

```bash
git worktree add ../exploration-cycle-plugin-upgrade -b feat/smr-upgrade
cd ../exploration-cycle-plugin-upgrade
```

---

## Task 1: Create `discovery-planning` Skill

> **Adapted from:** `superpowers/brainstorming/SKILL.md`
> **SME Translation:** "Brainstorming" → "Discovery Planning Session". Developer language removed. HARD-GATE enforced before any capture agents fire.

**Files:**
- Create: `skills/discovery-planning/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p skills/discovery-planning
```

- [ ] **Step 2: Write `skills/discovery-planning/SKILL.md`**

Write the following content to `skills/discovery-planning/SKILL.md`:

```markdown
---
name: discovery-planning
description: >
  MUST run before any exploration capture begins. Leads the SME through a structured
  Discovery Planning Session to understand the problem, propose 2-3 solution
  approaches, build a Discovery Plan, and get explicit SME approval before
  dispatching any documentation or prototype agents. Trigger with "start exploration",
  "let's plan this out", "I have an idea", "help me scope this", or at the beginning
  of any new Opportunity 3 session.
---

# Discovery Planning Session

Help any Subject Matter Expert — technical or non-technical — turn a raw idea, business
problem, or process pain point into a structured Discovery Plan through natural,
guided conversation.

Start by understanding the current context, then ask one question at a time to refine
the idea. Once you understand what we are going to explore, present the plan and get
the SME's explicit approval before anything is documented or built.

<HARD-GATE>
Do NOT dispatch any documentation agents (requirements-doc-agent, prototype-companion-agent,
business-rule-audit-agent, handoff-preparer-agent) or trigger any prototype-building
activity until you have presented a Discovery Plan and the SME has explicitly approved it.
This applies to EVERY session regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple to Need a Plan"

Every session goes through this process. A simple automation, a process improvement,
a documentation need — all of them. Simple problems are where unexamined assumptions
cause the most wasted effort. The plan can be brief (a few sentences), but you MUST
present it and get approval.

## Discovery Planning Checklist

Complete these steps in order:

1. **Understand the context** — ask the SME what they are trying to solve

*(content truncated)*

## See Also

- [[agent-execution-prompt-exploration-cycle-plugin-upgrade]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]
- [[exploration-cycle-plugin-design-recommendation]]
- [[exploration-cycle-plugin-architecture-reference]]
- [[copilot-proposer-prompt-exploration-cycle-plugin]]
- [[optimization-program-exploration-cycle-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/docs/superpowers/plans/2026-04-06-exploration-cycle-smr-upgrade.md`
- **Indexed:** 2026-04-17T06:42:09.579765+00:00
