---
concept: agent-loops-pattern-guide
source: plugin-code
source_file: agent-loops/references/PATTERN_GUIDE.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.220405+00:00
cluster: pros
content_hash: 1eef7ae12779d167
---

# Agent Loops: Pattern Guide

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Agent Loops: Pattern Guide

This guide maps the Agent-Loops skills to standard industry terminology (e.g., Google ADK patterns) and provides a comparative reference for when and how to use them.

## Overview of Patterns

| Our Skill | Industry Alias | Primary Use Case |
| :--- | :--- | :--- |
| `learning-loop` | Single Agent / Loop Agent | Self-contained research, content generation, and exploration where no inner delegation is required. |
| `dual-loop` | Sequential Agent / Agent as a Tool | Delegating a well-defined task to a worker agent, verifying its execution, and repeating if necessary. |
| `agent-swarm` | Parallel Agent | Work that can be partitioned into independent sub-tasks running concurrently across multiple agents. |
| `orchestrator` | Routing Agent / Hierarchical | Analyzing an ambiguous trigger and routing it to one of the specific specialized implementations above. |
| `red-team-review` | Review and Critique Pattern | Iterative generation paired with adversarial review, continuing until an "Approved" verdict is reached. |
| `triple-loop-learning` | Meta-Learning System | Continuous, unguided self-improvement of agent processes through rigorous objective headless testing, iterating on prompts and system skills from logged friction. |

---

## 1. Single Agent / Loop Agent (`learning-loop`)

The foundational pattern where a single agent repeatedly interacts with the environment (tools, research) to synthesize knowledge.

![Learning Loop / Single Agent Architecture](resources/diagrams/learning_loop.png)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Simple to implement** and highly flexible | **Large system prompts** can become unwieldy over time |
| **Easier to debug** given the linear, single-context trace | **Harder to re-use** individual components |
| **Low latency** for immediate or simple tasks | **Single point of failure** and lacks structural oversight |

### When to Use
Use when a task requires pure exploratory research, basic document generation, or knowledge retrieval, and the outcome does not critically risk the codebase.

---

## 2. Sequential Agent / Agent as a Tool (`dual-loop`)

An outer/manager agent defines a strategy packet, hands it to an inner/worker agent, and verifies the output before continuing.

![Sequential Agent / Dual Loop Architecture](resources/diagrams/inner_outer_loop.png)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **More predictable execution** via manager oversight | **Inflexible**: cannot easily skip steps without explicit manager instruction |
| **Easier to test and debug** isolated worker packets | **Cumulative latency**: sub-agent must finish before manager verifies |
| **Fewer LLM calls** compared to an unstructured loop, lowering cost | Requires strict boundaries to prevent context contamination |

### When to Use
Use for feature implementations or bug fixes where a clear specification exists. The inner agent acts exclusively as an execution tool, isolated from the overarching Git architecture.

---

## 3. Parallel Agent (`agent-swarm`)

Tasks are partitioned into independent chunks and delegated to N agents executing simultaneously, followed by an aggregation/merge step.

![Parallel Agent / Agent Swarm Architecture](resources/diagrams/agent_swarm.png)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Lower latency**: tasks execute concurrently rather than blocking | **Harder to manage dependencies** and state (risk of race conditions) |
| **Maintains predictability** of sequential agents via strict mapping | Potential **compute resource contention** if local models are used |
| Fast and highly efficient for bulk processing | **Harder to debug** simultaneous failures |

### When to Use
Use for bulk operations (RLM distillation, massive doc conversions) or partitioned tests where tasks are 100% independent and do not rely on each other's intermediate state.

---

## 5. Meta-Learning System (`triple-loop-learning`)

The **Meta-Learning Loop** architecture a

*(content truncated)*

## See Also

- [[agent-loops]]
- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]
- [[memory-promotion-decision-guide]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-loops/references/PATTERN_GUIDE.md`
- **Indexed:** 2026-04-17T06:42:09.220405+00:00
