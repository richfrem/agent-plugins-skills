# Research Summary: Agent Operating Systems (AOS)
## Integrating Agentic Control Planes into, and Beyond, Traditional Operating Systems

**Author**: Ankur Sharma, Independent Researcher, San Francisco, USA
**Published**: Authorea (preprint), February 11, 2026
**DOI**: https://doi.org/10.22541/au.177083718.83864768/v1
**License**: CC-BY 4.0
**Status**: Preprint, not peer-reviewed

---

## Core Thesis

Traditional operating systems were designed for deterministic programs with explicit control flow. Agentic AI introduces a fundamentally different execution model: long-lived, goal-directed entities that reason probabilistically, invoke tools dynamically, and adapt behavior based on feedback. Existing OSes are not wrong; they are incomplete for this workload class.

Sharma argues for an AOS as a **control plane** that extends (not replaces) the traditional OS - adding semantic governance above the process level while preserving the OS as the sole mediator of hardware resources. The most important property: **agent internal reasoning may be probabilistic, but AOS enforcement must be deterministic**.

The paper is more systems-engineering-grounded than Koubaa's - it maps AOS concepts onto actual Linux and Windows primitives and provides concrete implementation paths.

---

## Why Classical OS Abstractions Are Incomplete

### Process abstraction assumes bounded execution
- Agents are long-lived stateful loops that may run for days/weeks, evolving state not captured by heap memory
- Agents activate opportunistically (idle waiting for triggers, then burst into activity)
- Agent identity persists across process restarts and migrations - the process is just a container

### Scheduling assumes instruction progress, not goal progress
- OS schedulers allocate CPU time slices; agent progress depends on tool latencies, human input, risk budgets
- A "blocked" agent waiting for tool approval is idle to the OS scheduler but actively progressing toward its goal
- Cost budgets and rate limits require scheduling decisions beyond CPU allocation

### Memory is not merely addressable storage
- Agent state includes: short-term context windows, long-term episodic state, retrieved knowledge, and provenance metadata
- These have different lifetimes, trust levels, and replay requirements
- Classical memory management has no concept of "why was this data present when this decision was made"

### I/O assumes explicit, deterministic invocation
- System calls: allowed or denied based on privilege
- Agent tool calls: permission depends on dynamic context, impact radius, policy, and attribution chain
- Every tool call needs lineage, not just allow/deny

### Identity assumes stable principals and stable intent
- OS: user identity with known privileges
- Agent: autonomous behavior that may change over time, requiring scoped escalation, revocation, and delegated authority
- Static permission model is insufficient; needs capability-based access with explicit scopes, time limits, and revocation

### Observability focuses on resources, not decision lineage
- Traditional: CPU, memory, disk, network
- Agents need: what did the agent observe -> what action did it propose -> what did policy decide -> what tool executed -> what outcome occurred
- Without lineage, incident response and compliance audits are impossible

---

## Precise Definition

> An Agent Operating System (AOS) is a systems software layer that manages the lifecycle, execution, coordination, and governance of goal-directed agents by extending or reinterpreting classical operating system responsibilities, while preserving deterministic behavior at the system boundary.

Two properties separated:
- Agent internal reasoning: MAY be probabilistic
- AOS enforcement and external effects: MUST be deterministic and auditable

---

## First-Class Entities in an AOS

Classical OS: processes, threads, file descriptors, address spaces

AOS adds:
1. **Agent identity** - a principal with scoped authority and a defined lifecycle
2. **Goal and task graphs** - intended outcomes and dependencies
3. **Capability sets** - which tools/actions are allowed, including scopes and bounds
4. **Context state** - the structured memory view presented to the reasoning plane
5. **Execution records** - append-only audit trails for decisions and actions

AOS does not replace processes or threads. It interprets them as execution containers beneath the agent abstraction.

---

## Separation of Planes (Core Safety Property)

This is Sharma's most important architectural contribution:

```
+-----------------------------------------+
|         REASONING PLANE (untrusted)     |
|  Probabilistic inference, planning,     |
|  strategy selection. Outputs treated    |
|  as PROPOSALS, not commands.            |
+-----------------------------------------+
           |  proposed actions
           v
+-----------------------------------------+
|          POLICY PLANE                   |
|  Authorization, risk checks, compliance |
|  constraints, budget controls.          |
|  DENY BY DEFAULT where ambiguous.       |
|  Produces auditable decisions with      |
|  reason codes.                          |
+-----------------------------------------+
           |  authorized actions
           v
+-----------------------------------------+
|         EXECUTION PLANE (trusted)       |
|  Deterministic tool invocation,         |
|  system calls, side effects.            |
|  Enforces policy decisions              |
|  deterministically.                     |
|  Runs in least-privilege environments.  |
+-----------------------------------------+
```

This separation allows the system to treat reasoning outputs as proposals rather than commands. The reasoning plane is fundamentally untrusted with respect to policy.

