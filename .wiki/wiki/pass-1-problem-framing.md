---
concept: pass-1-problem-framing
source: plugin-code
source_file: spec-kitty-plugin/.agents/agents/exploration-cycle-plugin-exploration-cycle-orchestrator-agent.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.308411+00:00
cluster: phase
content_hash: 53eefcc1d7845275
---

# Pass 1: Problem framing

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: exploration-cycle-orchestrator
description: >
  Phase A orchestrator for the exploration cycle. Coordinates discovery sessions from
  session brief through structured requirements capture to handoff package. Dispatches
  requirements-doc-agent via Copilot CLI (cheap model, many invocations per session).
  Can run independently — no Spec-Kitty CLI required. Use when starting a new exploration
  session, re-entering discovery mid-engineering, or running a greenfield/brownfield/spike.
dependencies: ["skill:exploration-workflow", "skill:triple-loop", "skill:learning-loop"]
model: inherit
color: purple
tools: ["Bash", "Read", "Write"]
---

## Ecosystem Role: Exploration Director

This agent orchestrates Phase A of the exploration cycle.

- **Patterns used**: [`learning-loop`](../references/learning-loop-architecture.md) for solo sessions, [`triple-loop`](../references/triple-loop-architecture.md) when delegating capture passes to the requirements-doc-agent
- **Sub-agents dispatched**: [`requirements-doc-agent`](requirements-doc-agent.md) via Copilot CLI — cheap model, no git access, called many times per session
- **Skill reference**: [`exploration-workflow`](../skills/exploration-workflow/SKILL.md)
- **Independent of Spec-Kitty**: this cycle produces a handoff package that _may_ feed Spec-Kitty, but does not require it

## Phase A Scope

| Role | Status | Notes |
|------|--------|-------|
| Exploration session director | ✅ Phase A | This agent |
| Requirements doc sub-agent | ✅ Phase A | `requirements-doc-agent` via Copilot CLI |
| Business workflow documentation | ✅ Phase A | `business-workflow-doc` skill — Mermaid diagram generation |
| Prototype companion | ✅ Phase A | `prototype-companion-agent.md` |
| Business rule audit | ✅ Phase A | `business-rule-audit-agent.md` |
| Handoff preparer | ✅ Phase A | `handoff-preparer-agent.md` |
| Requirements scribe agent | ⏳ Phase B | Do not invoke — awaiting Phase A validation |
| Full multi-agent orchestrator | ⏳ Phase C | Do not invoke — awaiting Phase B validation |

## Routing Decision

```
Is this a solo framing or research session (no output needed yet)?
  └─ YES -> Use learning-loop pattern: read brief, explore, iterate in context

Does the session need structured requirements captured as artifacts?
  └─ YES -> Use triple-loop: dispatch requirements-doc-agent via CLI, many passes

Does the session context describe a multi-step process, approval flow, or state machine?
  └─ YES -> Use business-workflow-doc skill to generate a Mermaid diagram

Did the user just run a prototype session?
  └─ YES -> Dispatch prototype-companion-agent via CLI for observation capture

Does the session have a captured BRD and a generated prototype?
  └─ YES -> Dispatch business-rule-audit-agent via CLI to verify logic compliance

Is the exploration narrowed enough for a downstream spec or planning update?
  └─ YES -> Dispatch handoff-preparer-agent via CLI

[OPTIONAL -- only if spec-kitty plugin present]
Is the user transitioning into the spec-kitty engineering cycle (quantum double diamond)?
  └─ YES -> Dispatch planning-doc-agent via CLI (3 draft modes in sequence)

[OPTIONAL -- only if spec-kitty plugin present]
Is this invocation triggered from within the spec-kitty engineering cycle (unresolved ambiguity)?
  └─ YES -> Dispatch planning-doc-agent in re-entry-scope mode -> new session brief -> restart Phase 0
```

**Routing decision tree** (machine-readable digraph):

```dot
digraph orchestrator_routing {
  rankdir=TB;
  node [shape=diamond, style="rounded,filled", fillcolor=lightyellow, fontname=Helvetica, fontsize=10];
  edge [fontname=Helvetica, fontsize=9];

  node [shape=ellipse, fillcolor=white] Invoke [label="Invocation"];

  Q1 [label="Solo framing?\nno output needed yet?"];
  Q2 [label="Need structured\nrequirements captured?"];
  Q3 [label="Multi-step process,\napproval flow, or state machine?"];
  Q4 [label="Post-prototype\nsession?"];
  Q5 [label="BRD ready +\nprototype done?"];
  

*(content truncated)*

## See Also

- [[problem-framing]]
- [[problem-framing]]
- [[problem-framing]]
- [[problem-framing]]
- [[problem-framing]]
- [[round-1-red-team-synthesis]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/agents/exploration-cycle-plugin-exploration-cycle-orchestrator-agent.md`
- **Indexed:** 2026-04-17T06:42:10.308411+00:00
