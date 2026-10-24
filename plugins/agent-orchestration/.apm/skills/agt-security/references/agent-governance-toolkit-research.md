# Microsoft Agent Governance Toolkit (AGT) Research & Architecture

**Source Lineage**: Recovered from institutional research (`docs/MAF-research-analysis/`, ADR-007).
**Scope**: Microsoft Agent Governance Toolkit (AGT) architecture, packages, runtime integration, and deterministic governance principles.

## Contents

- [The Core Principle](#the-core-principle-deterministic-vs-prompt-governance)
- [Framework-Agnostic Architecture](#framework-agnostic-architecture)
- [The Seven AGT Packages](#the-seven-agt-packages)
- [Runtime Integration & Middleware Pipeline](#runtime-integration--middleware-pipeline)
- [Operational Sandboxing & HMAC Key Lifecycle](#operational-sandboxing--hmac-key-lifecycle)
- [References & Authoritative Sources](#references--authoritative-sources)

---

## The Core Principle: Deterministic vs Prompt Governance

> **"The fundamental problem with prompt-based governance is the recursive trust issue: You are using an LLM to decide whether an LLM should be allowed to do something."**

AGT replaces cognitive governance (an LLM reading English instructions in a system prompt) with **deterministic code-level governance** (code evaluating formal policies before and after model invocation).

### Production Validation

In Microsoft production deployments across 11 specialized autonomous agents:
- Over 473 unauthorized tool execution attempts were hard-blocked deterministically across an 11-day observation window.
- Every single incident was intercepted in **under 8 milliseconds**.
- 10/10 coverage of the OWASP Agentic Top 10 vulnerabilities backed by 13,000+ unit tests.

---

## Framework-Agnostic Architecture

While AGT was released by Microsoft alongside the Microsoft Agent Framework (MAF), AGT is a **standalone, framework-agnostic open-source project** (`https://github.com/microsoft/agent-governance-toolkit`). It provides dedicated adapters across multiple agent ecosystems:

| Runtime / Framework | AGT Integration Adapter |
| :--- | :--- |
| **Claude Code CLI** | `agent-governance-claude-code` |
| **Copilot CLI** | `agent-governance-copilot-cli` |
| **Antigravity CLI** | `agent-governance-antigravity-cli` |
| **LangChain** | `LangChainKernel.as_middleware()` |
| **CrewAI** | `CrewAIKernel.as_hooks()` |
| **OpenAI Agents SDK** | `OpenAIAgentsKernel.as_hooks()` |
| **Google ADK** | `GoogleADKKernel.as_plugin()` |
| **Pydantic AI** | `PydanticAIGovernanceCapability` |
| **Microsoft Agent Framework (MAF)** | `GovernancePolicyMiddleware` |

---

## The Seven AGT Packages

| Package | Component | Core Responsibility |
| :--- | :--- | :--- |
| **Agent OS** | `agent-os-kernel` | Core policy enforcement point (PEP) & decision point (PDP) evaluating YAML, OPA Rego, or Cedar policies deterministically. |
| **Agent Mesh** | `agentmesh-platform` | Zero-trust agent identity using DIDs + Ed25519 keys, Inter-Agent Trust Protocol (IATP), and dynamic behavioral trust scoring (0–1000). |
| **Agent Runtime** | `agent-hypervisor` | CPU-ring metaphor privilege rings, multi-step saga transaction rollback, and immediate out-of-band kill switches. |
| **Agent SRE** | `agent-sre` | Latency SLOs, error budgets, autonomous circuit breakers, and progressive rollout canary gates. |
| **Agent Compliance** | `agent-governance-toolkit` | Automated compliance grading against EU AI Act, HIPAA, SOC2, and OWASP Agentic Top 10. |
| **Agent Marketplace** | `agent-marketplace` | Agent and plugin lifecycle management, package signing, and provenance verification. |
| **Agent Lightning** | `agent-lightning` | Reinforcement learning (RL) training governance, safety boundary guards during self-evolution. |

---

## Runtime Integration & Middleware Pipeline

In a unified agent pipeline (such as MAF, Claude Code, or our custom Python control plane), model safety and tool governance operate at distinct layers:
1. **Model Safety Layer (MAF / LLM Vendor)**: Handles input/output content filtering, prompt injection detection, and jailbreak shields.
2. **Action Governance Layer (AGT)**: Governs **agent actions, filesystem access, subprocess execution, and tool invocations**.

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENT TASK CALL                        │
├─────────────────────────────────────────────────────────────┤
│  Model Input Filtering (Content Safety / Prompt Shields)     │
├─────────────────────────────────────────────────────────────┤
│  AGT Middleware Pipeline:                                   │
│  ├── AuditTrailMiddleware        (Append-only trace)        │
│  ├── GovernancePolicyMiddleware  (OPA / Cedar rule eval)    │
│  ├── CapabilityGuardMiddleware   (Tool whitelist / budgets) │
│  └── RogueDetectionMiddleware    (Behavioral anomaly guard) │
├─────────────────────────────────────────────────────────────┤
│  Subprocess Execution / Sandboxed Tool Invocation           │
└─────────────────────────────────────────────────────────────┘
```

---

## Operational Sandboxing & HMAC Key Lifecycle

The local operational implementation within `agt-security` provides deterministic enforcement primitives:

1. **Subprocess Environment Sanitization**:
   - Scrubbing high-risk injection variables (`PYTHONPATH`, `PYTHONHOME`, `LD_PRELOAD`, `DYLD_LIBRARY_PATH`) prior to dispatching child workers (`scripts/agt_ops.py verify-sandbox`).
2. **Filesystem Boundary Containment**:
   - Strictly confining tool operations to authorized workspace paths, deterministically raising `PermissionError` on path traversal attempts (`scripts/path_security.py`).
3. **Cryptographic HMAC Session Envelopes**:
   - Generating 32-byte cryptographically secure session keys with private `0600` permissions (`context/exploration/.secrets/session_hmac.key`) to sign local inter-agent bus events.

---

## References & Authoritative Sources

- ADR-007: MAF as Optional Certified Runtime Adapter (`docs/ADRs/007_maf_adapter_runtime_decision.md`)
- [Microsoft Agent Governance Toolkit GitHub](https://github.com/microsoft/agent-governance-toolkit)
- [Governance at the Speed of Agents (Microsoft DevBlogs)](https://devblogs.microsoft.com/agent-framework/governance-at-the-speed-of-agents-microsoft-agent-framework-and-agent-governance-toolkit-better-together/)
- [Acceptance Criteria](acceptance-criteria.md)