---

## Four Memory Classes

| Class | Description | Lifetime | Trust |
|-------|------------|---------|-------|
| Ephemeral context | Bounded working set constructed for a reasoning slice | Duration of one turn | Working |
| Durable agent memory | Persistent state across long-lived tasks | Versioned, long-term | High (internal) |
| Retrieved knowledge | Content from documents, tools, external stores | Per-retrieval | Low (external - must carry provenance) |
| Execution records | Append-only event streams of actions, policy decisions, outcomes | Permanent (audit) | Authoritative |

Key constraint on retrieved knowledge: must carry provenance, integrity metadata, and classification labels. Any summarization of retrieved content must record source inputs and summarizer version. This enables reconstruction of "what could the agent have known at this moment" for incident response.

---

## Tool and Capability Registry

Tools are analogous to system calls but with explicit mediation. Each tool definition should specify:
- Name and version
- Input schema and validation rules
- Side effect classification
- Required capabilities and scopes
- Rate limits and quotas
- Deterministic prechecks and postconditions
- Audit requirements

Tool invocation pipeline (all steps deterministic):
1. Schema validation and normalization
2. Policy checks (including context-dependent constraints)
3. Risk checks (sensitive data egress limits)
4. Budget checks (cost, rate limits)
5. Execution in least-privilege sandbox
6. Post-checks on outputs
7. Append-only audit logging with reason codes

---

## Layered Policy Model

Static authorization -> Capability constraints -> Context policy -> Risk policy -> Governance policy

Trust states: normal, restricted, quarantined, reviewed (triggered by deterministic signals: repeated denials, suspicious tool patterns, integrity failures, unexpected data classification mismatches). These are crisp operational postures, not opaque trust scores.

---

## Four Architectural Invariants

These are Sharma's most actionable contribution - non-negotiable properties of any AOS implementation:

**Invariant 1**: No side-effecting action is executed without a deterministic policy decision of "allow."

**Invariant 2**: All policy outcomes (allow, deny, defer) are recorded in an append-only audit record prior to rescheduling.

**Invariant 3**: Scheduling decisions depend only on observable state and budgets, not on internal reasoning tokens.

**Invariant 4**: Underlying OS remains the sole mediator of hardware resources.

These four invariants are the minimum viable security contract for any AOS. The Agentic OS plugin's `PreToolUse` hooks partially enforce Invariant 1, but Invariants 2 and 3 are not yet formally implemented.

---

## Integration Models

Sharma evaluates four integration strategies, ordered by increasing enforcement strength:

### Model 1: AOS as User-Space Runtime (pragmatic today)
- AOS runs as user-space services/libraries; underlying OS unchanged
- Policy engine as a service; tool mediation as a sidecar or gateway
- Advantages: low-risk adoption, rapid iteration, portability
- Limitations: limited visibility into kernel scheduling; bypass risk if agents can access tools outside mediation
- **Practical mitigation**: combine with OS/network controls forcing all side effects through mediated channels

### Model 2: AOS as OS Extension
- OS-level primitives or hooks: agent identity as OS-recognized principal, capability tokens at syscall layer
- Better enforcement, harder to bypass
- Risks: increased kernel complexity, expanded attack surface, slower evolution
- Pragmatic path: use Linux Security Modules, eBPF, Windows policy frameworks for selective enforcement

### Model 3: AOS as Distributed Control Plane
- AOS as a cluster control plane; agent identity/goals/policy/audit centralized; execution delegated to node-level executors
- Appropriate for multi-service agent workloads and organization-level governance
- Differs from Kubernetes: schedules goal progress (not pods), defines deterministic policy boundaries, standardizes decision lineage

### Model 4: AOS Subsuming Parts of the OS (long horizon)
- AOS gradually takes over higher-layer scheduling, policy-driven access control, structured audit interfaces
- Core kernel responsibilities remain OS-native (memory paging, low-level CPU scheduling, hardware abstraction)
- Credible long-term path: AOS as a deterministic control plane governing side effects while kernel provides foundational isolation

---

## Linux and Windows Mapping

### Linux primitives for AOS
| AOS Concern | Linux Primitive |
|-------------|----------------|
| Agent isolation | namespaces (pid, mount, net, ipc, uts, user) |
| Resource bounds | cgroups v1/v2 (CPU, memory, I/O, pids) |
| Tool sandbox syscall restriction | seccomp filters |
| Mandatory access control | SELinux, AppArmor |
| Runtime observability | eBPF programs for network and syscall tracing |
| Tool egress control | network namespaces + firewall rules |
| Audit correlation | propagate stable agent action identifiers through execution |

### Windows primitives for AOS
| AOS Concern | Windows Primitive |
|-------------|-----------------|
| Agent identity | Security identifiers (SIDs), restricted tokens |
| Least-privilege tool execution | Token restriction, UAC integrity levels |
| Object-level enforcement | Access Control Lists (DACL/SACL) |
| Resource bounds | Job objects |
| Audit trail | Event Tracing for Windows (ETW) + centralized logging |
| Enterprise policy | Managed service identities, Group Policy |

