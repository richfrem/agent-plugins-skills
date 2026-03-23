# Research Summary: Agent Operating Systems (Agent-OS)
## A Blueprint Architecture for Real-Time, Secure, and Scalable AI Agents

**Author**: Anis Koubaa, Alfaisal University, Riyadh, Saudi Arabia
**Published**: TechRxiv (preprint), September 8, 2025
**DOI**: https://doi.org/10.36227/techrxiv.175736224.43024590/v1
**License**: CC-BY-NC-SA 4.0
**Status**: Preliminary report, not peer-reviewed

---

## Core Thesis

Today's agent stacks resemble "bare-metal" computing before operating systems existed - ad-hoc pipelines with no unified abstractions for lifecycle management, memory, scheduling, security, or real-time guarantees. This paper proposes the Agent Operating System (Agent-OS) as the next foundational layer: not a system fully realizable today, but an "architectural North Star" to guide the next decade of agent infrastructure research.

The paper argues: just as traditional OSes virtualized hardware to create stable contracts between applications and resources, Agent-OS must virtualize the agent substrate to create stable contracts between agent applications and their execution environment.

---

## The "Billion Agent Problem"

By 2030, billions of AI agents will require coordination. Without OS-level abstraction, this creates computational chaos at unprecedented scale. The paper frames this as the same inflection point computing faced before operating systems: before OSes, every programmer wrote their own memory manager, scheduler, and I/O routines. Agent development today is at the same fragmented stage.

---

## Five-Layer Architecture

```
Layer 5: User & Application Layer
  - Agent definitions, user-facing APIs, chat-as-shell interface
  - Agent Contract (portable, machine-readable specification)

Layer 4: Orchestration & Workflow Layer
  - DAG/state machine workflow engine
  - Planners, routers, agent-to-agent (A2A) delegation
  - HITL (Human-in-the-Loop) gates with approval prompts
  - Retry, idempotency, compensation logic

Layer 3: Agent Runtime Layer
  - Agent lifecycle manager (spawn/pause/resume/kill)
  - Context window management and summarization
  - RAG pipelines with citation and provenance
  - Tool execution with schema validation

Layer 2: Resource & Service Layer
  - Memory backends (vector stores, KV caches, relational DBs)
  - Tool registry with capability-scoped permissions
  - Model gateway with cost/placement/privacy routing
  - Secret management and redaction

Layer 1: Kernel Layer (trusted core)
  - Scheduler: token-rate-aware, goal-progress-oriented
  - Context manager: token budgets, episodic logs
  - Action manager: capability enforcement, audit logging
  - Zero-trust microkernel: no agent executes without contracts

Cross-cutting concerns (span all layers):
  - Security and governance
  - Observability (OTel traces, lineage)
```

---

## Agent Contracts (Key Innovation)

An Agent Contract is a portable, machine-readable specification that travels with an agent across runtimes. Fields include:

- `prompt_template`: The agent's system prompt or policy template
- `tool_scopes`: Which tools the agent may invoke and under what constraints
- `latency_class`: HRT, SRT, or DT (see below)
- `model_policy`: Routing rules (local vs. cloud, cost, privacy class)
- `budget`: Token/cost limits per turn or session
- `memory_policy`: Retention, redaction, namespacing rules
- `hitl_gates`: Which actions require human approval

The contract enables **portability** (run the same agent on any compliant runtime) and **enforcement** (the runtime verifies the contract at execution time).

---

## Latency Classes (Time Semantics)

One of the paper's most original contributions: formalizing three latency classes as first-class OS primitives with enforceable SLOs.

### Hard Real-Time (HRT) - Deterministic and safety-critical
- **Definition**: Correctness depends on meeting every deadline; any miss = system failure
- **Use cases**: Robot navigation, medical devices, factory control loops, LLM-guided safety filters
- **Targets**: 1-20 ms execution slices; jitter <= 5 ms; zero deadline misses
- **OS policies**: EDF/RM scheduling, CPU/GPU reservations, pinned threads, fixed memory arenas (no GC), lock-free queues
- **LLM anchors**: Bounded context templates, capped output tokens, pre-validated tool paths, lightweight local models

### Soft Real-Time (SRT) - Interactive and perceptual
- **Definition**: Occasional misses tolerable, but user-perceived responsiveness is crucial
- **Use cases**: Conversational assistants, meeting summarizers, live captioning, screen copilots
- **Targets**: First-token onset 150-300 ms; full-turn 0.8-1.2 s; jitter P95 <= 20%
- **OS policies**: Priority-queue scheduling, streaming partial completions, barge-in support, adaptive buffering, rolling context caches
- **LLM anchors**: TTFT, tokens/sec, function-call round-trip, RAG latency budget (<= 150 ms retrieval)

### Delay-Tolerant (DT) - Throughput and cost first
- **Definition**: No hard deadline, maximize throughput per unit cost
- **Use cases**: Overnight batch analytics, report generation, data migration, city-scale planning
- **Targets**: 60-120 s full-turn acceptable; cost-per-token optimized
- **OS policies**: Low-priority preemptible tasks, opportunistic batching, resumable checkpoints
- **LLM anchors**: Cost-per-token budget, batch efficiency, checkpoint/resume semantics

---

## Functional Requirements (FR)

