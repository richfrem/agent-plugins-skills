---
concept: task-number-title
source: plugin-code
source_file: agent-agentic-os/skills/os-evolution-planner/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.711255+00:00
cluster: model
content_hash: 7136a779bc26a0bc
---

# <task-number> — <title>

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-evolution-planner
description: >
  Codifies the plan-and-delegate workflow for evolving plugins, skills, and agents.
  Given a target (plugin/skill/agent name) and an evolution goal, this skill first
  brainstorms 2-3 approach options using the cheapest available model, presents them
  for selection, then writes a structured task plan and Copilot CLI delegation prompt
  for the chosen approach. Called by os-architect for Path B (update) and Path C (create)
  executions. Can also be invoked standalone.
model: inherit
color: blue
tools: ["Bash", "Read", "Write"]
---

## Role

os-evolution-planner transforms an evolution goal into a structured task plan and a
Copilot CLI delegation prompt that can be dispatched in one premium request. Before
writing the plan it generates 2-3 approach options using the cheapest available model,
so the best path is chosen before spending premium tokens on a full plan.

## Inputs

| Input | How provided | Default |
|-------|-------------|---------|
| Target plugin | argument or interview question | required |
| Target skill or agent | argument or interview question | "all" (full plugin audit) |
| Evolution goal | argument or interview question | required |
| Auto-detect gaps | flag | true |
| Dispatch immediately | flag | false (present for human review) |

---

## Phase 0 — Read Environment Profile

Before doing anything else, check `context/memory/environment.md`:
- If it exists, read the `## Delegation Strategy` section to determine:
  - **Brainstorm model** (cheapest available)
  - **Dispatch backend** (Copilot CLI or Claude subagent)
- If it does not exist, default to Claude-only mode and note:
  > "No environment profile found — defaulting to Claude-only. Run `os-environment-probe`
  > to unlock free-tier Copilot or Gemini brainstorming."

---

## Phase 1 — Brainstorm Options (cheap model)

**Do this before gap detection and before writing any plan.**

Using the cheapest available model, generate 2-3 distinct approaches to the evolution goal.
Each approach sketch is ~3-5 sentences: what it does, what it doesn't do, estimated effort,
key tradeoff.

**Model selection** (use first that is available per environment profile):

| Priority | Model | How to invoke |
|----------|-------|---------------|
| 1 | Copilot free tier (gpt-4o-mini) | `gh copilot suggest "<brainstorm prompt>"` |
| 2 | Gemini free tier (gemini-flash-2.0) | `gemini -m gemini-2.0-flash-exp "<brainstorm prompt>"` |
| 3 | Claude Haiku subagent | Spawn `Agent(subagent_type="haiku", prompt=...)` |

**Brainstorm prompt template:**
```
Evolution goal: <goal>
Target: <target skill/agent>
Current gaps detected: <gap list>

Generate exactly 3 distinct approaches to this evolution goal. For each:
- Approach name (2-4 words)
- What it does (2-3 sentences)
- What it trades off (1 sentence)
- Estimated effort: [Small / Medium / Large]
```

**Present options to user:**
```
Here are 3 approaches to <goal>:

**Option A — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

**Option B — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

**Option C — <name>** [<effort>]
<description>
Tradeoff: <tradeoff>

My recommendation: **Option <X>** — <one-line reason>.
Which would you like to proceed with? (A / B / C / modify)
```

Wait for the user to select before proceeding to Phase 2.

---

## Phase 2 — Gap Detection Lens

Once the approach is confirmed, read the target files and check for each gap below.
Each confirmed gap becomes one workstream:

| Check | Gap if... | Workstream type |
|-------|-----------|-----------------|
| `## Gotchas` section | absent from SKILL.md or agent file | Add Gotchas (3–5 field-derived patterns) |
| `## HANDOFF_BLOCK` in completion | absent from child skill completion section | Add HANDOFF_BLOCK code fence |
| `evals.json` | stub (< 6 cases) or REPLACE placeholders | Fill with real routing cases |
| Model identifiers | contain dashes (claude-sonnet-4-6) | Fix to dot notation |
| Domain patterns layer 

*(content truncated)*

## See Also

- [[task-dispatch-agent-uses-filesystem-tools-default-behaviour]]
- [[title-node-center]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-evolution-planner/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.711255+00:00
