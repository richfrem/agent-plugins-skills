---
concept: agent-orchestrator-acceptance-criteria
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/orchestrator/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.136131+00:00
cluster: must
content_hash: d6668eb9bf188243
---

# Agent Orchestrator Acceptance Criteria

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Orchestrator Acceptance Criteria

To pass Open Standard certification, the `agent-orchestrator` plugin must dynamically instantiate hierarchical loops independently of global `.agents/` state tracking directories.

## Core Rules
1. Must natively execute the `./agent_orchestrator.py` script directly without legacy slash-command wrappers.
2. Must not assume the existence of external branch dependencies or global templates.
3. Must generate `handoffs/` and `retros/` dynamically in the active Project Runtime.
4. Orchestrator must be able to act autonomously to verify output against provided prompt packets utilizing the `verify` command.


## See Also

- [[acceptance-criteria-agent-swarm]]
- [[acceptance-criteria-create-sub-agent]]
- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-dependency-agent]]
- [[acceptance-criteria-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/orchestrator/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.136131+00:00