| ID | Requirement | Key "Good Enough" Criteria |
|----|------------|---------------------------|
| FR1 | Agent lifecycle & scheduling | >=99% recovery within 60s; no duplicate side effects; deterministic turn replay |
| FR2 | Context, memory, and knowledge | Context never exceeds max_context_tokens; RAG recall@K meets targets; retention policies enforced |
| FR3 | Tools & environments | >=99% schema-conformant calls; out-of-scope tools blocked and logged; tool sequences replayable |
| FR4 | Orchestration & multi-agent coordination | Exactly-once semantics across retries; HITL within SLOs; delegation preserves scopes |
| FR5 | Observability | >99% steps have trace spans; full run reconstruction with provenance |
| FR6 | Safety, security, governance | Unauthorized actions blocked and logged; audit integrity provable; injection deflection >=95% |
| FR7 | Model, cost, placement | Routing complies with policy; budgets enforced; no privacy-class violations |
| FR8 | Interfaces & HITL | Interactive turns meet SLOs; reviewers can intervene with full context and diffs |
| FR9 | Multitenancy & portability | Isolation tests always pass; same Agent Contract runs identically across reference runtimes |

---

## Non-Functional Requirements (NFR)

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Reliability | 99.9% control plane availability; RTO <= 60s with idempotent replay |
| NFR2 | Performance | Orchestration overhead P95 <= 200 ms; first-token < 1s for interactive |
| NFR3 | Security by design | SSO/OIDC, encrypted at rest/transit, DLP/redaction for PII, injection deflection >= 95% |
| NFR4 | Scalability | Horizontal scale-out; autoscaling on queue depth + tokens/sec; graceful back-pressure |
| NFR5 | Interoperability | Versioned adapters; MCP-style tool contracts; portable Agent Contracts across runtimes |
| NFR6 | Operations | Health probes, circuit breakers, canary releases, CE pipelines, SLO dashboards |
| NFR7 | Real-time | Class-specific SLOs enforced; pre-deployment schedulability checks reject non-compliant deploys |
| NFR8 | Compliance | Retention/redaction controls, data-residency modes, end-to-end lineage, policy attestation |

---

## Zero-Trust Microkernel

The kernel layer is explicitly zero-trust: no agent executes without contracts, capabilities, and audit trails. Key primitives:

- **RBAC**: Role-based access control with capability scoping per tool/data
- **Capability-scoped tools**: Every tool invocation must stay within its declared scope; violations blocked and logged
- **Encrypted memory**: Tenant isolation at the memory layer
- **Immutable audit trails**: Tamper-evident logs with hash chains
- **Consent gates**: High-risk actions require explicit HITL approval

Security is not an application-level add-on; it is a kernel responsibility.

---

## Comparison to Existing Systems

| Aspect | LLM as OS (conceptual) | AIOS (academic) | Agent-OS (this paper) |
|--------|----------------------|----------------|----------------------|
| Scope | Visionary analogies | LLM agents only | Full agentic ecosystem including multimodal, HITL |
| Architecture | No layered stack | 3 layers | 5 layers + cross-cutting security/governance |
| Requirements | None | Empirical gains, no formal FR/NFR | Prioritized FR/NFR baseline |
| Real-time | Not addressed | Latency reduction, no taxonomy | Formal HRT/SRT/DT with enforceable SLOs |
| Security | Mentioned conceptually | Access manager | Zero-trust microkernel as kernel primitive |
| Standards | Calls for them | Runtime-internal | MCP for tools, A2A for inter-agent, OTel for observability |

---

## Open Challenges Identified

1. **Complexity and Performance Overhead**: Multi-layered design adds latency, especially problematic for HRT workloads
2. **Ecosystem Fragmentation**: MCP and A2A are gaining traction but competing with proprietary vendor APIs
3. **Scalable Governance at Billions of Agents**: Rigorous audit and consent across millions of agents is computationally expensive
4. **Stochastic LLMs in Real-Time Systems**: Reconciling nondeterministic model outputs with deterministic scheduling guarantees is an unsolved problem

## Research Agenda

1. Modular microkernel design - minimal trusted core, everything else in user-space
2. Formal verification of safety layers (mathematical proof of contract adherence)
3. Standardized HRT/SRT/DT benchmarks that measure deadline misses, jitter, and cost
4. Open ecosystem foundations to prevent vendor fragmentation

---

## Relevance to Agentic OS Plugin

### Validates the OS Metaphor
The paper's five-layer architecture strongly validates the Agentic OS plugin's existing OS metaphor (kernel/RAM/disk/daemons/event bus). The plugin implements several of these layers at project scale.

### Agent Contracts = plugin.json + Scope Declarations
The paper's Agent Contract concept maps directly to combining `plugin.json` with the Explicit Scope Declaration Model proposed in `vision.md`. Formalizing these as portable, machine-readable contracts is the right direction.

### Latency Classes Suggest Plugin Tiering
The HRT/SRT/DT taxonomy suggests the Agentic OS plugin should eventually classify skills and agents by latency class. Interactive user-facing agents are SRT; background daemons (os-learning-loop, os-health-check) are DT. Future robotics/automation integrations may require HRT guarantees.

### Confirms Microkernel Approach
The paper's argument for a zero-trust microkernel with minimal trusted core validates keeping `kernel.py` small and pushing skill logic to disk-resident SKILL.md bodies. The kernel should do less, not more.

### Confirms Adapter Pattern Necessity
FR2's "pluggable backends" for memory (vector stores, KV caches, relational DBs) directly validates the adapter pattern proposed in `vision.md` - the current file-system-based memory should be one swappable backend, not the only option.

---

## Key Quotes

> "Today's agent architectures resemble the pre-OS era of computing - a chaos of duplicated solutions lacking fundamental abstractions for resource management, isolation, and coordination."

> "Security by Architecture: A zero-trust microkernel ensures no agent executes without contracts, capabilities, and audit trails - making trust enforceable, not optional."

> "The most critical insight is that for agentic AI to be trustworthy, core system properties - especially real-time responsiveness and zero-trust security - must be architected into a minimal kernel, not bolted on as application-level afterthoughts."

> "The path from today's promising agent prototypes to tomorrow's dependable, society-scale AI systems is paved with this systems-level rigor."
