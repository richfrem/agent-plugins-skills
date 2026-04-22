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
- Discovery Planning Session (interactive, nuanced — needs full model capability)
- Phase completion gates (require orchestrator judgment)

## Fallback Behavior

If the chosen strategy becomes unavailable mid-session:
1. Fall back silently to `direct` mode
2. Inform the SME: "The [strategy] strategy isn't available. I'll handle the rest directly."
3. Update `**Dispatch Strategy:**` in the dashboard to `direct (fallback)`

## Dispatch Reference by Environment

### Claude Code — `claude-subagents` strategy

Use the `Agent` tool directly in Claude Code. Set `model: "haiku"` for simple tasks, omit for complex ones (inherits current session model).

```
# Simple capture task — haiku
Agent({
  description: "Capture problem framing from session brief",
  model: "haiku",
  prompt: "Read exploration/session-brief.md. Mode: problem-framing.
           Extract the problem statement, user groups, goals, and scope hypotheses.
           Write structured output to exploration/captures/problem-framing.md.
           Mark anything not stated as [NEEDS HUMAN INPUT]."
})

# Q&A clarification pass — haiku
Agent({
  description: "Collect BRD clarifications",
  model: "haiku",
  prompt: "Read exploration/captures/brd-draft.md. Find every [NEEDS HUMAN INPUT] marker.
           Present the 3 most important as plain questions to the user, collect their answers,
           and write a structured summary to exploration/captures/clarifications-brd.md."
})

# Business rule audit — haiku
Agent({
  description: "Audit prototype against BRD",
  model: "haiku",
  prompt: "Read exploration/captures/brd-draft.md and exploration/captures/prototype-notes.md.
           For each business rule in the BRD, check whether the prototype notes confirm,
           contradict, or leave it uncertain. Write findings to exploration/captures/audit-findings.md.
           Flag CONTRADICTED and UNCERTAIN rules explicitly."
})

# Handoff synthesis — sonnet (complex, multi-file)
Agent({
  description: "Synthesise exploration captures into handoff package",
  prompt: "Read all files in exploration/captures/. Synthesise into a handoff package at
           exploration/handoffs/handoff-package.md following the handoff-preparer-agent instructions.
           Cite source files for every major claim. Mark gaps [NEEDS HUMAN INPUT]."
})
```

### Copilot CLI — `copilot-cli` strategy

```bash
# Simple capture task — gpt-5-mini (free tier)
python scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-requirements-doc-agent/SKILL.md \
  --context exploration/session-brief.md \
  --instruction "Mode: problem-framing. Capture the problem statement, user groups, goals." \
  --output exploration/captures/problem-framing.md

# Q&A clarification pass — gpt-5-mini (free tier)
python scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-requirements-doc-agent/SKILL.md \
  --context exploration/captures/brd-draft.md \
  --instruction "Ask 3 targeted questions to clarify the gaps marked [NEEDS HUMAN INPUT].
                 Write structured answers to clarifications-brd.md." \
  --output exploration/captures/clarifications-brd.md

# Complex synthesis — claude-sonnet (1 premium request, batch dense for value)
# Pack all captures into one invocation — Copilot charges per request, not per token
python scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-handoff-preparer-agent/SKILL.md \
  --context exploration/captures/problem-framing.md \
             exploration/captures/brd-draft.md \
             exploration/captures/user-stories-draft.md \
             exploration/captures/prototype-notes.md \
             exploration/captures/audit-findings.md \
  --instruction "Synthesise all captures into a complete handoff package.
                 Cite sources. Mark gaps [NEEDS HUMAN INPUT]." \
  --output exploration/handoffs/handoff-package.md
```

### When no sub-agent tooling is available (`direct` strategy)

Run all tasks in the current session. To reduce context carry-forward:
- After completing a capture pass, summarise the output in 3 bullet points before moving on — the summary travels with you, not the full output.
- After Phase 1 completes, use `/compact` before starting Phase 2.
- After Phase 3 completes, use `/compact` before starting Phase 4.
- Pass file paths to the next phase, not file contents — read on demand rather than keeping everything in context.
