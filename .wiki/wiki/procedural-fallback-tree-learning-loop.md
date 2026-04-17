---
concept: procedural-fallback-tree-learning-loop
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/learning-loop/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.105562+00:00
cluster: phase
content_hash: 3dcd6a47b1d217de
---

# Procedural Fallback Tree: Learning Loop

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Learning Loop

## 1. Context Snapshot Is Missing
If during Phase I (Orientation) the agent cannot find the expected `snapshot.md` or session state file:
- **Action**: Do not invent context. Ask the user if this is a fresh project (in which case, create the initial orientation docs) or if the state file is located elsewhere. Do not proceed to Synthesis without establishing the baseline.

## 2. User Denies "Proceed" at Strategic Gate
If during Phase III (HITL) the user rejects the architectural findings or proposed strategy:
- **Action**: Backtrack to Phase II (Synthesis). Ask the user for specific directional constraints, rewrite the research artifacts, and present the new findings at the Strategic Gate again.

## 3. Red Team Auditor Subagent Fails to Boot
If during Phase IV the attempt to spawn an adversarial CLI subagent (e.g., via `claude-cli-agent`) fails due to auth or pathing issues:
- **Action**: Provide the context bundle directly to the User in the chat and ask them to perform the Red Team Review manually. Do not bypass the audit phase just because the subagent failed.

## 4. Forced Premature Exit
If the user abruptly says "stop" or "end session here":
- **Action**: Immediately jump to Phase V (Completion & Handoff). Compile whatever partial synthesis exists, issue the Orchestrator handoff statement, and terminate. Never leave a session completely unsealed without attempting a graceful handoff.


## See Also

- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-orchestrator-routing]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/learning-loop/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.105562+00:00
