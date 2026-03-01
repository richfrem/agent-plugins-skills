---
name: agent-swarm
description: "Parallel multi-agent execution pattern. Use when: work can be partitioned into independent tasks that N agents can execute simultaneously across worktrees. Includes routing (sequential vs parallel), merge verification, and correction loops."
---

# Agent Swarm

Parallel or pipelined execution across multiple agents and worktrees. The orchestrator partitions work, dispatches to agents, and verifies/merges the results.

## When to Use

- Large features that can be split into independent work packages
- Bulk operations (tests, docs, migrations) that benefit from parallelism
- Multi-concern work where specialists handle different aspects simultaneously

## Process Flow

1. **Plan & Partition** — Break work into independent tasks. Define boundaries clearly.
2. **Route** — Decide execution mode:
   - **Sequential Pipeline** — Tasks depend on each other (A → B → C)
   - **Parallel Swarm** — Tasks are independent (A | B | C)
3. **Dispatch** — Create a worktree per task. Assign each to an agent:
   - CLI agent (Claude, Gemini, Copilot)
   - Deterministic script
   - Human
4. **Execute** — Each agent works in isolation. No cross-worktree communication.
5. **Verify & Merge** — Orchestrator checks each worktree's output against acceptance criteria.
   - **Pass** → Merge into main branch
   - **Fail** → Generate correction packet, re-dispatch
6. **Seal** — Bundle all merged artifacts
7. **Retrospective** — Did the partition strategy work? Was parallelism effective?

## Worker Selection

Each worktree can be assigned to a different worker type based on task complexity:

| Worker | Best For |
|--------|---------|
| **High-reasoning CLI** (Opus, Ultra) | Complex logic, architecture |
| **Fast CLI** (Haiku, Flash) | Tests, docs, routine tasks |
| **Specialist CLI** | Security audit, QA, DB migration |
| **Deterministic Script** | Formatting, linting, data transforms |
| **Human** | Judgment calls, creative decisions |

## Implementation: swarm_run.py

The **swarm_run.py** script is the universal engine for executing this pattern. It is driven by **Job Files** (.md with YAML frontmatter).

### Key Features

- **Resume Support** — Automatically saves state to `.swarm_state_<job>.json`. Use `--resume` to skip already processed items.
- **Intelligent Retry** — Exponential backoff for rate limits.
- **Verification Skip** — Use `check_cmd` in the job file to short-circuit work if a file is already processed (e.g. exists in cache).
- **Dry Run** — Test your file discovery and template substitution without cost.

### Usage

```bash
python3 plugins/agent-loops/skills/agent-swarm/scripts/swarm_run.py \
    --job plugins/rlm-factory/resources/jobs/rlm_chronicle.job.md \
    [--dir some/dir] [--resume] [--dry-run]
```

### Job File Schema

```yaml
---
model: haiku        # haiku, sonnet, opus
workers: 10         # parallelism
timeout: 120        # seconds per worker
ext: [".md"]        # filters for --dir
# Shell template. {file}, {output}, {basename}, {var}
post_cmd: "python3 plugins/rlm-factory/skills/rlm-curator/scripts/inject_summary.py --file {file} --summary {output}"
# Optional command to check if work is already done (exit 0 => skip)
check_cmd: "python3 plugins/rlm-factory/skills/rlm-curator/scripts/check_cache.py --file {file}"
vars:
  profile: project
---
Prompt for Claude goes here.
```

## Constraints

- Each worker execution must be independent
- Post-commands must be idempotent if using resume
- Orchestrator owns the overall job state

## Diagram

See: [plugins/agent-loops/resources/diagrams/agent_swarm.mmd](plugins/agent-loops/resources/diagrams/agent_swarm.mmd)


