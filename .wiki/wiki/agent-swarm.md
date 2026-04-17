---
concept: agent-swarm
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/agent-swarm/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.709246+00:00
cluster: work
content_hash: 0ab254b7ee152845
---

# Agent Swarm

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: agent-swarm
description: "(Industry standard: Parallel Agent) Primary Use Case: Work that can be partitioned into independent sub-tasks running concurrently across multiple agents. Parallel multi-agent execution pattern. Use when: work can be partitioned into independent tasks that N agents can execute simultaneously across worktrees. Includes routing (sequential vs parallel), merge verification, and correction loops."
allowed-tools: Bash, Read, Write
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `../../requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Agent Swarm

Parallel or pipelined execution across multiple agents and worktrees. The orchestrator partitions work, dispatches to agents, and verifies/merges the results.

## When to Use

- Large features that can be split into independent work packages
- Bulk operations (tests, docs, migrations, RLM distillation) that benefit from parallelism
- Multi-concern work where specialists handle different aspects simultaneously

## Process Flow

1. **Plan & Partition** -- Break work into independent tasks. Define boundaries clearly.
2. **Route** -- Decide execution mode:
   - **Sequential Pipeline** -- Tasks depend on each other (A -> B -> C)
   - **Parallel Swarm** -- Tasks are independent (A | B | C)
3. **Dispatch** -- Create a worktree per task. Assign each to an agent:
   - CLI agent (Claude, Gemini, Copilot)
   - Deterministic script
   - Human
4. **Execute** -- Each agent works in isolation. No cross-worktree communication.
5. **Verify & Merge** -- Orchestrator checks each worktree's output against acceptance criteria.
   - **Pass** -> Merge into main branch
   - **Fail** -> Generate correction packet, re-dispatch
6. **Seal** -- Bundle all merged artifacts
7. **Retrospective** -- Did the partition strategy work? Was parallelism effective?

## Worker Selection

Each worktree can be assigned to a different worker type based on task complexity:

| Worker | Cost | Best For |
|--------|------|----------|
| **High-reasoning CLI** (Opus, Ultra, GPT-5.3) | High | Complex logic, architecture |
| **Fast CLI** (Haiku, Flash 2.0) | Low | Tests, docs, routine tasks |
| **Free Tier: Copilot gpt-5-mini** | **$0** | Bulk summarization, zero-cost batch jobs |
| **Free Tier: Gemini gemini-3-pro-preview** | **$0** | Large context batch jobs |
| **Deterministic Script** | None | Formatting, linting, data transforms |
| **Human** | N/A | Judgment calls, creative decisions |

> **Zero-Cost Batch Strategy**: For bulk summarization or distillation jobs, use `--engine copilot` (gpt-5-mini) or `--engine gemini` (gemini-3-pro-preview). Both are free-tier models available via their respective CLIs. Gemini Flash 2.0 is also very cheap if more capacity is needed. Use `--workers 2` for Copilot (rate-limit safe) and `--workers 5` for Gemini.

## Implementation: ./../scripts/swarm_run.py

The **./../scripts/swarm_run.py** script is the universal engine for executing this pattern. It is driven by **Job Files** (.md with YAML frontmatter).

### Key Features

- **Resume Support** -- Automatically saves state to `.swarm_state_<job>.json`. Use `--resume` to skip already processed items.
- **Intelligent Retry** -- Exponential backoff for rate limits.
- **Verification Skip** -- Use `check_cmd` in the job file to short-circuit work if a file is already processed (e.g. exists in cache).
- **Dry Run** -- Test your file discovery and template substitution without cost.
- **Engine Flag** -- `--engine [claude|gemini|copilot]` switches CLI backends at runtime.

### Usage

```bash
# Zero-cost Copilot batch (2 workers recommended to avoid rate limits)
source ~/.zshrc   # NOTE: use source ~/.zshrc, NOT 'export COPILOT_GITHUB_TOKEN=$(gh auth token)'
                  # gh auth token ge

*(content truncated)*

## See Also

- [[acceptance-criteria-agent-swarm]]
- [[procedural-fallback-tree-agent-swarm]]
- [[acceptance-criteria-agent-swarm]]
- [[procedural-fallback-tree-agent-swarm]]
- [[acceptance-criteria-agent-swarm]]
- [[procedural-fallback-tree-agent-swarm]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/agent-swarm/SKILL.md`
- **Indexed:** 2026-04-17T06:42:09.709246+00:00
