# Agent Harness: Summary

## What This Is

A pragmatic developer harness that gives your agent three things working together:

1. **Structured memory hierarchy** - agents carry forward what they learned in previous sessions with deduplication, conflict detection, and size management above native auto-memory limits.
2. **Continuous improvement loop** - skills and workflows learn from session friction and improve with every execution. It leverages a feedback control system with a metric-based gate.
3. **Cross-IDE orchestration** - a shared event log with simple execution locks allows solo developers to comfortably orchestrate things across multiple IDEs (Cursor, VS Code, Windsurf) while preventing collisions.

Claude Code ships auto-memory, native hooks, and subagent coordination. This plugin provides an **opinionated discipline layer** on top of those primitives to connect different workspaces.

## Who This Is For

Developers running **long-horizon, multi-session workflows** — projects where Claude Code runs across days or weeks, multiple agents share context, and the quality of what gets remembered and improved directly affects every future session.

Not for single-session tasks (native auto-memory is enough), enterprise multi-machine deployments, or framework-agnostic portability requirements.

## The Feedback and Learning Layer (The Differentiator)

While many tools add memory to agents, fewer implement a true feedback control system. This plugin operates as a **learning layer for agent workflows**, running a reinforcement + supervised learning cycle at the **instruction level**.

How it works:

```text
Session runs -> errors and friction captured to events.jsonl
             -> Triple-Loop Orchestrator formulates learning hypothesis for a SKILL.md
             -> eval_runner.py (The Headless Evaluator) scores it against static evals/evals.json fixtures
             -> if DISCARD, agent automatically reverts via `git reset --hard`
             -> if KEEP, the improved instruction is retained for the next session
```

A **test registry** prevents re-testing falsified hypotheses so improvement cycles don't repeat dead ends.

> **Note on Architecture:** The system strictly implements the **Karpathy 3-File Autoresearch Framework**. This replaces earlier experimental proxy heuristics with a rigorous headless evaluation relying purely on `eval_runner.py` and static `evals.json`. Subjective "LLM mental testing" is strictly prohibited to combat "Agent Dementia" (Goodhart's Law).

**⚠️ Current Safety Limits:** While the keyword bloat issue is solved by headless baseline testing, the loop still operates directly in the developer's workspace without a heavily isolated sandbox mode. The agent's strict `git reset --hard` mandate mitigates risk, but it is not a true parallel shadow execution environment.

The validator (`eval_runner.py`) provides the supervised part: changes **must** pass an objective benchmark before they are applied. The loop is the reinforcement part: friction in use generates the training signal.

The Agentic OS plugin applies this loop to its own skills. The plugin improves itself using the same mechanism it teaches — a live demonstration, not documentation.

## Agent Signaling Patterns

The core turn-management patterns this plugin enables:

**Triple-Loop Learning System** - A unified architectural model where the outer loop (Orchestrator) is a supervisor that sets goals, manages memory, and triggers evaluation runs overnight. The inner loops (Strategic Planner and Tactical Executor) handle the iterative patching of code/skills. The entire stack communicates via shared memory and event logs without tight coupling.

**Background + foreground** - a foreground session agent does active work while a background agent (`os-learning-loop`, `os-health-check`) runs asynchronously. Simple locks prevent collisions. The background agent's findings are available to the foreground agent in the next session through promoted memory.

**Sequential agent handoff** - agent A completes a phase and writes a completion state to the event log. Agent B picks up where A left off by reading the log, not by being told what A did. No tight coupling; agents are swappable.

What ties these patterns together is that all three share the same event log (`events.jsonl`) and the same memory hierarchy (L2 session logs -> L3 curated memory). A learning signal from the inner loop benefits the outer loop's next run. A finding from the background agent is available to foreground agents.

## Scope and Honest Limits

- **Single developer, single machine** - designed for this use case, tested for this use case
- **File system is the backend** - no databases, no message queues, no external dependencies
- **No scale requirements** - if you need multi-machine coordination or high-throughput event streaming, this is not the tool; see `references/vision.md` for what that would require
- **Academic/research quality** - deliberate. The goal is clarity of implementation, not production hardening
- **Complementary to native Claude Code** - Anthropic has shipped auto-memory, hooks, and subagent coordination. This plugin adds the structured memory hierarchy, eval-gated improvement loop, and event bus coordination on top of those native primitives — not competing with them

## How It Works: The Environment Harness (Formerly 'Agentic OS')

The original design leaned heavily on an operating system metaphor to explain design decisions. While technically it's a feedback and learning layer rather than a true distributed OS, the mental model helps explain the architecture. The context window is finite RAM - every byte consumed by infrastructure is a byte unavailable for actual work. The architecture is designed around that constraint.

| Real OS | Agentic OS |
|---------|------------|
| Kernel | `CLAUDE.md` + `kernel.py` - rules loaded every session + concurrency manager |
| RAM (finite, clears on shutdown) | Active context window - finite, clears every session |
| Always in RAM | Skill metadata headers, agent descriptions, `CLAUDE.md`, `soul.md`, `user.md` |
| Application on disk | Full `SKILL.md` body - stays on disk until that skill is triggered |
| App launcher | Skill metadata descriptions - scanned to route to the right skill |
| Opening an application | A skill triggering - full body loads into context window |
| Library loaded on demand | `references/` files via progressive disclosure - only the specific doc, only when needed |
| Background daemon | `os-learning-loop`, `os-health-check` - runs, acquires lock, does work, terminates |
| Cron scheduler | `/loop` + `heartbeat.md` |
| Working files | `context/memory/YYYY-MM-DD.md` session logs (L2) |
| Permanent storage | `context/memory.md` (L3) - curated facts |
| System event log | `context/events.jsonl` |
| Mutex / process lock | `context/.locks/` + `kernel.py` |
| Self-updating software | `os-learning-loop` + `os-eval-runner` |
| **No OS equivalent** | **Instruction-level self-improvement** - the system rewrites its own SKILL.md and CLAUDE.md based on observed usage |
| **No OS equivalent** | **LLM reasoning engine** - the CPU follows instructions; the LLM understands intent, fills gaps, and generates new skills on demand |

### Three-Tier Lazy Loading

The architecture enforces three tiers to protect working memory:

| Tier | What | When it enters context |
|------|------|----------------------|
| Always loaded | Skill metadata headers, agent descriptions, `CLAUDE.md`, `soul.md`, `user.md` | Every session |
| Loaded on trigger | Full `SKILL.md` body | Only when that skill is invoked |
| Loaded on demand | `references/` documents | Only when a specific sub-topic is needed |
| Never auto-loaded | `context/events.jsonl`, session logs | Only when explicitly read for audit/diagnosis |

This is why `CLAUDE.md` has a 300-line discipline and skill descriptions are deliberately tight. Infrastructure should not consume the context window. The agent's working memory should be available for actual work.

## How to Use It

Install the plugin, then ask your agent to "set up an agentic OS" or "run the agentic-os-setup agent." The setup agent runs a discovery interview and scaffolds the environment for your project. After that:

- **Memory runs automatically** - session logs are written at the end of each session; the `os-memory-manager` promotes important facts to long-term memory
- **Loops run on command** - run `/os-loop` to trigger a retrospective that mines the event log and proposes skill improvements
- **Health checks on demand** - run `os-health-check` to inspect system state, event log, and memory integrity

The improvement flywheel starts generating useful signal after a few sessions. By session ten, the skills and CLAUDE.md instructions are meaningfully more accurate for your specific workflow than they were at install.
