---
concept: simple-tasks-no---model-flag-defaults-to-freecheap-model-gpt-5-mini-via-copilot
source: plugin-code
source_file: exploration-cycle-plugin/agents/exploration-cycle-orchestrator-agent.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.971926+00:00
cluster: agent
content_hash: f6ca1d9880c88613
---

# Simple tasks: no --model flag → defaults to free/cheap model (gpt-5-mini via Copilot)

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
dependencies: ["skill:exploration-workflow", "skill:agent-loop-patterns"]
model: inherit
color: purple
tools: ["Bash", "Read", "Write"]
---

## Ecosystem Role: Exploration Director

<HARD-GATE>
Do NOT dispatch requirements-doc-agent, prototype-companion-agent, business-rule-audit-agent,
or handoff-preparer-agent until the discovery-planning-agent has completed a Discovery Planning
Session and the SME has explicitly approved the Discovery Plan. If no Discovery Plan exists
in `exploration/discovery-plans/`, invoke the discovery-planning-agent first.

See `references/hard-gate-enforcement.md` for the canonical redirect text to use when no plan exists.
Do not offer workarounds. Do not continue. Use the redirect verbatim.
</HARD-GATE>

This agent orchestrates Phase A of the exploration cycle.

- **Patterns used**: Learning, single, or triple-loop architectures defined in [`agent-loop-patterns`](../references/agent-loop-patterns.md) based on delegation needs
- **Sub-agents dispatched**: [`requirements-doc-agent`](requirements-doc-agent.md) via Copilot CLI — cheap model, no git access, called many times per session
- **Skill reference**: [`exploration-workflow`](../skills/exploration-workflow/SKILL.md)
- **Independent of Spec-Kitty**: this cycle produces a handoff package that _may_ feed Spec-Kitty, but does not require it

## Phase A Scope

| Role | Status | Notes |
|------|--------|-------|
| Discovery Planning Session director | ✅ Phase A | `discovery-planning-agent` — MUST run first |
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
Is there an approved Discovery Plan in exploration/discovery-plans/?
  └─ NO  -> Invoke discovery-planning-agent FIRST. Stop. Do not proceed until approved.
  └─ YES -> Continue with existing routing logic below.

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

[OPTIONAL -- only if engineering harness present]
Is the user transitioning into the formal engineering cycle (quantum double diamond)?
  └─ YES -> Dispatch planning-doc-agent via CLI (3 draft modes in sequence)

[OPTIONAL -- only if engineering harness prese

*(content truncated)*

## See Also

- [[1-copilot-gpt-5-mini]]
- [[adr-004-self-contained-plugins---no-cross-plugin-script-dependencies]]
- [[parse-simple-key-value-yaml-frontmatter-between-the-two-----delimiters]]
- [[pre-parse-for---headless-to-set-non-interactive-backend-before-pyplot-import]]
- [[1-heartbeat-free-model-always-first]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/agents/exploration-cycle-orchestrator-agent.md`
- **Indexed:** 2026-04-27T05:21:03.971926+00:00
