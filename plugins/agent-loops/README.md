# Agent Loops

Composable agent loop architectures for **learning loops**, **agent orchestration**, **red team coordination**, and **parallel swarm execution**. Framework-agnostic — works with any AI agent in any repository, with or without other plugins.

## Core Skills

| Skill | Pattern | Description |
|-------|---------|-------------|
| **`orchestrator`** | Router | Assesses the trigger, selects the appropriate loop pattern, and manages shared closure (seal, persist, retro + self-improvement). |
| **`learning-loop`** | 1. Simple Learning | Self-directed research, document, iterate. No inner agents or review gates. |
| **`red-team-review`** | 2. Adversarial Review | Research → bundle context → red team review → iterate in rounds until approved. |
| **`dual-loop`** | 3. Inner/Outer Agent | Outer loop plans and delegates to an inner CLI agent via strategy packets, then verifies output. |
| **`agent-swarm`** | 4. Parallel Execution | Partition work → dispatch to N agents across isolated workspaces → verify and merge all. |

## How It Works

The orchestrator assesses the trigger (question, issue, research need, work assignment, review request) and routes to the appropriate pattern:

```
Trigger → Orchestrator → Which pattern?
  │
  ├── 1. Simple Learning Loop (solo, no agents)
  ├── 2. Red Team Review Loop (bundle + adversarial review rounds)
  ├── 3. Agent Orchestration (inner/outer delegation via CLI)
  └── 4. Agent Swarm (parallel execution across N workspaces)
  │
  └── Shared Closure: Seal → Persist → Retrospective → Improve Infrastructure
```

## Separation of Concerns

This plugin focuses on **loop execution patterns**. It does NOT own:

| Concern | Owned By | Relationship |
|---------|----------|-------------|
| Worktree / workspace creation | External tooling | Agent-loops receives a workspace and runs its pattern inside it. Works standalone. |
| Context bundling | `context-bundler` | Used by red-team-review and seal phases. **Required generic dependency.** |
| Memory synthesis | External utility | Used during orientation to load prior context. Optional dependency. |
| Remote archival (e.g., HuggingFace) | User's choice | Out of scope — external skill or manual step. |

> **Key Principle**: Agent-loops works standalone for basic activities. Complex patterns require the generic `context-bundler` utility.

## Directory Structure

```text
agent-loops/
├── .claude-plugin/      # Plugin manifest
├── hooks/               # Lifecycle hooks (closure enforcement)
├── personas/            # Specialized AI subagent configurations
├── resources/
│   ├── diagrams/        # Architecture diagrams (overview + per-pattern)
│   └── templates/       # Strategy packets, retrospective, audit templates
├── skills/
│   ├── orchestrator/    # Routes to patterns, manages closure
│   ├── learning-loop/   # Pattern 1
│   ├── red-team-review/ # Pattern 2
│   ├── dual-loop/       # Pattern 3
│   └── agent-swarm/     # Pattern 4
└── workflows/           # Pre-built loop workflows
```

## Diagrams

| Diagram | Shows |
|---------|-------|
| [agent_loops_overview.mmd](resources/diagrams/agent_loops_overview.mmd) | High-level routing to all 4 patterns |
| [learning_loop.mmd](resources/diagrams/learning_loop.mmd) | Pattern 1: Simple learning |
| [red_team_review_loop.mmd](resources/diagrams/red_team_review_loop.mmd) | Pattern 2: Adversarial review |
| [inner_outer_loop.mmd](resources/diagrams/inner_outer_loop.mmd) | Pattern 3: Dual-loop handoff |
| [agent_swarm.mmd](resources/diagrams/agent_swarm.mmd) | Pattern 4: Parallel swarm |

## Compatible Agents

The orchestration layer works with any CLI-invokable agent:
- **Anthropic**: Claude CLI (`claude`)
- **Google**: Gemini CLI (`gemini`)
- **GitHub**: Copilot CLI (`gh copilot`)
- **OpenHands**: OpenClaw / ClawdBot
- **Local**: Ollama, LM Studio, or any custom agent
