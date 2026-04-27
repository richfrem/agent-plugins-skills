---
concept: dispatch-strategies
source: plugin-code
source_file: exploration-cycle-plugin/references/dispatch-strategies.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.976744+00:00
cluster: model
content_hash: 48f5045ffc4ed160
---

# Dispatch Strategies

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Dispatch Strategies

This document defines how the exploration-cycle orchestrator delegates work to sub-agents and models,
prioritizing token efficiency. The core principle: **the orchestrator (expensive model, large context)
should only do coordination work — delegate everything else to the cheapest model capable of that task.**

## Strategy Selection

The SME chooses a strategy during Block 0 of `exploration-workflow`. Choices:

| Strategy | When | Free/cheap model | Premium model | Cost model |
|---|---|---|---|---|
| `copilot-cli` | User has GitHub Copilot Pro | `gpt-5-mini` (free) | `claude-sonnet-4.6` or `claude-opus-4.6` | **Per request** — batch everything into 1 dense call |
| `gemini-cli` | User has Gemini CLI | `gemini-3.1-flash-lite-preview` (cheap) | `gemini-3.1-pro-preview` | Per token — standard |
| `claude-subagents` | Claude Code only, no external CLI | `haiku-4.5` (cheapest) | `sonnet` / `claude-sonnet-4.6` | Per token — standard |
| `direct` | No sub-agent tooling / all in-session | This session's model | This session's model | This session's cost model |

> **Model names change.** The identifiers above are current as of the plugin version date. Always verify against:
> - Copilot CLI: `copilot --help` or [GitHub Copilot model docs](https://docs.github.com/en/copilot/using-github-copilot/ai-models)
> - Gemini CLI: `gemini --help` or Google AI docs
> - Claude sub-agents: check `haiku` model alias or use full model ID from Anthropic docs

Record the resolved strategy in `exploration/exploration-dashboard.md` as `**Dispatch Strategy:**`.

### Critical: Copilot CLI Premium Request Batching

Copilot CLI charges **per request**, not per token. This changes everything about how you use premium models:

- **Wrong:** 3 separate `claude-sonnet-4.6` calls for 3 related tasks = 3 premium charges
- **Right:** 1 dense call with all 3 tasks fully specified = 1 premium charge

**Rule:** Before making any Copilot premium model call, ask: "Can I combine this with anything else I'll need in the next few turns?" If yes — combine first, then call once. See `plugins/copilot-cli/skills/copilot-cli-agent/SKILL.md` for the full batching discipline and `===FILE:===` delimiter pattern.

## Task Complexity Guide

Use this to decide which model/strategy tier to use for each task:

| Task type | Complexity | Dispatch tier |
|---|---|---|
| Single-pass document capture (requirements, stories) | Simple | Free / cheap |
| Business rule audit against BRD | Simple | Free / cheap |
| Filling in a template from provided input | Simple | Free / cheap |
| Prototype component (scoped, self-contained) | Complex | Premium |
| Handoff synthesis across multiple captures | Complex | Premium |
| Discovery planning session (interactive) | In-session | Orchestrator direct |
| Re-entry scope drafting | Simple | Free / cheap |

## Token Efficiency: Cheap Sub-Agents for Q&A

**Design insight (from architecture review):** Even clarifying questions back to the SME can be
delegated to a cheap model. The orchestrator's expensive context should be reserved for coordination
decisions and synthesis — not interactive back-and-forth Q&A.

**Pattern:**

1. Orchestrator identifies a clarification need (missing information, ambiguous input)
2. Orchestrator drafts the exact question(s) to ask — 3-5 max, numbered
3. Dispatches a cheap model to:
   a. Present the questions to the SME (via CLI or lightweight session)
   b. Collect and structure the answers
   c. Write answers to `exploration/captures/clarifications-[topic].md`
4. Orchestrator reads the structured answers file and continues

**When to apply this pattern:**
- Filling gaps in a session brief (after initial brief is created)
- Clarifying ambiguous business rules during BRD review
- Scoping questions during prototype observation capture
- Any Q&A that can be expressed as numbered questions + structured answers

**When NOT to apply:**
- The first framing conversation with the SME (needs orchestrator presence)
- 

*(content truncated)*

## See Also

- [[premium-dispatch-claude-sonnet-46-for-complex-multi-file-generation-charged-per-request-batch-everything]]
- [[task-dispatch-agent-uses-filesystem-tools-default-behaviour]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/references/dispatch-strategies.md`
- **Indexed:** 2026-04-27T05:21:03.976744+00:00
