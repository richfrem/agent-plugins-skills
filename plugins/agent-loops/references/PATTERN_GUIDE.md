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

The **Meta-Learning Loop** architecture automates the iterative improvement of an agentic system over long horizons using rigorous headless testing. Unlike simpler loops, it acts as an autonomous optimization engine continuously hunting for friction, hypothesizing process and rule improvements, deploying them safely to headless testing environments, and securely promoting the winning logic into systemic changes.

**Best used when:** You have comprehensive headless test metrics running the core workflows and you want an agent to autonomously test improvements without supervision.

---

## 4. Routing Agent / Hierarchical (`orchestrator`)

An initial decision layer that analyzes the prompt or trigger and directs the query to the correct specialized sub-agent or pattern.

![Routing Agent / Orchestrator Architecture](resources/diagrams/agent_loops_overview.png)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Highly scalable** ecosystem entrypoint | Added **latency** for the initial classification inference step |
| Prevents overloading a single agent with too many tools | Router failures cause cascading failures downstream |
| Ideal for "universal" command inputs | Increases architectural complexity |

### When to Use
Use as the primary entry point for ambiguous human triggers. The Router decides if the task warrants a simple learning loop, a triple-loop delegation, or a full swarm.

---

## 5. Review and Critique Pattern (`red-team-review`)

A specialized iterative pattern pairing a generator with an adversarial reviewer.

![Review and Critique / Red Team Review Architecture](resources/diagrams/red_team_review_loop.png)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **High quality output** enforced by adversarial scrutiny | **Significant latency** due to synchronous back-and-forth rounds |
| Catches design flaws and epistemic drift early | **Higher token cost**: redundant context loading across rounds |
| Reduces reliance on human-in-the-loop for intermediate QA | Can lead to infinite loops if acceptance criteria are too vague |

### When to Use
Use for architecture decisions (ADRs), security audits, and critical design phases where adversarial pushback is a hard requirement before execution.
