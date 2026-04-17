---
concept: deferred-exploration
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/deferred/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.018974+00:00
cluster: plugin-code
content_hash: 3fee3869d8dccdb8
---

# Deferred Exploration

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: deferred
description: >-
  Holds and manages deferred exploration work in the exploration cycle. Use when
  deferring decisions or tasks until prototype data is available, holding back
  ambiguous scope items for later discovery, or re-entering a paused exploration
  session. Trigger with "defer this exploration", "park this decision for later",
  "hold exploration until prototype is ready", or "re-enter deferred exploration".
allowed-tools: Bash, Read, Write
---

# Deferred Exploration

> ⚠️ **STUB** — This skill is a container for deferred/in-progress exploration sub-skills.

This skill coordinates exploration work that must be deferred until more information is
available, typically prototype feedback or clarified business requirements.

## Sub-Skills

- [exploration-orchestrator](./exploration-orchestrator/SKILL.md) — Coordinates the multi-agent exploration loop
- [prototype-builder](./prototype-builder/SKILL.md) — Builds exploratory prototypes to make direction concrete

## When to Use

- Defer a decision or exploration thread until prototype data is available
- Hold back ambiguous scope items rather than prematurely narrowing
- Re-enter a paused exploration phase from a deferred state
- Park exploration work while waiting for stakeholder input


## See Also

- [[category-semantic-deferred-tool-binding]]
- [[category-semantic-deferred-tool-binding]]
- [[category-semantic-deferred-tool-binding]]
- [[category-semantic-deferred-tool-binding]]
- [[category-semantic-deferred-tool-binding]]
- [[category-semantic-deferred-tool-binding]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/deferred/SKILL.md`
- **Indexed:** 2026-04-17T06:42:10.018974+00:00
