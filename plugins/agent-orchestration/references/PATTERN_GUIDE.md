# Agent Loops: Pattern Guide

This guide maps the `agent-orchestration/` skills to standard industry terminology (e.g., Google ADK patterns) and provides a comparative reference for when and how to use them.

## Contents
- [Overview of Patterns](#overview-of-patterns)
- [1. Single Agent / Loop Agent (`learning-loop`)](#1-single-agent--loop-agent-learning-loop)
- [2. Sequential Agent / Agent as a Tool (`dual-loop`)](#2-sequential-agent--agent-as-a-tool-dual-loop)
- [3. Parallel Agent (`agent-swarm`)](#3-parallel-agent-agent-swarm)
- [4. Meta-Learning System (`triple-loop-learning`)](#4-meta-learning-system-triple-loop-learning)
- [5. Dispatcher Pattern (`orchestrator`)](#5-dispatcher-pattern-orchestrator)
- [6. Review and Critique Pattern (`red-team-review`)](#6-review-and-critique-pattern-red-team-review)
- [7. Deterministic DAG Runner Pattern (`graph-execution`)](#7-deterministic-dag-runner-pattern-graph-execution)
- [8. Strategy Selector Pattern (`select-loop-strategy`)](#8-strategy-selector-pattern-select-loop-strategy)

---

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

## 5. Dispatcher Pattern (`orchestrator`)

Dispatches the selected pattern to worker runtimes after `select-loop-strategy` decides the execution topology. It does not perform autonomous classification or routing on its own.

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Clean separation**: Decouples pattern selection from pattern dispatch | Extra step between strategy decision and execution |
| Standardizes input packets and handoff structures | Requires structured task brief or decision record |

### When to Use
Use after `select-loop-strategy` produces a decision record, to prepare dispatch packets and trigger the selected pattern planner.

---

## 6. Review and Critique Pattern (`red-team-review`)

A specialized iterative pattern pairing a generator with an adversarial reviewer.

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **High quality output** enforced by adversarial scrutiny | **Significant latency** due to synchronous back-and-forth rounds |
| Catches design flaws and epistemic drift early | **Higher token cost**: redundant context loading across rounds |
| Reduces reliance on human-in-the-loop for intermediate QA | Can lead to infinite loops if acceptance criteria are too vague |

### When to Use
Use for architecture decisions (ADRs), security audits, and critical design phases where adversarial pushback is a hard requirement before execution.

---

## 7. Deterministic DAG Runner Pattern (`graph-execution`)

A deterministic directed acyclic graph runner where tasks traverse discrete typed nodes: `parallel_read`, `sync_barrier`, `sequential_mutation`, and `verifier_gate`. Features total sequential ordering on mutations, thread-safe main-thread rollback, and outside run receipts.

### Pros & Cons
| Pros | Cons |
| :--- | :--- |
| **Highest safety & predictability**: strict topological dependency execution | Requires pre-compiled `graph-manifest.json` |
| **Safe automated rollback**: restores exact baseline SHA on failure | More ceremony than a lightweight loop |
| **Audit receipts**: per-node commit records stored outside the worktree | Inflexible for informal brainstorming or quick spikes |

### When to Use
Use for workflows with parallel read fan-out, synchronization barriers, or ordered multi-step mutations where intermediate verifier gates and rollback safety are required.

---

## 8. Strategy Selector Pattern (`select-loop-strategy`)

Interactive front door that diagnoses task characteristics (unit structure, ordering/convergence, assurance need, and task nature), compiles a decision record (`select-loop-strategy-decision.json`), and hands off to the pattern planner.

### When to Use
Use at the beginning of any non-trivial engineering initiative to determine whether the task requires `dual-loop`, `agent-swarm`, `graph`, `red-team-review`, `learning-loop`, or `triple-loop-learning`. Swarm plan artifact is a job file (`<task-id>.job.md`) plus file list.
