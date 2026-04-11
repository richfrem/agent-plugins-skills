# Dispatch Strategies

This document defines how the exploration-cycle orchestrator delegates work to sub-agents and models,
prioritizing token efficiency. The core principle: **the orchestrator (expensive model, large context)
should only do coordination work — delegate everything else to the cheapest model capable of that task.**

## Strategy Selection

The SME chooses a strategy during Block 0 of `exploration-workflow`. Choices:

| Strategy | When | Simple tasks | Complex tasks |
|---|---|---|---|
| `copilot-cli` | User has GitHub Copilot Pro | `gpt-5-mini` (free) via `copilot` CLI | `claude-sonnet` (1 premium req, batched dense) |
| `claude-subagents` | No Copilot available | `haiku` (cheapest) | `sonnet` (standard) |
| `direct` | No sub-agent tooling / all in-session | This session's model | This session's model |

Record the resolved strategy in `exploration/exploration-dashboard.md` as `**Dispatch Strategy:**`.

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

## CLI Dispatch Reference

```bash
# Simple capture task (cheap model)
python3 scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-requirements-doc-agent/SKILL.md \
  --context exploration/session-brief.md \
  --instruction "Mode: problem-framing. Capture the problem statement, user groups, goals." \
  --output exploration/captures/problem-framing.md

# Q&A clarification pass (cheap model)
python3 scripts/dispatch.py \
  --agent .agents/skills/exploration-cycle-plugin-requirements-doc-agent/SKILL.md \
  --context exploration/captures/brd-draft.md \
  --instruction "Ask 3 targeted questions to clarify the gaps marked [NEEDS HUMAN INPUT]. Write answers to clarifications-brd.md." \
  --output exploration/captures/clarifications-brd.md
```