Shared gap on both platforms: neither OS natively models agent intent, goal progress, or decision lineage. AOS must provide this semantic layer and propagate stable identifiers so kernel events can be attributed to agent actions.

---

## What Existing Technologies Cannot Provide

| Technology | What it provides | What it doesn't provide for AOS |
|-----------|-----------------|--------------------------------|
| Containers | Process isolation, reproducible packaging | Agent identity, decision lineage, deterministic tool mediation, goal progress scheduling |
| Hypervisors | Strong hardware isolation, VM boundaries | Fine-grained capability mediation, cross-VM policy by agent identity, unified decision lineage |
| Kubernetes | Declarative workloads, self-healing services | Goal progress scheduling, per-action parameter constraints, decision lineage, agent-specific governance |
| Policy engines (OPA) | Declarative authorization, consistent decisions | End-to-end action mediation, resource accounting across reasoning/execution phases, built-in decision lineage |
| Agent frameworks | Planning loops, tool calling, memory abstractions | Deterministic enforcement boundaries, capability-based revocation, auditability, resource scheduling at scale |

---

## Evaluation Criteria

Key criteria (systems properties, not model accuracy):
1. **Deterministic enforcement correctness**: same inputs -> same authorization outcomes; decisions explainable via logged reason codes
2. **Audit completeness**: every side-effecting action recorded with lineage; logs tamper-evident and queryable
3. **Containment and least privilege**: tools cannot be invoked outside mediation; capability scopes minimal
4. **Operational comprehensibility**: operators can understand agent state, blocked reasons, and actions without interpreting model internals
5. **Bounded performance overhead**: mediation overhead measurable and acceptable
6. **Safe failure modes**: degrade by denying side effects when policy or audit infrastructure unavailable

---

## Open Research Problems

1. Agent scheduling theory for goal progress and fairness (not CPU fairness)
2. Memory semantics for deterministic context construction with provenance
3. Formal verification boundaries for enforcement pipelines
4. Deterministic trust and risk state transitions that avoid opaque scoring
5. Cross-system identity and delegation standards ensuring revocation and attribution across tool chains

---

## Relevance to Agentic OS Plugin

### Four Invariants as Implementation Target
The four architectural invariants provide a concrete checklist for the Agentic OS plugin. Currently:
- Invariant 1 (no action without allow): Partially implemented via `PreToolUse` hooks
- Invariant 2 (all outcomes logged before rescheduling): `events.jsonl` partially does this; needs policy decision reason codes
- Invariant 3 (scheduling on observable state, not internal reasoning): Not formally implemented
- Invariant 4 (OS mediates hardware): Assumed, never formally enforced

### Separation of Planes Validates Hook Architecture
The reasoning/policy/execution plane separation directly validates the existing hook architecture: `PreToolUse` hooks ARE the policy plane intercepting proposals from the reasoning plane before they reach the execution plane. The plugin should make this framing explicit in its documentation.

### Memory Classes Map to Plugin Components
| Sharma's class | Plugin component |
|---------------|-----------------|
| Ephemeral context | Active context window (cleared each session) |
| Durable agent memory | `context/memory.md` (L3 long-term) + `context/memory/YYYY-MM-DD.md` (L2) |
| Retrieved knowledge | Skills loaded on-trigger via progressive disclosure |
| Execution records | `context/events.jsonl` (event bus) |

The plugin's three-tier lazy-loading architecture already implements Sharma's memory classes, though not with the formal trust labels and provenance metadata he recommends.

### Integration Model Recommendation
The plugin currently implements Model 1 (user-space runtime). Sharma's analysis confirms this is the right starting point. Model 2 (OS extensions via eBPF, LSM) becomes relevant as the plugin matures for enterprise deployments. Model 3 (distributed control plane) aligns with the vision doc's enterprise orchestrator concept.

### Confirms "Reasoning as Untrusted" Framing
The paper's most important security insight for the plugin: the LLM reasoning output must be treated as untrusted input to the policy plane. The plugin's current framing - hooks as security sentinels - is correct but should be strengthened to explicitly treat all LLM outputs as proposals subject to deterministic policy evaluation.

---

## Key Quotes

> "AOS does not replace kernels; it introduces intent and governance as first-class scheduling and enforcement concepts above them. In this sense, AOS represents a semantic elevation of control rather than a reimplementation of operating systems."

> "The research challenge is not in making agents autonomous, but in making autonomy deterministic at the boundary."

> "AOS can tolerate nondeterminism inside reasoning. It cannot tolerate nondeterminism in enforcement."

> "LLMs and learning components are probabilistic, may be incorrect, and may be adversarially influenced. The system boundary must be deterministic in enforcement, audit, and safety decisions."
