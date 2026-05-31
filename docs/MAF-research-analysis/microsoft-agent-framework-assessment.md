# Microsoft Agent Framework: Independent Architectural Assessment & Strategic Analysis

**Date:** 2026-05-30
**Author:** Architecture Red Team Audit (Opus 4.6 + Richard Fremmerlid)
**Contributors:** GPT-5.5 (critique calibration and industry analysis)
**Scope:** MAF v1.0 GA (April 2026) evaluated against Claude Agent SDK, OpenAI Agents SDK, Google ADK 2.0, GitHub Copilot SDK, and Agent Governance Toolkit (AGT)
**Context:** Senior enterprise architect operating a modular, repository-native agent ecosystem ("Plugin Triad") across multiple CLI runtimes (Claude Code, Copilot CLI, Antigravity CLI, Gemini CLI)

---

## Executive Summary

Microsoft's Agent Framework (MAF) v1.0 is marketed as a unified, model-agnostic orchestration layer for building multi-agent AI systems. After exhaustive analysis of its architecture, provider matrix, and integration patterns — cross-referenced against the four frontier provider SDKs and our own production plugin ecosystem — we conclude:

1. **MAF's "model-agnostic abstraction layer" is lossy, not lossless.** It wraps each provider's chat completion API, not their full agent SDK. Provider-specific capabilities (built-in tools, background execution, context compaction, structured output) are stripped to achieve API uniformity.

2. **Every core MAF capability except multi-model orchestration and .NET support is duplicated by frontier provider SDKs.** Sessions, tool calling, MCP, guardrails, human-in-the-loop, tracing, handoffs — all now ship natively in Claude Agent SDK, OpenAI Agents SDK, and Google ADK 2.0.

3. **The Agent Governance Toolkit (AGT) — Microsoft's strongest offering — is framework-agnostic and does not require MAF.** It has dedicated adapters for Claude Code, Copilot CLI, Antigravity CLI, LangChain, CrewAI, OpenAI Agents, and Google ADK.

4. **A well-designed local plugin architecture with standalone enforcement scripts provides equivalent or superior capabilities to MAF for solo/small-team development, without provider capability degradation or framework lock-in.**

5. **The broader industry critique is not that MAF is bad engineering — it's that MAF may be solving the 2024 orchestration problem while frontier labs increasingly think the 2026 problem is context management, agent operations, reliability, and autonomy.**

**Recommendation:** Do not adopt MAF. Adopt AGT and OpenTelemetry independently (both are framework-agnostic). Continue using frontier model CLIs at full native power with portable `.md` agent definitions and standalone Python enforcement scripts.

