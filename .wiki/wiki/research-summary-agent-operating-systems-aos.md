---
concept: research-summary-agent-operating-systems-aos
source: plugin-code
source_file: agent-agentic-os/references/meta/research/sharma-2026-aos-control-plane.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.144223+00:00
cluster: policy
content_hash: 45f59692ccac1408
---

# Research Summary: Agent Operating Systems (AOS)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
1. **Agent identity** - a principal with scoped authority and a defined li

*(content truncated)*

## See Also

- [[research-summary-agent-operating-systems-agent-os]]
- [[agent-harness-summary]]
- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]
- [[template-post-run-agent-self-assessment]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/references/meta/research/sharma-2026-aos-control-plane.md`
- **Indexed:** 2026-04-17T06:42:09.144223+00:00
