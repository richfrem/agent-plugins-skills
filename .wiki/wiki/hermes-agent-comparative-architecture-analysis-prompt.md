---
concept: hermes-agent-comparative-architecture-analysis-prompt
source: research-docs
source_file: hermes-agent/analysis-prompt.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.453764+00:00
cluster: richfrem
content_hash: 94778c464de821c9
---

# Hermes Agent: Comparative Architecture Analysis Prompt

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Hermes Agent: Comparative Architecture Analysis Prompt

**Model target:** Claude Sonnet (claude-cli)
**Source repo:** https://github.com/nousresearch/hermes-agent
**Local copy:** `temp/hermes-agent/`
**Output directory:** `plugin-research/hermes-agent/`

---

## Important Context Before You Begin

Hermes Agent is NOT a Claude Code plugin ecosystem. It is a standalone Python
agent runtime built by Nous Research. You are comparing two fundamentally
different architectural tiers:

- **richfrem plugins** (agent-agentic-os, exploration-cycle-plugin): Skill/plugin
  ecosystems built on top of existing IDE agents (Claude Code, Antigravity, Copilot).
  They extend what those agents can do through markdown-first Skills and commands.

- **Hermes Agent**: A full Python agent runtime -- its own execution engine, state
  machine, tool composition system, model routing, context compression, and
  multi-agent coordination layer.

These are different layers of the stack. Your analysis must be honest about this
difference. Do NOT treat missing features as gaps -- instead, ask: "What
architectural patterns or philosophies in Hermes are worth borrowing?"

---

## Step 1: Read and Internalize the Systems

### Plugin A: agent-agentic-os (richfrem)
```
plugins/agent-agentic-os/
```
Priority files:
- `README.md` and `SUMMARY.md`
- All `skills/` subdirectories (each SKILL.md)
- All `agents/` files
- All `commands/` files
- `hooks/hooks.json`
- `references/` directory

### Plugin B: exploration-cycle-plugin (richfrem)
```
plugins/exploration-cycle-plugin/
```
Priority files:
- `README.md`
- All `skills/` subdirectories
- All `agents/` files
- All `commands/` files
- `references/` and `templates/` directories

### System C: Hermes Agent (Nous Research)
```
temp/hermes-agent/ which is a clone of https://github.com/nousresearch/hermes-agent
```

Read these files in this order -- stop after each group and process before
continuing (this is a large repo and you need to be selective):

**Group 1 -- Architecture and Philosophy (read first):**
- `README.md`
- `AGENTS.md` (17KB -- this is the core agent protocol and working conventions)
- `RELEASE_v0.2.0.md`, `RELEASE_v0.3.0.md`, `RELEASE_v0.4.0.md` (skim for
  architectural decisions and evolution -- these are high signal)

**Group 2 -- Core Runtime (read selectively):**
- `hermes_state.py` (50KB state machine -- read the class definitions and
  docstrings, not line-by-line)
- `agent/smart_model_routing.py` (how it routes between models)
- `agent/context_compressor.py` (context management approach)
- `agent/prompt_builder.py` (how prompts are constructed)
- `agent/skill_commands.py` (how skills integrate into the runtime)
- `toolsets.py` (tool composition -- read class definitions and organization)

**Group 3 -- Skill Organization (sample, do not read all 26 categories):**
- `skills/software-development/` -- one full category read
- `skills/research/` -- one full category read
- `skills/autonomous-ai-agents/` -- one full category read
- `optional-skills/DESCRIPTION.md`

**Group 4 -- Multi-Agent and Coordination:**
- `honcho_integration/` (if present -- multi-agent framework integration)
- `acp_adapter/` directory listing and any README (Agent Communication Protocol)
- `.plans/` and `plans/` directory overview

---

## Step 2: Produce the Analysis Report

Save all outputs to `plugin-research/hermes-agent/`. One file per output.

---

### Output 1: `architectural-tier-comparison.md`

**Frame this as a layer-cake diagram (text)** showing where Hermes and richfrem
plugins sit in the stack:

```
[ LLM Model Layer ]
[ Agent Runtime Layer ] <-- Hermes lives here
[ Plugin/Skill Layer  ] <-- richfrem plugins live here
[ IDE / CLI Layer     ]
```

Then answer for each layer:
- What does Hermes implement at this layer?
- What does richfrem implement at this layer?
- Where do they overlap? Where are they complementary?
- What does richfrem assume exists at the layer below (that Hermes builds itself)?

This framing prev

*(content truncated)*

## See Also

- [[gstack-comparative-architecture-analysis-prompt]]
- [[paperclip-comparative-architecture-analysis-prompt]]
- [[superpowers-vs-mine-comparative-analysis-prompt]]
- [[agent-plugin-analyzer---architecture]]
- [[agent-creation-prompt]]
- [[strategic-analysis-agent-skills-ecosystem-in-azure]]

## Raw Source

- **Source:** `research-docs`
- **File:** `hermes-agent/analysis-prompt.md`
- **Indexed:** 2026-04-17T06:42:10.453764+00:00