> **Hands-on learning reference:** The [MAF Learning Repo](https://github.com/deployed-in-azure/MicrosoftAgentFramework) contains working .NET examples covering all core MAF concepts (hello world through workflows). Key finding from hands-on testing: Foundry/Azure is NOT required for the basics — plain OpenAI or Gemini API keys work with zero Azure setup. Gemini works via the OpenAI-compatible endpoint using the standard `Microsoft.Agents.AI.OpenAI` package (no additional adapter needed).

---

## Part 1: The Frontier SDK Landscape (May 2026)

### 1.1 The Four Frontier Agent SDKs

| Framework | Owner | GA Status | Languages | Core Metaphor |
|---|---|---|---|---|
| **Claude Agent SDK** | Anthropic | GA (2026) | Python, TypeScript | "Give one agent a computer" — the agent IS the runtime |
| **OpenAI Agents SDK** | OpenAI | v0.17.4 | Python, TypeScript | "Coordinate a team" — minimal primitives, developer composes |
| **Google ADK** | Google | 2.0 GA | Python, TS, Go, Java, Kotlin | "Graph-based workflows" — deterministic execution flows |
| **GitHub Copilot SDK** | GitHub | GA | Python, TS, Go, .NET, Java, Rust | "Copilot CLI as a library" — same runtime, programmable |

### 1.2 Critical Finding: Claude Code IS the Claude Agent SDK

Claude Code is not a separate product — it is the Claude Agent SDK with a terminal UI. Anthropic's own documentation states:

> "The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript."

This means any architecture running inside Claude Code is **already running on the Claude Agent SDK**. There is no additional SDK to "adopt" — only programmatic access to capabilities the CLI already provides.

### 1.3 The Copilot SDK: Multi-Model But Single-Agent

The GitHub Copilot SDK is a capable single-agent runtime with multi-model selection (GPT, Claude, Gemini), but it **lacks multi-agent workflow orchestration**. A GitHub feature request (#185990) from January 2026 documents:

- No agent delegation / subagent coordination
- Static model selection (cannot change mid-session)
- No workflow definition language
- No durable state with checkpointing

This gap is real, but it's fillable without MAF (see Part 7).

---

## Part 2: The Microsoft Agent Framework — Honest Capability Assessment

### 2.1 What MAF Actually Ships (v1.0 GA, April 2026)

MAF v1.0 consolidates Semantic Kernel (~22K GitHub stars) and AutoGen (~53K stars) into a single framework. The unification resolved a real problem — two years of parallel development with incompatible APIs that confused the developer community. As the OpenAIToolsHub review notes: *"Developers kept asking 'Which one should I use?' Microsoft's answer for months was a vague 'it depends on your use case,' which satisfied nobody."*

Key components:

| Component | Description |
|---|---|
| **Agent Pipeline** | 3-layer architecture: Agent Middleware → Context Layer → Chat Client Layer |
| **Workflow Orchestration** | Pregel-style BSP superstep graph with 5 built-in patterns (Sequential, Concurrent, Handoff, GroupChat, Magentic) |
| **AgentSession** | Conversation state container with serialization/restoration |
| **Provider Matrix** | 6 providers: Azure OpenAI, OpenAI, Anthropic, Bedrock, Gemini, Ollama |
| **MCP + A2A** | First-class support for Model Context Protocol and Agent-to-Agent Protocol |
| **Observability** | OpenTelemetry instrumentation (traces, metrics, logs) |
| **DevUI** | Local web-based debugging tool |
| **Declarative YAML** | Workflow definition via YAML with PowerFx expressions |
| **Foundry Agent Service** | Cloud deployment with per-request micro-VM isolation |

### 2.2 Microsoft's Own Design Rationale

Microsoft's Command Line blog articulates the layered design clearly:

> "Agent loops, workflows, and harnesses let developers choose the right architecture to support simple assistants and complex multi-agent systems."

The framework is organized around three ideas:
- **Agent loops**: The core execution pattern connecting models, conversations, tools, and state
- **Workflows**: Structured orchestration for multi-step, multi-agent, or business-critical processes
- **Harnesses**: Reusable runtime capabilities (tools, context, memory, planning, controls, middleware)

This is well-engineered. The question is not whether the engineering is good — it's whether the engineering is **necessary** given what frontier SDKs now provide natively.

### 2.3 The Provider Capability Matrix — Where the Abstraction Breaks

Microsoft's own documentation reveals the lossy nature of the provider abstraction:

| Capability | Azure OpenAI | OpenAI | Anthropic | GitHub Copilot | Ollama |
|---|---|---|---|---|---|
| Function Tools | ✅ | ✅ | ✅ | ✅ | ✅ |
| Structured Output | ✅ | ✅ | ✅ | ❌ | ✅ |
| Code Interpreter | ✅ | ✅ | ✅ | ❌ | ❌ |
| File Search | ✅ | ✅ | ❌ | ❌ | ❌ |
| MCP Tools | ✅ | ✅ | ✅ | ✅ | ❌ |
| Background Responses | ✅ | ✅ | ❌ | ❌ | ❌ |

**Analysis:** The "one-line provider swap" claim is technically true at the API call level — but functionally misleading. Swapping from Azure OpenAI to Anthropic loses File Search and Background Responses. Swapping to Ollama loses Code Interpreter, File Search, MCP, and Background Responses. Workflows that depend on any of these features **silently break** on provider swap.

**The abstraction gives you the intersection of all providers' capabilities. But the value of each provider is in its unique capabilities — the things that don't survive the abstraction.**

---

## Part 3: Industry Critiques — A Calibrated Assessment

### Important Calibration Note

**Neither Anthropic nor OpenAI has directly and publicly criticized MAF.** The critiques documented below come from independent practitioners, industry analysts, distributed-systems engineers, and security researchers — not from competing frontier labs. However, both Anthropic and OpenAI have increasingly promoted architectural ideas that can be read as indirect philosophical divergence from MAF's approach:

- More model autonomy, less rigid orchestration
- Dynamic planning over hard-coded workflows
- Agent loops that adapt rather than follow predetermined graphs
- Emphasis on observability, evaluation, and tool safety rather than elaborate orchestration layers
- Preference for lightweight abstractions that expose model capabilities instead of hiding them

### 3.1 Too Much Abstraction / Orchestration Overhead

MAF inherits concepts from both Semantic Kernel and AutoGen, resulting in workflows, graphs, middleware, sessions, checkpoints, agent loops, harnesses, and orchestration primitives.

Critics argue that for many real-world applications, a simple agent loop plus tools is easier to reason about and maintain than a graph-heavy orchestration system. The OpenAIToolsHub review notes: *"The graph abstraction adds complexity for simple single-agent use cases"* and describes the framework as having *"more boilerplate than lighter alternatives."*

This is probably the closest thing to the "Anthropic/OpenAI philosophy gap." Both companies' SDKs favor lightweight agent loops where the model decides the next step, rather than encoding decisions into workflow graphs.

**What Anthropic would likely criticize (inferred, not stated):** Graph-centric orchestration, excessive workflow definitions, over-structuring agent behavior, framework logic replacing model reasoning. Anthropic has increasingly moved toward long-running autonomous agents, subagents, and model-driven planning with minimal orchestration constraints.

**What OpenAI would likely criticize (inferred, not stated):** OpenAI's recent direction (Responses API, Agents SDK, Operator-style systems) suggests a preference for lightweight orchestration, tracing and evaluation, tool calling, and handoff patterns — rather than large enterprise workflow abstractions. The likely criticism is that some MAF workflows encode decisions that modern frontier models can make themselves.

### 3.2 Framework Complexity vs. Model Capability

A recurring argument in the agent community, articulated by Joey Hipolito:

> "As models get smarter, orchestration frameworks become less valuable."

Instead of encoding logic into workflow graphs, developers increasingly let Claude, GPT, or other frontier models decide the next step themselves. This isn't a direct attack on MAF specifically, but it is a critique of large orchestration frameworks generally.

**The strongest version of this critique:** MAF may be solving the 2024 agent problem (orchestration) while frontier labs increasingly think the 2026 problem is context management, agent operations, reliability, and autonomy.

### 3.3 Microsoft Ecosystem Sprawl

Forbes published a pointed analysis after MAF 1.0 shipped:

> "Microsoft's agent story still spans too many surfaces across build, deployment, governance and distribution. Google Cloud and AWS each present more coherent default paths from framework to managed runtime."

The article details the fragmentation:
- **Build layer:** Agent Framework (pro-code) + Copilot Studio (low-code)
- **Runtime layer:** Foundry Agent Service (hosted) + local InProcess runner
- **Distribution:** Microsoft 365 Agents SDK (Teams/Copilot) + Azure OpenAI (native)
- **Governance:** Agent Governance Toolkit (separate project) + Agent 365 ($15/user/month)

**Microsoft's own IT team** hit this confusion when building an employee self-service agent — they evaluated Copilot Studio, Azure AI Foundry, and Microsoft 365 Copilot, started with one, found it insufficient, and concluded that *"different use cases called for different combinations of all three platforms."*

If Microsoft's own people can't navigate their own agent stack, that's a product coherence problem, not a user education problem.

### 3.4 Durability and Recovery Concerns — "Still Not Durable"

Diagrid CTO Yaron Schneider published a detailed technical analysis:

> "Microsoft's Agent Framework has the most explicitly designed checkpointing system of any agent framework I've reviewed... On paper, this is well-engineered. In practice, it has the same gap as every other framework."

The specific findings:
- **Resume is entirely manual** — the `restore_from_checkpoint` method requires the caller to provide an explicit `checkpoint_id`. There is no supervisor, no scheduler, no automatic restart.
- **No automatic failure detection** — if a process crashes mid-workflow, the checkpoint sits in storage until something external decides to use it.
- **At scale** — hundreds of concurrent workflows require developers to build the entire detection-and-retry infrastructure themselves.

This critique applies equally to LangGraph, CrewAI, and Google ADK — MAF is not uniquely deficient here. But the criticism is that Microsoft presents checkpointing as a "production-grade" feature when it stops short of true durable execution.

### 3.5 Security and MCP Attack Surface

Lyrie Research published a security analysis covering the entire agent framework ecosystem, including Semantic Kernel and related Microsoft tooling:

Security researchers argue that orchestration frameworks can create larger attack surfaces through:
- Prompt injection via tool results
- MCP server supply-chain risks
- Agent permission escalation through tool abuse
- Framework-level vulnerabilities that affect all agents running on the platform

These concerns are not unique to Microsoft but are amplified by the number of integration surfaces MAF exposes.

### 3.6 Enterprise-First Design (Not a Bug, But a Cost)

The OpenAIToolsHub review describes MAF as *"the strongest enterprise-oriented agent framework available — but 'enterprise-oriented' also means more boilerplate than lighter alternatives."*

Common complaints from practitioners:
- More boilerplate than Claude Agent SDK or OpenAI Agents SDK
- More concepts to learn (agent loops, workflows, harnesses, executors, supersteps, middleware, context providers, sessions)
- Heavier architecture for simple use cases
- Strong alignment with Azure environments

Meanwhile, frameworks like LangGraph, OpenAI Agents SDK, Claude Agent SDK, or lightweight custom loops get praised for faster iteration.

### 3.7 The Duplication Problem

Every core MAF capability now exists natively in at least two frontier provider SDKs:

| MAF Capability | Claude Agent SDK | OpenAI Agents SDK | Google ADK 2.0 |
|---|---|---|---|
| Agent + system prompt | ✅ | ✅ | ✅ |
| Built-in tools | ✅ (9 tools) | ✅ (sandbox, file I/O) | ✅ (search, code exec) |
| Multi-agent / subagents | ✅ Native spawning | ✅ Handoffs | ✅ Collaborative modes |
| Orchestration | ✅ Agent loop + delegation | ✅ Runner + handoff chains | ✅ Graph workflows |
| State / sessions | ✅ Checkpoint resume | ✅ SQLite/Redis | ✅ Graph state checkpoints |
| Guardrails / safety | ✅ Tool policies | ✅ Input/output guardrails | ✅ Callbacks + evaluation |
| Human-in-the-loop | ✅ Permission system | ✅ Approval mechanism | ✅ Pause points |
| Tracing / observability | ✅ Tool invocation logs | ✅ Native tracing | ✅ Evaluation tools |
| MCP support | ✅ Native | ✅ Native | ✅ Native |

The frontier SDKs aren't thin API wrappers anymore — they're full agent runtimes. MAF adds an orchestration layer on top of runtimes that already have orchestration built in.

---

## Part 4: What MAF Genuinely Offers (The Honest Short List)

After removing all duplicated and degraded capabilities, MAF's unique value reduces to:

### 4.1 Multi-Model Orchestration in a Single Typed Workflow ✅

No frontier SDK can natively run a workflow where Agent A uses Claude, Agent B uses GPT, and Agent C uses a local Ollama model — all with typed message passing and BSP synchronization barriers.

**However:** This is achievable without MAF through CLI-level dispatch. A Python script can shell out to `claude -p`, `copilot`, and `gemini` CLIs, collect results, and coordinate via SQLite. The orchestration is less typed but equally functional — and each model runs at full native capability instead of through MAF's lossy wrapper.

**Verdict:** Genuine unique capability, but the trade-off (typed orchestration vs. provider capability loss) makes it situationally valuable, not universally valuable.

### 4.2 .NET First-Class Support ✅

MAF is the only agent framework with first-class C#/.NET support.

**Verdict:** Genuine differentiator. Irrelevant for Python-primary teams.

### 4.3 BSP Superstep Workflow Graph with Compile-Time Type Validation ✅

MAF's `WorkflowBuilder` validates that message types between connected executors are compatible before execution begins. No other framework does compile-time workflow validation.

**Verdict:** Real engineering value. For solo developers iterating rapidly, the difference between "fails at compile time" and "fails on first run" is negligible. For large teams with complex workflows, this matters more.

### 4.4 FIDES Prompt Injection Defense ✅

Information-flow control with integrity/confidentiality labels — a novel security primitive shipped May 2026. Not available in any other framework.

**Verdict:** Genuinely novel. Worth monitoring independently of MAF adoption.

---

## Part 5: The Agent Governance Toolkit — The Real Product

### 5.1 AGT Is Framework-Agnostic

AGT is a separate open-source project (3.4K GitHub stars) that plugs into **any** agent runtime, not just MAF. It has dedicated adapters for:

| Runtime / Framework | Adapter |
|---|---|
| Claude Code | `agent-governance-claude-code` |
| Copilot CLI | `agent-governance-copilot-cli` |
| Antigravity CLI | `agent-governance-antigravity-cli` |
| LangChain | `LangChainKernel.as_middleware()` |
| CrewAI | `CrewAIKernel.as_hooks()` |
| OpenAI Agents SDK | `OpenAIAgentsKernel.as_hooks()` |
| Google ADK | `GoogleADKKernel.as_plugin()` |
| Pydantic AI | `PydanticAIGovernanceCapability` |
| LlamaIndex | Native integration |
| MAF | `GovernancePolicyMiddleware` (one of 12+ integrations) |

### 5.2 AGT's Seven Packages

| Package | Purpose |
|---|---|
| **Agent OS** | Core policy engine — PEP/PDP pair evaluating YAML, OPA Rego, or Cedar rules. Sub-millisecond, deterministic, hallucination-free |
| **Agent Mesh** | Zero-trust identity using DIDs + Ed25519 keys, behavioral trust scoring (0–1000) |
| **Agent Runtime** | Privilege rings, saga orchestration, kill switch |
| **Agent SRE** | SLOs, error budgets, circuit breakers, chaos engineering |
| **Agent Compliance** | Automated compliance grading against EU AI Act, HIPAA, SOC2, OWASP Agentic Top 10 |
| **Agent Marketplace** | Plugin lifecycle management |
| **Agent Lightning** | RL training governance |

### 5.3 Production Validation

Microsoft's own AI team runs AGT in production without MAF:

> "11 specialized agents running concurrently against production repositories... 473 denials over an 11-day window — 473 times an agent tried to execute an unauthorized action and was hard-blocked. Every single incident caught deterministically in under 8 milliseconds."

### 5.4 The Key Insight

> "The fundamental problem with prompt-based governance is the recursive trust issue: You are using an LLM to decide whether an LLM should be allowed to do something."

AGT replaces cognitive governance (LLM reads instructions) with deterministic governance (code evaluates policy). This is the most architecturally significant contribution in Microsoft's entire agent ecosystem — and it doesn't require MAF.

---

## Part 6: What SDK Programmatic Access Actually Provides Over CLI + Markdown

While MAF is not recommended, the frontier SDKs' programmatic interfaces offer genuine improvements over CLI + markdown agent operation:

### 6.1 Deterministic Control Flow

**CLI + Markdown:** LLM reads SKILL.md, interprets checkboxes, decides what to route where. Routing is probabilistic — subject to hallucination, attention drift, and context pressure.

**SDK Programmatic:** Code queries the database, selects the next task, calls `agent.run()`. The LLM does the work, not the routing. No LLM in the control path.

### 6.2 Schema-Enforced Structured Output

**CLI + Markdown:** LLM returns "JSON" — usually correct, sometimes wrapped in markdown fences, sometimes with hallucinated fields.

**SDK Programmatic:** `agent.run(output_schema=TaskResult)` — the SDK validates the response against the schema before your code sees it. Malformed output is retried automatically.

### 6.3 Typed Streaming Event Hooks

**CLI + Markdown:** `dispatch.py` captures stdout/stderr after completion. No visibility during execution.

**SDK Programmatic:** Typed event stream — every tool call, text chunk, and error — as it happens. Can log, gate, or kill mid-execution.

### 6.4 Session Serialization / Crash Recovery

**CLI + Markdown:** Session crash loses conversation context. Task state survives (via SQLite), but the LLM's reasoning chain is gone.

**SDK Programmatic:** `session.serialize()` / `Session.deserialize()` — full conversation history, tool call results, and reasoning chain survives crashes.

### 6.5 Embedded Agent-in-Application

**CLI + Markdown:** Agents require a human at a terminal.

**SDK Programmatic:** Agent runs inside a web API, Slack bot, CI pipeline, or any application.

### 6.6 Recommendation

Cherry-pick these deterministic primitives from whichever SDK you're running inside (Claude Agent SDK when in Claude Code, Copilot SDK when in Copilot CLI). Wire them through your existing enforcement layer. Do not adopt a separate framework — use the native SDK of whatever runtime you're in.

---

## Part 7: The Correct Architecture

### 7.1 Design Principles

1. **Agent identity files (`.md`) are the portable interface definition** — consumed by any LLM CLI runtime without modification
2. **Enforcement scripts (`state_engine.py`, `sandbox_runner.py`) are standalone Python** — called via subprocess or Python import from any runtime
3. **Each frontier model CLI is used at full native capability** — no wrapper degradation
4. **Protocol exposure (MCP + A2A) provides interop** — without abstracting over runtimes
5. **Governance (AGT) and observability (OpenTelemetry) are adopted independently** — no framework dependency

### 7.2 Architecture Stack

```
Layer 1: Agent Identity        → .md files (portable, any runtime)
Layer 2: State Management      → state_engine.py (SQLite WAL, standalone)
Layer 3: Process Isolation     → sandbox_runner.py (standalone)
Layer 4: Governance (future)   → AGT (pip install, framework-agnostic)
Layer 5: Observability (future)→ OpenTelemetry (pip install, standard)
Layer 6: Runtime               → Claude Code / Copilot CLI / Gemini CLI
                                  (native SDKs at full power)
Layer 7: Protocol Interop      → MCP + A2A (when needed)
```

### 7.3 Multi-Model Without MAF

The plugin architecture already supports multi-model orchestration:

```
Claude Code (orchestrator)
    ├──► dispatch.py --cli claude  (Claude subagent)
    ├──► dispatch.py --cli gemini  (Gemini subagent)
    ├──► dispatch.py --cli copilot (Copilot subagent → GPT/Claude/Gemini)
    └──► state_engine.py collects all results into SQLite
```

Each model runs at full native capability. Adding a new model is adding a `--cli` flag, not writing a provider adapter.

### 7.4 Future SDK Integration (Post-v1.3)

When deterministic routing, structured output, and session serialization are needed, adopt SDK primitives directly — not through MAF:

```python
# Deterministic orchestrator — no LLM in the routing path
async def run_workflow(session_id):
    conn = state_engine.init_db(DB_PATH)
    while True:
        task = state_engine.get_next_pending(conn, session_id)
        if not task:
            break
        result = await agent.run(
            f"Implement {task.component_name}",
            output_schema=TaskResult,       # SDK: deterministic schema
            session=saved_session,           # SDK: deterministic state
            tools=[state_engine_tools],      # SDK: deterministic tool access
        )
        state_engine.commit_task_complete(
            conn, task.id, agent_id, task.version,
            payload_hash=hash(result),
            tdd_report=result.tdd_evidence   # Typed, not parsed from text
        )
```

The SDK provides the determinism. The enforcement layer provides the safety. Neither replaces the other.

---

## Part 8: MAF Adoption Decision

### 8.1 Decision: NOT ADOPTED

MAF provides no capabilities that this plugin architecture lacks for its current use case:
- Multi-model orchestration: `dispatch.py` routes to any CLI runtime
- Cross-runtime portability: `.md` files work in Claude/Copilot/Antigravity/Gemini
- Durable state: `state_engine.py` with SQLite WAL
- Workflow coordination: task leasing, CAS completion, phase gating

Adopting MAF would **degrade** capabilities by wrapping frontier SDKs through a lossy abstraction layer that strips provider-specific features.

### 8.2 Fair Acknowledgment

MAF is not bad engineering. The Semantic Kernel + AutoGen unification was necessary and well-executed. The BSP superstep model is architecturally sound. The middleware pipeline is cleanly designed. The DevUI debugger is genuinely useful. For .NET enterprise teams running multi-provider workflows in regulated environments, MAF is the strongest option available.

The critique is not about engineering quality — it's about **architectural fit**. For a solo/small-team developer using frontier model CLIs at full native power with a custom enforcement layer, MAF adds overhead and removes capabilities.

### 8.3 Adopted Instead (Standalone, No Framework Dependency)

| Component | Source | Status |
|---|---|---|
| **SQLite Control Plane** | Custom (`state_engine.py`) | v1.3 plan — in progress |
| **Process Sandboxing** | Custom (`sandbox_runner.py`) | v1.3 plan — in progress |
| **HMAC Dispatch Envelopes** | Custom (`sandbox_runner.py`) | v1.3 plan — in progress |
| **TDD Enforcement Gates** | Custom (`state_engine.py`) | v1.3 Tasks 12-14 — planned |
| **Git Worktree Isolation** | Custom (`sandbox_runner.py`) | v1.3 Tasks 12-14 — planned |
| **OpenTelemetry** | `pip install opentelemetry-sdk` | Future — framework-agnostic |
| **AGT Governance** | `pip install agent-governance-toolkit` | Future — framework-agnostic |

### 8.4 Reassessment Triggers

Revisit MAF adoption if any of these conditions become true:

1. A team of 5+ developers needs a shared, standardized agent orchestration pattern
2. Regulatory compliance requires a certified workflow runtime backing AGT's audit framework
3. The architecture moves to .NET
4. MAF's provider wrappers achieve full feature parity with native SDKs

None of these conditions are met today. Reassess quarterly.

---

## Part 9: Billing Awareness

### 9.1 Claude Agent SDK Credit Pool (Effective June 15, 2026)

Anthropic is splitting billing into two pools:

| Pool | Contents | Impact |
|---|---|---|
| **Interactive Pool** | Claude Code terminal interaction, Claude.ai chat, Cowork | Normal subscription usage — unchanged |
| **Agent SDK Credit Pool** | `claude -p` headless mode, Agent SDK calls, GitHub Actions | `dispatch.py` subagent spawns move to this pool |

Budget gates in `state_engine.py` (`max_parallel_agents`, `max_premium_calls_per_phase`) directly control spend against the Agent SDK Credit Pool. These economic controls are billing safeguards, not optional optimizations.

---

## Appendix A: Complete MAF Component Inventory

For reference, the full MAF v1.0 component list:

1. **Agent** — Core building block wrapping LLM client + instructions + tools + middleware
2. **Pipeline Architecture** — 3-layer: Agent Middleware → Context Layer → Chat Client Layer
3. **AgentSession** — Conversation state with serialization/restoration
4. **Tools** — Function Tools (local) + MCP Tools (standard) + Hosted Tools (Code Interpreter, File Search)
5. **Workflow Orchestration** — BSP superstep graph: Sequential, Concurrent, Handoff, GroupChat, Magentic
6. **Interoperability** — A2A (agent-to-agent) + MCP (agent-to-tool), both first-class
7. **Provider Matrix** — 6 providers swappable (with capability degradation per matrix above)
8. **Agent Governance Toolkit** — 7 packages (framework-agnostic, works without MAF)
9. **Observability** — OpenTelemetry traces, metrics, logs
10. **DevUI** — Local web debugger
11. **Foundry Agent Service** — Cloud deployment with per-request micro-VM isolation
12. **Declarative YAML** — Workflow definition with PowerFx expressions

## Appendix B: Key Sources

| Source | Author / Org | Date | Key Finding |
|---|---|---|---|
| MAF 1.0 GA Announcement | Microsoft | April 2026 | Semantic Kernel + AutoGen unification |
| "Claude Agent SDK + Agent Framework" | Microsoft Azure Feeds | 2026 | Official integration guidance |
| "Microsoft's Agent Stack Confuses Developers While Rivals Simplify" | Forbes (Janakiram MSV) | April 2026 | Ecosystem fragmentation critique |
| "Agent Frameworks Are Solving the Wrong Problem" | Joey Hipolito | March 2026 | Model capability vs. framework complexity |
| "Still Not Durable: How MAF and Strands Repeat the Same Mistakes" | Diagrid (Yaron Schneider) | March 2026 | Checkpointing is manual, not durable |
| "The Agentic Framework Supply Chain Crisis" | Lyrie Research | May 2026 | MCP and tool integration security risks |
| "Microsoft Agent Framework — Semantic Kernel Meets AutoGen in One SDK" | OpenAIToolsHub | April 2026 | Enterprise-strong but boilerplate-heavy |
| "How We Designed a Layered SDK" | Microsoft Command Line | 2026 | Agent loops, workflows, harnesses rationale |
| Agent Governance Toolkit GitHub | Microsoft (open source) | Ongoing | 12+ framework adapters, 3.4K stars |
| Claude Agent SDK Documentation | Anthropic | 2026 | Same runtime as Claude Code |
| Claude Code Billing Changes | Anthropic | June 2026 | Agent SDK credit pool split |
| Provider Capability Matrix | Microsoft Docs | 2026 | Feature degradation across providers |

## Appendix C: Critique Calibration Statement

This assessment critiques MAF's **architectural fit** for a specific use case (solo/small-team development using frontier model CLIs). It does not claim:

- That MAF is poorly engineered (it isn't — the BSP model and middleware pipeline are well-designed)
- That Anthropic or OpenAI have publicly criticized MAF (they haven't — the philosophical divergence is inferred from their product directions)
- That MAF is never the right choice (it is — for .NET enterprise teams running multi-provider workflows in regulated environments)
- That MAF will remain limited (the provider capability matrix may reach parity in future releases)

The critique is that **for this specific architecture and use case**, MAF adds overhead and removes capabilities. For other architectures and use cases, the calculus may differ.
