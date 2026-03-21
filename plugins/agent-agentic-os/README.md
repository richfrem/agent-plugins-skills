# Agent Agentic OS Plugin

> **Executive Summary**: For a conceptual overview of the architecture, OS analogy deep-dive, and key differentiators from a traditional operating system, read [`SUMMARY.md`](./SUMMARY.md) first.

## Purpose

`plugins/agent-agentic-os` is the canonical operational reference for the **Agentic OS / Agent Harness** pattern.

LLMs are stateless functions. `CLAUDE.md` is the only file loaded into every conversation by default. The Agentic OS pattern turns this constraint into a full OS metaphor: your `CLAUDE.md` files are the kernel, `context/` is persistent RAM, `skills/` is the standard library, and `/loop` is your cron daemon.

This plugin teaches agents how to:
- Understand and navigate the full CLAUDE.md hierarchy (global -> org -> project -> local)
- Structure and maintain the `context/` folder (soul, user prefs, dated memory logs)
- Use `.claude/agents/`, `.claude/hooks/`, and `.claude/commands/` effectively
- Run background scheduled tasks with `/loop` and `heartbeat.md`
- Bootstrap new sessions via `START_HERE.md` and `MEMORY.md`
- Manage memory hygiene: when to write, promote, archive, and expire

## Installation

### Option 1: From a Marketplace (Recommended)
If this plugin is listed in a marketplace catalog, add the marketplace first then install:
```bash
/plugin marketplace add <marketplace-url>
/plugin install agent-agentic-os
```
For skills-only portability across all agents (Claude, Gemini, Copilot, etc.):
```bash
npx skills add <marketplace-url>/plugins/agent-agentic-os
```

### Option 2: From GitHub Directly
```bash
# Skills only (portable, works with all agents)
npx skills add richfrem/agent-plugins-skills --path plugins/agent-agentic-os

# Full plugin (Claude Code native - skills + commands + agents + hooks)
/plugin marketplace add richfrem/agent-plugins-skills
/plugin install agent-agentic-os
```

### Option 3: Local Development Checkout
```bash
# Skills only
npx skills add ./plugins/agent-agentic-os

# Full plugin
/plugin marketplace add ./
/plugin install agent-agentic-os
```

**Note:** This plugin installs with **standard library only** (no external dependencies). See `requirements.txt` for details.

## Supervised Learning & Improvement Loop (Karpathy Parity)

The Agentic OS implements a rigorous, objective self-improvement loop inspired by Andrej Karpathy's `autoresearch`:

- **Objective Metrics (The Trainer)**: `skill-improvement-eval` uses `eval_runner.py` to calculate routing accuracy against a fixed validation set (`evals/evals.json`). A change is only kept if it improves the objective score.
- **Persistent Benchmarking**: All evaluation results are recorded in `evals/results.tsv` (commit, score, status), establishing a clear baseline for every skill.
- **Autonomous Supervision**: The `post_run_metrics.py` hook automatically captures session errors and friction events, emitting them to the Event Bus (`events.jsonl`) without human intervention.
- **Optimization Strategy**: Agents should follow the [Skill Optimization Guide](references/skill_optimization_guide.md) to achieve high routing accuracy through scoped keywords and diversity in `<example>` blocks.

## Part of the Triad

| Plugin | Role |
|--------|------|
| `agent-skill-open-specifications` | Spec - what ecosystem artifacts are |
| `agent-scaffolders` | Factory - how to create them |
| **`agent-agentic-os`** | **Operations - how to run the environment** |

## Plugin Components

### Skills

- **`agentic-os-guide`**: Master reference skill. The full anatomy of the Agentic OS pattern - all layers and their interactions.
- **`agentic-os-init`**: The core execution script and interview framework to scaffold a new OS environment.
- **`session-memory-manager`**: Operational skill for managing memory hygiene across sessions.
- **`os-clean-locks`**: System administration utility to cleanly remove stale agent locks and prevent deadlocks.
- **`skill-improvement-eval`**: QA evaluation engine mimicking Anthropic's benchmark suites to rigorously gate self-modifying autonomous behaviors.

### Agents

- **`agentic-os-setup`**: A persistent conversational architect that wraps the `agentic-os-init` skill to guide users through discovery, component planning, and post-init CLAUDE.md filling.
- **`os-learning-loop`**: The continuous improvement engine. Performs post-session retrospectives to identify friction points and writes permanent updates to skills and memory conventions.

## Kernel Architecture (v10+)

The OS operates on a centralized Python-based event bus (`context/kernel.py`) instead of relying solely on reactive filesystem reads:
- **Event Bus (`events.jsonl`)**: All agents publish their intents, results, and errors to the event bus using strict JSON schemas.
- **Atomic Concurrency**: The kernel uses atomic locks (`os.mkdir()`) to prevent race conditions during memory promotion or learning cycles.
- **Agent Registry**: Security validation via `agents.json` ensures only whitelisted sub-agents can mutate the OS state.

## Directory Structure

