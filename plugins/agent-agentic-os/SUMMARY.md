# Agentic OS: Summary

## What This Is

A developer harness that gives your agent three things working together as a system:

1. **Persistent memory** - agents carry forward what they learned in previous sessions instead of rediscovering it every time
2. **Improvement loops** - skills, instructions, and CLAUDE.md files get measurably better on every run through a reinforcement + supervised learning cycle at the instruction layer
3. **Multi-agent coordination** - multiple agents share a common memory bus and event log so they build on each other's work rather than running in isolation

This is not an enterprise product. It is a developer-grade lab tool that demonstrates patterns the industry is converging on. Frontier labs are expected to absorb these capabilities into their platforms natively - this fills the gap in the meantime and provides a working reference for what those platforms will need to get right.

## The Gap It Fills

LLMs are stateless. Every session starts from scratch unless you deliberately carry context forward. Most developers handle this informally - copying notes into CLAUDE.md, re-explaining decisions to the agent, re-running the same setup steps. That works for a few sessions. It breaks down when you have multiple agents, background loops, and workflows that span days or weeks.

The problem isn't just memory. It's coordination: how does the background improvement agent share what it learned with the foreground session agent? How does the outer-loop supervisor pass context to the inner-loop worker? How do you prevent two agents writing to the same memory file at the same time from corrupting it?

This plugin provides a system for that - not just primitives you assemble yourself.

## The Self-Improvement Loop (The Differentiator)

Many tools add memory to agents. Fewer implement an improvement loop. This one runs a reinforcement + supervised learning cycle at the **instruction level** - not training model weights, but continuously improving the instructions the model receives.

How it works:

```
Session runs -> errors and friction captured to events.jsonl
             -> os-learning-loop mines the event log
             -> proposes patches to SKILL.md files and CLAUDE.md
             -> skill-improvement-eval scores the patch against evals/evals.json
             -> patch kept only if objective score improves
             -> next session inherits better instructions
```

The validator (`eval_runner.py`) is the supervised part: changes must pass an objective benchmark before they are applied. The loop is the reinforcement part: friction in use generates the training signal. Together they create an improvement flywheel that runs without human intervention.

The Agentic OS plugin applies this loop to its own skills. The plugin improves itself using the same mechanism it teaches. That makes it a live lab: observing how it works here is directly applicable to any project that installs it.

## Multi-Agent Coordination Patterns

The core coordination patterns this plugin enables:

**Inner/outer loop** - the outer loop is a supervisor (human or orchestrator agent) that sets goals and reviews results. The inner loop is a worker agent that executes. The outer loop passes context via shared memory; the inner loop writes results back to the event bus. Neither needs to know the other's implementation.

**Background + foreground** - a foreground session agent does active work while a background daemon (`os-learning-loop`, `os-health-check`) runs asynchronously. Mutex locks prevent collisions. The background agent's findings are available to the foreground agent in the next session through promoted memory.

**Sequential agent handoff** - agent A completes a phase and writes structured output to the event bus. Agent B picks up where A left off by reading the bus, not by being told what A did. No tight coupling; agents are swappable.

What makes this a system and not just primitives: all three patterns share the same memory bus (`events.jsonl`) and the same memory hierarchy (L2 session logs -> L3 curated memory). A learning signal from the inner loop benefits the outer loop's next run. A finding from the background daemon is available to foreground agents. The coordination is built in.

## Scope and Honest Limits

- **Single developer, single machine** - designed for this use case, tested for this use case
- **File system is the backend** - no databases, no message queues, no external dependencies
- **No scale requirements** - if you need multi-machine coordination or high-throughput event streaming, this is not the tool; see `references/vision.md` for what that would require
- **Academic/research quality** - deliberate. The goal is clarity of implementation, not production hardening
- **Explicitly transitional** - Microsoft, Apple, NVIDIA, and the frontier labs (Anthropic, OpenAI, Google) are building native agentic OS capabilities. Some of these will ship within months. This plugin demonstrates what they need to get right; it is not trying to compete with what they will build

## How It Works: The OS Analogy

The OS metaphor explains the design decisions. The context window is finite RAM - every byte consumed by infrastructure is a byte unavailable for actual work. The architecture is designed around that constraint.

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
| Self-updating software | `os-learning-loop` + `skill-improvement-eval` |
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

- **Memory runs automatically** - session logs are written at the end of each session; the `session-memory-manager` promotes important facts to long-term memory
- **Loops run on command** - run `/os-loop` to trigger a retrospective that mines the event log and proposes skill improvements
- **Health checks on demand** - run `os-health-check` to inspect system state, event log, and memory integrity

The improvement flywheel starts generating useful signal after a few sessions. By session ten, the skills and CLAUDE.md instructions are meaningfully more accurate for your specific workflow than they were at install.
