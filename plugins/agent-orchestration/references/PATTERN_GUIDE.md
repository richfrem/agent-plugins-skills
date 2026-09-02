# Agent Loops: Pattern Guide

This guide maps the agent-orchestration/ skills to standard industry terminology (e.g., Google ADK patterns) and provides a comparative reference for when and how to use them.

## Overview of Patterns

| Our Skill | Industry Alias | Primary Use Case |
| :--- | :--- | :--- |
| `learning-loop` | Single Agent / Loop Agent | Self-contained research, content generation, and exploration where no inner delegation is required. |
| `dual-loop` | Sequential Agent / Agent as a Tool | Delegating a well-defined task to a worker agent, verifying its execution, and repeating if necessary. |
| `agent-swarm` | Parallel Agent | Work that can be partitioned into independent sub-tasks running concurrently across multiple agents. |
| `orchestrator` | Routing Agent / Hierarchical | Analyzing an ambiguous trigger and routing it to one of the specific specialized implementations above. |
| `red-team-review` | Review and Critique Pattern | Iterative generation paired with adversarial review, continuing until an "Approved" verdict is reached. |
| `triple-loop-learning` | Meta-Learning System | Continuous, unguided self-improvement of agent processes through rigorous objective headless testing, iterating on prompts and system skills from logged friction. |
| `graph-execution` | Deterministic State Machine / DAG | Complex workflows requiring discrete typed nodes, human approval gates, worktree sandboxing, and automated rollback. |
| `select-loop-strategy` | Strategy Router / Decision Tree | Analyzing any incoming task and navigating the decision tree to select the optimal orchestration topology. |

---

## 1. Single Agent / Loop Agent (`learning-loop`)

The foundational pattern where a single agent repeatedly interacts with the environment (tools, research) to synthesize knowledge.

![Learning Loop / Single Agent Architecture](resources/diagrams/learning_loop.mmd)

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

![Sequential Agent / Dual Loop Architecture](resources/diagrams/inner_outer_loop.mmd)

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

![Parallel Agent / Agent Swarm Architecture](resources/diagrams/agent_swarm.mmd)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Lower latency**: tasks execute concurrently rather than blocking | **Harder to manage dependencies** and state (risk of race conditions) |
| **Maintains predictability** of sequential agents via strict mapping | Potential **compute resource contention** if local models are used |
| Fast and highly efficient for bulk processing | **Harder to debug** simultaneous failures |

### When to Use
Use for bulk operations (RLM distillation, massive doc conversions) or partitioned tests where tasks are 100% independent and do not rely on each other's intermediate state.

---

## 4. Meta-Learning System (`triple-loop-learning`)

The **Meta-Learning Loop** architecture automates the iterative improvement of an agentic system over long horizons using rigorous headless testing. Unlike simpler loops, it acts as an autonomous optimization engine continuously hunting for friction, hypothesizing process and rule improvements, deploying them safely to headless testing environments, and securely promoting the winning logic into systemic changes.

**Best used when:** You have comprehensive headless test metrics running the core workflows and you want an agent to autonomously test improvements without supervision.

---

## 5. Routing Agent / Hierarchical (`orchestrator`)

An initial decision layer that analyzes the prompt or trigger and directs the query to the correct specialized sub-agent or pattern.

![Routing Agent / Orchestrator Architecture](resources/diagrams/agent_loops_overview.mmd)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Highly scalable** ecosystem entrypoint | Added **latency** for the initial classification inference step |
| Prevents overloading a single agent with too many tools | Router failures cause cascading failures downstream |
| Ideal for "universal" command inputs | Increases architectural complexity |

### When to Use
Use as the primary entry point for ambiguous human triggers. The Router decides if the task warrants a simple learning loop, a triple-loop delegation, or a full swarm.

---

## 6. Review and Critique Pattern (`red-team-review`)

A specialized iterative pattern pairing a generator with an adversarial reviewer.

![Review and Critique / Red Team Review Architecture](resources/diagrams/red_team_review_loop.mmd)

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **High quality output** enforced by adversarial scrutiny | **Significant latency** due to synchronous back-and-forth rounds |
| Catches design flaws and epistemic drift early | **Higher token cost**: redundant context loading across rounds |
| Reduces reliance on human-in-the-loop for intermediate QA | Can lead to infinite loops if acceptance criteria are too vague |

### When to Use
Use for architecture decisions (ADRs), security audits, and critical design phases where adversarial pushback is a hard requirement before execution.

---

## 7. Deterministic State Machine / DAG Pattern (`graph-execution`)

A finite state machine or directed acyclic graph where tasks traverse discrete typed nodes (`TRIAGE` $\rightarrow$ `PLAN` $\rightarrow$ `AWAITING_APPROVAL` $\rightarrow$ `AUTHORIZED` $\rightarrow$ `EXECUTE` $\rightarrow$ `VERIFY_GATE` $\rightarrow$ `COMMIT` / `ROLLBACK`).

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Highest safety & predictability**: strict state transitions | Requires explicit controller script and state files |
| **Asymmetric persistence**: safe rollback with retained learnings | More setup overhead than a lightweight loop |
| **Tamper-evident proof**: bound by cryptographic receipts | Inflexible for informal brainstorming or quick spikes |

### When to Use
Use for high-assurance autonomous coding, self-evolution cycles, infrastructure changes, or any multi-attempt repair where failures must revert code without losing diagnostic insights.

---

## 8. Strategy Router Pattern (`select-loop-strategy`)

A dedicated decision framework providing an interactive and deterministic tree to evaluate task characteristics and select the exact orchestration primitive.

### When to Use
Use at the very beginning of a non-trivial initiative when deciding whether to run solo (`learning-loop`), pair (`co-pilot-loop`), delegate (`dual-loop`), parallelize (`agent-swarm`), critique (`red-team-review`), evolve (`triple-loop-learning`), or structure as a DAG (`graph-execution`).