```text
agent-agentic-os
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── CONNECTORS.md
│   ├── README.md
│   ├── SUMMARY.md
│   ├── agent-agentic-os-architecture.mmd
│   ├── agents/
│   │   ├── agentic-os-setup.md
│   │   ├── os-health-check.md
│   │   └── os-learning-loop.md
│   ├── commands/
│   │   ├── os-init.md
│   │   ├── os-loop.md
│   │   └── os-memory.md
│   ├── hooks/
│   │   ├── hooks.json
│   │   ├── update_memory.py
│   │   └── scripts/
│   │       └── post_run_metrics.py
│   ├── lsp.json
│   ├── references/
│   │   ├── anthropic-official-docs.md
│   │   ├── metrics.md
│   │   ├── post_run_survey.md
│   │   ├── skill_optimization_guide.md
│   │   ├── status-file-spec.md
│   │   └── diagrams/
│   │       ├── agentic-os-loop-lifecycle.mmd / .png
│   │       ├── agentic-os-memory-subsystem.mmd / .png
│   │       ├── agentic-os-overview.mmd / .png
│   │       ├── agentic-os-structure.mmd / .png
│   │       ├── agentic-os-system-architecture.mmd / .png
│   │       └── event-bus-architecture.mmd
│   ├── requirements.in
│   └── skills/
│       ├── agentic-os-guide/
│       │   ├── CONNECTORS.md
│       │   ├── SKILL.md
│       │   ├── agentic-os-guide-flow.mmd
│       │   ├── evals/
│       │   │   ├── evals.json
│       │   │   └── results.tsv
│       │   └── references/
│       │       ├── acceptance-criteria.md
│       │       ├── architecture.md
│       │       ├── canonical-file-structure.md
│       │       ├── claude-md-hierarchy.md
│       │       ├── context-folder-patterns.md
│       │       ├── loop-scheduler.md
│       │       ├── memory-hygiene.md
│       │       └── sub-agents-and-hooks.md
│       ├── agentic-os-init/
│       │   ├── CONNECTORS.md
│       │   ├── SKILL.md
│       │   ├── agentic-os-init-flow.mmd
│       │   ├── evals/
│       │   │   ├── evals.json
│       │   │   └── results.tsv
│       │   ├── references/
│       │   │   ├── acceptance-criteria.md
│       │   │   ├── architecture.md
│       │   │   └── project-setup-guide.md
│       │   ├── runtime/
│       │   │   ├── agents.json        <- kernel agent permit list
│       │   │   └── kernel.py          <- atomic lock + event bus controller
│       │   ├── scripts/
│       │   │   └── init_agentic_os.py
│       │   └── templates/
│       ├── os-clean-locks/
│       │   ├── SKILL.md
│       │   ├── evals/
│       │   │   └── evals.json
│       │   └── references/
│       │       └── acceptance-criteria.md
│       ├── session-memory-manager/
│       │   ├── CONNECTORS.md
│       │   ├── SKILL.md
│       │   ├── evals/
│       │   │   ├── evals.json
│       │   │   └── results.tsv
│       │   ├── references/
│       │   │   ├── acceptance-criteria.md
│       │   │   ├── architecture.md
│       │   │   └── memory-promotion-guide.md
│       │   └── session-memory-manager-flow.mmd
│       ├── skill-improvement-eval/
│       │   ├── SKILL.md
│       │   ├── evals/
│       │   │   └── evals.json
│       │   ├── references/
│       │   │   ├── acceptance-criteria.md
│       │   │   └── optimizer-engine-patterns.md
│       │   └── scripts/
│       │       └── eval_runner.py
│       └── todo-check/
│           ├── SKILL.md
│           ├── evals/
│           │   └── evals.json
│           └── scripts/
│               └── check_todos.py
```

## Architecture Visualizations

### 1. Conceptual OS Structure
How the `agent-agentic-os` concepts map logically to a standard operating system.
![Agentic OS Logical Architecture](./references/diagrams/agentic-os-overview.png)

### 2. Physical Plugin Architecture
How the individual data layers, processes, and hooks inside this code repository interact.
![Agentic OS Plugin Architecture](./references/diagrams/agentic-os-structure.png)

### 3. Loop Lifecycle
Sequence mapping how the scheduled `/loop` cron interacts with the status queue and triggers internal handlers.
![Agentic OS Loop Architecture](./references/diagrams/agentic-os-loop-lifecycle.png)

### 4. Memory Promotion Subsystem
Flowchart portraying how raw logs are transitioned from short-term memory arrays to clean L3 curated rulesets.
![Agentic OS Memory Architecture](./references/diagrams/agentic-os-memory-subsystem.png)

## Key References

- [Executive Summary & OS Analogy](./SUMMARY.md) — conceptual architecture, analogy table, and key differentiators
- [Anthropic CLAUDE.md documentation](https://docs.anthropic.com/en/docs/claude-code/memory)
- [Anthropic /loop scheduler](https://docs.anthropic.com/en/docs/claude-code/loop)
- [Agent Skills Open Standard](https://agentskills.io)
