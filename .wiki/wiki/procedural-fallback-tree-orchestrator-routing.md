---
concept: procedural-fallback-tree-orchestrator-routing
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/orchestrator/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.137467+00:00
cluster: user
content_hash: d685bed7c06f7b70
---

# Procedural Fallback Tree: Orchestrator Routing

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Orchestrator Routing

## 1. Ambiguous Routing Signal
If the user's prompt (e.g., "Fix it") does not map cleanly to Research (Pattern 1), Review (Pattern 2), Execution (Pattern 3), or Parallelism (Pattern 4):
- **Action**: Do not guess. Default to Pattern 1 (Learning Loop) to synthesize the requirement. Ask the user 1 clarifying question to determine if code execution or review is actually needed.

## 2. Inner Loop Crashes (Timeout/Dependency)
If the delegated inner loop (whether dual-loop or swarm) crashes abruptly without returning a completed artifact or a status:
- **Action**: The Orchestrator reclaims control. It does NOT enter an infinite wait. It assesses the terminal output or log of the crash, generates a Correction Packet containing the crash trace, and attempts to re-delegate.

## 3. Sub-Agent Process Fails to Start
If `agent_orchestrator.py` or the environment fails to spawn the requested CLI subagent:
- **Action**: Present the generated Task Packet to the user directly in chat. Ask the user to instantiate the environment (e.g., another terminal window) and act as the bridge manually. 

## 4. Retrospective Cannot Be Generated
If the loop completes but the friction logs are empty or the agent lacks memory of what actually happened during the execution:
- **Action**: Generate an explicit 'Null Retrospective' noting that execution traces were lost. Prompt the user to confirm closure before passing control to the Primary Agent for the seal sequence.


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-learning-loop]]
- [[procedural-fallback-tree-red-team-review]]
- [[procedural-fallback-tree-plugin-analyzer]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/orchestrator/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.137467+00:00
