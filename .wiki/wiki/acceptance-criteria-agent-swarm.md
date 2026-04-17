---
concept: acceptance-criteria-agent-swarm
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/agent-swarm/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.710156+00:00
cluster: orchestrator
content_hash: 95efc2c36e00daf0
---

# Acceptance Criteria: Agent Swarm

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: Agent Swarm

## 1. Execution Boundary Constraints
- [ ] Orchestrator does NOT execute the payload commands itself. It strictly maps the jobs and invokes `../scripts/swarm_run.py`.
- [ ] The swarm partition strategy ensures that no two workers are modifying the same source code file simultaneously.

## 2. Resiliency & Scale
- [ ] The orchestrator implements the `--resume` flag on large batches to protect against partial system failures.
- [ ] The orchestrator strictly limits Copilot workers to `2` to prevent throttling, while allowing higher limits for Gemini/Claude.

## 3. Protocol Fidelity
- [ ] Target logic relies purely on injected shell post-commands and input passing without depending on the sub-agents having complex filesystem context.


## See Also

- [[agent-orchestrator-acceptance-criteria]]
- [[acceptance-criteria-create-sub-agent]]
- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-dependency-agent]]
- [[acceptance-criteria-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/agent-swarm/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:09.710156+00:00
