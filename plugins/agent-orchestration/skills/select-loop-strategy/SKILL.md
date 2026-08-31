---
name: select-loop-strategy
plugin: agent-orchestration
description: "Selects the optimal agent orchestration or looping strategy for a given task using a deterministic decision tree. Distinguishes between solo discovery, dual-loop delegation, adversarial review, parallel swarms, meta-learning, and deterministic graph-state machines."
allowed-tools: Read, Bash
---

# Select Loop Strategy: Orchestration Pattern Decision Tree

Provides a deterministic decision framework to help agents and developers select the right execution topology for any given software engineering, research, or system evolution task.

---

## The Master Decision Tree

Evaluate your task against the following gates in order:

```
[Incoming Task / Trigger]
    │
    ▼
1. Does the task require strict human approval gates, formal state tracking, 
   transactional worktree isolation, or automatic rollbacks on test failure?
   ├─ YES ──▶ Pattern 7: graph-execution (Deterministic State Machine)
   └─ NO  ──▶ continue
    │
    ▼
2. Can the work be partitioned into 10+ independent, non-overlapping items 
   that execute simultaneously with zero shared state?
   ├─ YES ──▶ Pattern 4: agent-swarm (Parallel Fan-Out)
   └─ NO  ──▶ continue
    │
    ▼
3. Is the primary requirement adversarial critique, security analysis, 
   or multi-perspective red-teaming until an explicit "Approved" verdict?
   ├─ YES ──▶ Pattern 2: red-team-review (Generator / Critic Feedback)
   └─ NO  ──▶ continue
    │
    ▼
4. Does the task involve unguided friction discovery, automated hypothesis 
   testing, and headless benchmark evaluation over long horizons?
   ├─ YES ──▶ Pattern 5: triple-loop-learning (Meta-Learning System)
   └─ NO  ──▶ continue
    │
    ▼
5. Does the task require separating strategy/git management (Outer Loop) 
   from tactical coding/test execution (Inner Loop)?
   ├─ YES ──▶ Pattern 3: dual-loop (Hierarchical Delegation)
   │          (Optionally use co-pilot-loop for Claude + Gemini Flash Low pairing)
   └─ NO  ──▶ continue
    │
    ▼
6. Is this self-directed research, documentation, or local exploratory discovery 
   where the agent works autonomously in a single context window?
   └─ YES ──▶ Pattern 1: learning-loop (Single-Agent Cognitive Continuity)
```

---

## Pattern Comparison Matrix

| Pattern | Skill | Core Mechanics | Primary Use Case | Risk / Tradeoff |
|---|---|---|---|---|
| **1. Solo Learning** | `learning-loop` | Single context, orientation $\rightarrow$ synthesis $\rightarrow$ closure | Research, documentation, local spikes | Risk of context drift on large tasks |
| **2. Adversarial Review** | `red-team-review` | Generator + multi-persona critics, convergence limit | Security audits, architectural decisions | High token cost; multi-round latency |
| **3. Dual-Loop** | `dual-loop` | Outer Director (Git) $\leftrightarrow$ Inner Worker (No Git) | Features, bugs, bounded code changes | Inner agent must wait for manager review |
| **4. Parallel Swarm** | `agent-swarm` | Partitioned jobs, concurrent batch worker runners | Bulk migrations, mass doc generation | Merge conflicts if tasks share dependencies |
| **5. Meta-Learning** | `triple-loop-learning` | Friction logging $\rightarrow$ hypothesis $\rightarrow$ headless eval | Autonomous system self-optimization | Requires objective automated test harness |
| **6. Fast-Tier Pair** | `co-pilot-loop` | Claude (Director) + Gemini Flash Low (Worker) | Cost-sensitive rapid prototyping | Requires multi-CLI tooling configuration |
| **7. Graph Execution** | `graph-execution` | Deterministic DAG state transitions, receipts, rollbacks | High-assurance self-evolution, safe migrations | Highest structural rigor; state files required |

---

## When to Use Loops vs. Graphs vs. Swarms

### Use a **Loop** (`learning-loop`, `dual-loop`, `red-team-review`) when:
- The task is iterative and converges on quality through refinement.
- State is naturally maintained in conversational context or a task packet.
- Failure simply means "try another edit or refine the prompt."

### Use a **Graph** (`graph-execution`) when:
- The task involves irreversible or high-risk filesystem mutations.
- Human authorization is non-negotiable before execution or commit.
- You require **asymmetric persistence** (discarding bad code while saving learnings).
- Cryptographic proof receipts (`EVO-INTEGRITY-...`) are needed to verify execution integrity.

### Use a **Swarm** (`agent-swarm`) when:
- High volume of homogeneous items (e.g., 50 files to convert or test).
- Zero shared dependencies or ordering requirements between tasks.

---

See [`references/PATTERN_GUIDE.md`](../references/PATTERN_GUIDE.md) for full pattern comparisons and trade-off matrices.
