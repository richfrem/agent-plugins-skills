---
concept: dispatch-strategy-reference
source: plugin-code
source_file: exploration-cycle-plugin/skills/exploration-workflow/references/dispatch-strategies.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.601575+00:00
cluster: model
content_hash: 18465860c79ed879
---

# Dispatch Strategy Reference

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Dispatch Strategy Reference

> Read this file during Block 0 (Bootstrap) when asking the SME about dispatch strategy,
> or during Phase 3 when deciding which model to use for a task.

## Copilot CLI (`copilot-cli`)

- Uses the `copilot-cli-agent` skill pattern (`scripts/run_agent.py`)
- Simple/mechanical tasks → `gpt-5-mini` (free, no per-request cost)
- Complex reasoning/multi-file generation → `claude-sonnet-4-6` or `claude-opus-4-6` (premium)
- **Critical cost model: charged per REQUEST, not per token.** One dense prompt with 7 file specs costs the same as one small prompt. Always batch everything into a single call.
- Full batching discipline and `===FILE:===` delimiter pattern: `plugins/copilot-cli/skills/copilot-cli-agent/SKILL.md`

## Gemini CLI (`gemini-cli`)

- Simple/mechanical tasks → `gemini-3.1-flash-lite-preview` (cheap, fast)
- Complex tasks → `gemini-3.1-pro-preview`
- Charged per token — standard model. Batching still reduces round-trips but is not as cost-critical as Copilot.

## Claude Sub-agents (`claude-subagents`)

- Uses the `Agent` tool with `model` parameter
- Mechanical tasks → `model: "haiku"` (cheapest — currently `haiku-4.5`)
- Complex tasks → `model: "sonnet"` (mid-tier)
- Orchestrator stays on primary model; dispatches implementation to cheaper models. Never delegates judgment.

## Direct (`direct`)

- All work done in the current session by the current model
- Simplest approach, no dispatch overhead
- Best when the session is interactive and the SME wants to see everything happen live

> **Model names change.** Verify current identifiers against CLI help or vendor docs before using. The names above reflect the plugin version date.

## Decision Tree (for the orchestrator, not the SME)

When dispatching a task during Phase 3:

```
Is the task mechanical / single-file / boilerplate?
  → copilot-cli:      gpt-5-mini (free)
  → gemini-cli:       gemini-3.1-flash-lite-preview (cheap)
  → claude-subagents: model: "haiku" (cheapest)
  → direct:           do it inline

Is the task complex / multi-file / requires reasoning?
  → copilot-cli:      claude-sonnet-4-6 (batch ALL related tasks into ONE dense request)
  → gemini-cli:       gemini-3.1-pro-preview
  → claude-subagents: model: "sonnet"
  → direct:           do it inline

Is the task orchestration / planning / decision-making?
  → Always keep in the current session (orchestrator model)
  → Never delegate planning or routing decisions to cheap models
```

**Copilot premium call rule — critical cost discipline:**
A detailed implementation plan, a full prototype component set, a complete handoff package — even a long yolo-mode execution task — all count as **1 premium request** if sent in a single call. Size does not change the cost. Use this aggressively.

Before calling `claude-sonnet-4-6` or `claude-opus-4-6` via Copilot, ask: "Can I combine this with anything else I'll need in the next few turns?" If yes — combine first, call once. Never split work across multiple premium calls when one dense call covers it all.

> **Model names will change over time.** The identifiers in this file are current at the plugin version date. Always verify before use:
> - Copilot: `copilot --help` or GitHub Copilot model docs
> - Gemini: `gemini --help` or Google AI docs
> - Claude: Anthropic model docs or `haiku`/`sonnet` aliases in Claude Code

## Special Cases

**Analysis/Docs sessions:** Skip the dispatch strategy question entirely.
Default to `direct`. Announce: *"Since this is a documentation session with no code
phase, I'll handle all the work directly."*

**Fallback:** If the chosen dispatch strategy becomes unavailable during Phase 3,
fall back to `direct` mode and announce: *"The [strategy] dispatch isn't available
right now, so I'll build this directly in this session."*


## See Also

- [[optimizer-engine-patterns-reference-design]]
- [[project-setup-reference-guide]]
- [[optimizer-engine-patterns-reference-design]]
- [[analysis-framework-reference]]
- [[path-reference-auditor---usage-guide]]
- [[path-reference-auditor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/skills/exploration-workflow/references/dispatch-strategies.md`
- **Indexed:** 2026-04-17T06:42:09.601575+00:00
