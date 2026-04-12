# Dispatch Strategy Reference

> Read this file during Block 0 (Bootstrap) when asking the SME about dispatch strategy,
> or during Phase 3 when deciding which model to use for a task.

## Copilot CLI (`copilot-cli`)

- Uses the `copilot-cli-agent` skill pattern (`scripts/run_agent.py`)
- Simple/mechanical tasks → `gpt-4o-mini` (free, unlimited)
- Complex reasoning/multi-file generation → `claude-sonnet-4-6` (1 premium request; batch everything into one dense prompt)
- Key advantage: premium model is charged per REQUEST not per token — one big prompt with 7 file specs costs the same as one small prompt

## Claude Sub-agents (`claude-subagents`)

- Uses the `Agent` tool with `model` parameter
- Mechanical tasks → `model: "haiku"` (cheapest Claude model)
- Complex tasks → `model: "sonnet"` (mid-tier)
- Follows the pattern from orba/superpowers: orchestrator stays on the primary model, dispatches implementation to cheaper models

## Direct (`direct`)

- All work done in the current session by the current model
- Simplest approach, no dispatch overhead
- Best when the session is interactive and the SME wants to see everything happen live

## Decision Tree (for the orchestrator, not the SME)

When dispatching a task during Phase 3:

```
Is the task mechanical / single-file / boilerplate?
  → copilot-cli: gpt-4o-mini (free)
  → claude-subagents: model: "haiku" (cheapest)
  → direct: do it inline

Is the task complex / multi-file / requires reasoning?
  → copilot-cli: claude-sonnet-4-6 (batch into ONE dense request)
  → claude-subagents: model: "sonnet"
  → direct: do it inline

Is the task orchestration / planning / decision-making?
  → Always keep in the current session (orchestrator model)
  → Never delegate planning or routing decisions to cheap models
```

The orchestrator always stays on the primary model. It delegates
**implementation** to cheaper/free models. It never delegates **judgment**.

## Special Cases

**Analysis/Docs sessions:** Skip the dispatch strategy question entirely.
Default to `direct`. Announce: *"Since this is a documentation session with no code
phase, I'll handle all the work directly."*

**Fallback:** If the chosen dispatch strategy becomes unavailable during Phase 3,
fall back to `direct` mode and announce: *"The [strategy] dispatch isn't available
right now, so I'll build this directly in this session."*
