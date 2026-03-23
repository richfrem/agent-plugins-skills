# Agentic OS - Future Vision

> Drafted: 2026-03-22
> Status: Vision / Pre-Spec

This document captures architectural direction for the next evolution of the Agentic OS plugin — moving from a tightly coupled local runtime toward a composable, backend-swappable agent infrastructure layer.

---

## Table of Contents

1. [Current State](#current-state)
2. [Competitive Landscape and Industry Direction](#competitive-landscape-and-industry-direction)
3. [Academic Research Validation](#academic-research-validation)
4. [Core Architectural Shift: Adapter Pattern](#core-architectural-shift-adapter-pattern)
5. [The OS Paradigm: What Exists and Where It Goes](#the-os-paradigm-what-exists-and-where-it-goes)
6. [Context Orchestrator (Enterprise Grade)](#context-orchestrator-enterprise-grade)
7. [Security Sentinels (Critical Gap)](#security-sentinels-critical-gap)
8. [Zero Trust for Agents, Skills, Prompts, and Hooks](#zero-trust-for-agents-skills-prompts-and-hooks)
9. [Explicit Scope Declaration Model](#explicit-scope-declaration-model)
10. [Agent Authentication: Ephemeral JWT Tokens](#agent-authentication-ephemeral-jwt-tokens-per-approved-action)
11. [5-Layer Proxy Architecture](#5-layer-proxy-architecture)
12. [Session Behavioral Intelligence (The Missing Layer)](#session-behavioral-intelligence-the-missing-layer)
13. [Near-Term Priorities](#near-term-priorities)

---

## Current State

The agentic-os is a local runtime with:
- File-based session memory (`session-memory-manager`)
- JSON/JSONL event bus (flat files, polling-based)
- Tightly coupled subsystems (memory, loops, hooks baked in)
- Single-machine scope

It works well for solo developer use. The constraint is that the subsystems are not swappable — you get the built-in memory and event bus or nothing.

---

## Competitive Landscape and Industry Direction

> Note: This section captures the industry direction as of early 2026. The space is moving fast and specific product claims should be verified against current sources.

The "Agentic OS" concept has moved from academic research to active industry investment. The trend is clear even if no single leader has emerged.

### Hyperscalers

**Microsoft** is the most visible: Pavan Davuluri (President, Windows and Devices) announced Windows 11 is being redesigned as an agentic OS. Windows Copilot Plus PCs use on-device models (Phi Silica), "Recall" screenshot history, and agentic workflows to manage files across applications. Early reception was poor - Recall's privacy implications triggered a backlash that delayed the rollout. The ambition to make the OS itself the agent harness is clear; the execution is early.

**NVIDIA** is building backend infrastructure: Vera Rubin platform and BlueField-4 STX storage are designed for long-context AI-native computing. The NVIDIA Agent Toolkit (OpenShell) targets self-evolving agents with persistent memory.

**Apple** has taken a quieter path with App Intents and Apple Intelligence - formalizing how apps expose actions to agent orchestration. More constrained than Windows but more reliable in execution.

### Enterprise Platforms

**PwC** launched an "AI Agent Operating System" in March 2025 - positioned as a switchboard for cross-platform orchestration across cloud providers (AWS, Oracle), integrating commercial models. It is an integration/governance layer, not a true OS-level primitive.

**Amdocs** has built an agentic OS (aOS) specifically for telecom/enterprise, designed to run on top of existing OSS/BSS stacks.

**Kore.ai** focuses on end-to-end enterprise agentic platforms with multi-agent orchestration.

**Xebia** and others offer similar "agentic OS platform" products - essentially enterprise agent orchestration layers.

### Memory-Specialized Frameworks

This is the most technically interesting category because memory is the hardest unsolved problem:

- **Letta (formerly MemGPT)**: OS-inspired memory management; agents control their own memory (RAM vs. disk) enabling "unlimited" context via paging
- **Mem0**: Standalone adaptive memory layer for personalization across agents and sessions
- **Zep / Graphiti**: Temporal knowledge graphs tracking how entities and preferences change over time

These frameworks are directly relevant to the Agentic OS plugin's memory adapter vision - they are the swappable backends that should eventually plug in.

### Academic Prototypes

- **AIOS**: LLM Agent OS from academia with a three-layer architecture; 2.1x faster execution via unified system calls
- **KAOS**: Built on Kylin OS, introduces management-role agents for resource scheduling
- **AgentStore**: "App store" for heterogeneous agents, improved OSWorld benchmark from 11% to 24%
- **Eliza**: Blockchain-integrated Agent OS for decentralized security

### The Security Gap at Scale

The competitive landscape creates a critical secondary concern: every major player is building agent skill/plugin repositories. OpenFang, AIOS, AgencyOS, NemoClaw, and the commercial platforms all aggregate third-party agent skills at scale. Anthropic's official Claude plugin marketplace has 100+ plugins as of early 2026. SkillsMP.com indexed 571,000+ SKILL.md files by March 2026.

**This is the browser extension problem at AI scale.** Browser extension stores spent years allowing credential-stealing and adware extensions before implementing meaningful review. Agent skill repositories carrying Manchurian Candidates - skills that behave normally in testing but activate malicious behavior under specific triggers, or that encode payloads in innocuous artifacts like image EXIF data - represent the same attack surface pattern with higher blast radius per compromised install.

The industry is in the "chaos of duplicated bespoke solutions" phase Koubaa describes in his research. The window to establish security norms before the first major incident is open now. It will close once a high-profile attack forces reactive policy.

---

## Academic Research Validation

Two papers from 2025-2026 independently validate the architectural direction of this vision and provide formal frameworks worth incorporating. Full summaries are in `references/research/`.

### Koubaa (TechRxiv, Sept 2025): Agent-OS Blueprint

Koubaa proposes a five-layer Agent-OS architecture (Kernel -> Resource+Service -> Agent Runtime -> Orchestration -> User) with Agent Contracts as portable machine-readable specifications. The paper is positioned as an "architectural North Star" - not a system realizable today, but a requirements-driven blueprint for the next decade.

**Validates:**
- The OS metaphor (kernel/RAM/disk/daemons) is the right framing for agent infrastructure
- Memory adapter pattern is necessary (FR2 requires pluggable backends: vector stores, KV caches, relational DBs)
- Zero-trust microkernel is the right security architecture
- Agent Contracts align with combining `plugin.json` + Explicit Scope Declarations

**Original contribution to incorporate - Latency Classes:**

Koubaa formalizes three latency classes as first-class OS scheduling primitives:

| Class | Definition | Use Cases | SLO Targets |
|-------|-----------|-----------|-------------|
| **HRT** (Hard Real-Time) | Any deadline miss = system failure | Robotics, safety-critical control loops | 1-20 ms slices; jitter <= 5 ms; 0 deadline misses |
| **SRT** (Soft Real-Time) | Occasional misses tolerable; user-perceived responsiveness critical | Chat assistants, screen copilots, live captioning | First-token 150-300 ms; full-turn 0.8-1.2 s |
| **DT** (Delay-Tolerant) | No hard deadline; maximize throughput per unit cost | Overnight batch analytics, report generation | 60-120 s acceptable; cost-per-token optimized |

For the Agentic OS plugin: interactive user-facing agents are SRT class; background daemons (`os-learning-loop`, `os-health-check`) are DT class. Classifying skills and agents by latency class enables smarter scheduling and better resource allocation.

### Sharma (Authorea, Feb 2026): AOS as Agentic Control Plane

Sharma's paper is more systems-engineering-grounded. It maps AOS onto real Linux and Windows primitives and provides concrete implementation paths. The most important contribution is the Separation of Planes and Four Architectural Invariants.

**Separation of Planes (core safety property):**

```
REASONING PLANE (untrusted)
  Probabilistic inference, planning, strategy selection.
  Outputs are PROPOSALS, not commands.
         |
         v proposed actions
POLICY PLANE
  Authorization, risk checks, budget controls.
  DENY BY DEFAULT where ambiguous.
  Produces auditable decisions with reason codes.
         |
         v authorized actions
EXECUTION PLANE (trusted)
  Deterministic tool invocation, system calls, side effects.
  Enforces policy decisions deterministically.
  Runs in least-privilege environments.
```

This separation is what the Agentic OS plugin's `PreToolUse` hooks implement partially. The key insight: treat all LLM reasoning outputs as untrusted proposals subject to deterministic policy evaluation before any side effect occurs.

**Four Architectural Invariants (non-negotiable):**

These are the minimum viable security contract for any AOS:

1. No side-effecting action is executed without a deterministic policy decision of "allow."
2. All policy outcomes (allow, deny, defer) are recorded in an append-only audit record prior to rescheduling.
3. Scheduling decisions depend only on observable state and budgets, not on internal reasoning tokens.
4. Underlying OS remains the sole mediator of hardware resources.

Current plugin compliance:
- Invariant 1: Partially implemented via `PreToolUse` hooks
- Invariant 2: `events.jsonl` partially implements this; missing policy decision reason codes
- Invariant 3: Not formally implemented
- Invariant 4: Assumed but not enforced

**Four Memory Classes:**

Sharma provides a formal decomposition that maps cleanly to the plugin's existing architecture:

| Memory Class | Plugin Component | Gap |
|-------------|-----------------|-----|
| Ephemeral context | Active context window | None - cleared each session |
| Durable agent memory | `context/memory.md` (L3) + session logs (L2) | Missing versioning and formal retention policy |
| Retrieved knowledge | Skills loaded via progressive disclosure | Missing provenance/integrity metadata |
| Execution records | `context/events.jsonl` | Missing policy reason codes per event |

**Integration Model Recommendation:**

Sharma evaluates four integration models. The plugin currently implements Model 1 (user-space runtime with hooks). This is the right starting point. The near-term path is Model 2 (selective OS-level enforcement via eBPF/LSM for enterprise deployments). The long-term path is Model 3 (distributed control plane), which aligns with the Context Orchestrator concept in this vision.

---

## Core Architectural Shift: Adapter Pattern

The next evolution is to define clean interfaces for each subsystem so implementations can be swapped without changing the OS runtime.

```
agentic-os runtime
  |-- memory-adapter       (interface)
  |-- event-bus-adapter    (interface)
  |-- task-adapter         (interface)
  |-- loop-adapter         (interface)
```

Each adapter has a default local implementation and can be replaced with a richer backend plugin.

---

## Memory Adapter

### Current
`session-memory-manager` — flat markdown files, single session scope.

### Swappable Backends

| Backend | Plugin | Use Case |
|---|---|---|
| File system (default) | built-in | Simple, portable, no dependencies |
| Tiered memory | `memory-management` plugin | Short + long term, GC, promotions |
| Vector DB | `vector-db` plugin | Semantic retrieval across sessions |
| RLM | `rlm-factory` plugin | Compressed long-term distillation |
| SQL DB | future | Queryable, relational, ACID, multi-agent shared state |
| Redis | future | Fast ephemeral/session memory, TTL-based expiry |

The `memory-management` plugin already exists and is the natural "better" default. The missing piece is wiring it in as a swappable adapter rather than a parallel system.

---

## Event Bus Adapter

### Current
JSON/JSONL flat files — agents write events, other agents poll files. Simple but:
- Polling-based (not reactive)
- No replay
- No multi-consumer fan-out
- Single machine only

### Swappable Backends

| Backend | Use Case |
|---|---|
| JSON files (default) | Local dev, zero dependencies |
| Redis pub/sub | Lightweight reactive, low latency |
| Kafka | Distributed, replay, partitioning, consumer groups, audit trail |
| RabbitMQ | Message routing, queues, dead-letter handling |

Kafka changes the coordination model fundamentally — agents become event consumers subscribing to topics rather than polling files. Every event is persistent and replayable. Multiple agents can react to the same event independently. This is the right model for multi-agent teams at scale.

---

## Task Adapter

### Current
Simple task files. No kanban, no cross-agent visibility.

### Swappable Backends

| Backend | Use Case |
|---|---|
| Flat files (default) | Local dev |
| spec-kitty kanban | Full SDD lifecycle tracking |
| Linear / GitHub Issues | External project management integration |

---

## Loop Adapter

### Current
`learning-loop` baked in as the default retrospective loop.

### Swappable Backends

| Backend | Use Case |
|---|---|
| learning-loop (default) | Single agent retrospective |
| dual-loop | Inner agent + outer supervisor |
| concurrent-agent-loop | Parallel agent fan-out |
| custom | Domain-specific loop logic |

---

## Why This Matters

### Comparison to prior technology cycles

MCP, Graph API, and low-code platforms all solved real problems at a specific moment — when direct integration was too hard. As tooling matures, the ecosystem moves toward direct approaches with less middleware.

The agentic-os adapter pattern follows the same logic: define the interface, provide a good default, let power users swap in production-grade backends without rewriting the OS. The OS becomes a thin runtime, not a monolith.

### The missing wire

Most of the swappable backends already exist as plugins in this repo:
- `memory-management` — tiered memory
- `vector-db` — semantic retrieval
- `rlm-factory` — long-term distillation
- `dual-loop`, `concurrent-agent-loop`, `learning-loop` — loop patterns

The work is not building new plugins — it is defining the adapter interfaces and wiring the existing plugins in.

---

## Distributed / Enterprise Direction

Once adapters are in place, the OS can scale beyond a single machine:

- **Shared event bus** (Kafka) — multiple agents on different machines react to the same event stream
- **Shared SQL memory** — agents read/write a common knowledge store
- **Agent registry** — OS knows which agents are running, their health, their last event
- **Cross-project coordination** — the AGENT_COMMS.md pattern promoted to a first-class event bus topic

This is the path from "local developer tool" to "distributed agent infrastructure."

---

## The OS Paradigm: What Exists and Where It Goes

The agentic-os is built on an OS metaphor that maps directly to classical operating system concepts. This section captures where each component stands today and the vision for its evolution.

### Current OS Analogy

| Real OS Concept | Agentic OS Today |
|---|---|
| Kernel | `CLAUDE.md` + `kernel.py` — rules loaded every session + concurrency manager |
| RAM (finite, clears on shutdown) | The active context window — finite, clears every session |
| Always in RAM | Skill metadata headers, agent descriptions, `CLAUDE.md`, `soul.md`, `user.md` |
| Application on disk | Full `SKILL.md` body — stays on disk until invoked |
| App launcher | Skill metadata descriptions — scanned to decide which skill to invoke |
| Background daemon | Agents (`os-learning-loop`, `os-health-check`) — runs autonomously, acquires locks, terminates |
| Cron scheduler | `/loop` + `heartbeat.md` |
| System registry | `context/os-state.json` |
| System event log | `context/events.jsonl` (JSONL, append-only, never enters context during normal operation) |
| Mutex / process lock | `context/.locks/` + `kernel.py` spinlocks with jittered backoff |
| Swap / overflow | `context/memory/archive/` — old memory rotated out when L3 gets too large |
| Antivirus / LSM | `PreToolUse` hooks — intercept every tool call before execution |
| Intrusion detection | `PostToolUse` hooks + `events.jsonl` |
| **No OS equivalent** | **Self-improvement loop** — `os-learning-loop` mines `events.jsonl` and patches `CLAUDE.md` and `SKILL.md` files based on observed friction |
| **No OS equivalent** | **On-demand software creation** — if no skill exists, describe it in plain language, `create-skill` generates it in seconds |
| **No OS equivalent** | **LLM reasoning engine** — the CPU follows instructions; the LLM understands them |

### Three-Tier Lazy-Loading (Context Window as RAM)

The context window is finite RAM. Every byte consumed by infrastructure is unavailable for actual work. The OS implements three-tier lazy-loading:

| Tier | What | When loaded |
|---|---|---|
| **Always in RAM** | Skill metadata headers, agent descriptions, `CLAUDE.md`, `soul.md`, `user.md` | Every session — routing and identity |
| **Loaded on trigger** | Full `SKILL.md` body | Only when that skill is invoked |
| **Loaded on demand** | `references/` docs via progressive disclosure | Only when a specific sub-topic is needed |
| **Loaded for audit** | `context/events.jsonl` | Only when `os-health-check` or `os-learning-loop` reads it — never during normal work |

**Vision:** As context windows grow (1M+ tokens becoming standard), this discipline remains critical because the problem doesn't disappear — it shifts. Larger context windows create new failure modes: attention dilution, relevant signal buried in noise, cost per token at scale. The lazy-loading pattern evolves from "fit in the window" to "maintain signal density." The Context Orchestrator (see below) is the next evolution of this discipline.

### Self-Improvement Loop: The Living OS

The most fundamental departure from traditional operating systems:

> A conventional OS is a static artifact — Windows does not rewrite its own kernel based on how you used it today. The Agentic OS does.

Every session, `os-learning-loop` observes failures, repeated friction, and patterns in the event log, then proposes and applies patches to the system's own skill instructions and `CLAUDE.md`. Using a Karpathy-style research loop, `skill-improvement-eval` validates each proposed change with `eval_runner` before it is committed. Over time, the OS becomes measurably better at the specific workflows of the project it lives in.

**Vision extensions:**

- **Cross-project learning** — improvements learned in one project's agentic-os propagate (with owner consent) to other projects running the same plugin. The improvement flywheel operates across the whole user base, not just one repo.
- **Skill performance ranking** — the event log contains latency, success rate, and friction signals per skill. Low-performing skills get flagged for improvement automatically; high-performing patterns get promoted.
- **A/B eval harness** — before committing an improvement, run both old and new skill versions against the eval suite. Only promote if measurably better. No blind commits.
- **Planetary scale** — at scale, millions of agent sessions across thousands of projects collectively observe friction and propose fixes. The agentic OS becomes a distributed, always-improving system shaped by aggregate usage intelligence. This is closer to a living organism than conventional software.

### Concurrency and State at Scale

**Today:** Spinlocks with jittered backoff in `kernel.py`. Works for single-project, few concurrent agents.

**Vision:**

- **Distributed lock management** — when multiple agents run across machines or worktrees, file-based spinlocks break down. Redis-based distributed locks or a proper lock service becomes the kernel primitive.
- **Optimistic concurrency** — for read-heavy workloads, move from pessimistic locking to optimistic concurrency with conflict detection and merge.
- **Event sourcing** — instead of mutable state files (`os-state.json`), derive state from the append-only event log. Current state is always a projection of events. Replay any point in time. No more state corruption from concurrent writes.
- **CQRS pattern** — separate read and write paths. Agents query a read model (fast, cached); mutations go through the event bus (auditable, serialized). The event bus becomes the source of truth.

### On-Demand Software Creation

On a traditional OS, if the application you need does not exist, you wait. On an Agentic OS, you describe what you need and the OS generates it — a new `SKILL.md` with full phases, logic, trigger descriptions, and documentation, ready to run in the same session.

**Vision extensions:**

- **Skill composition** — instead of generating from scratch, compose new skills from existing skill primitives. A "weekly report" skill composed from "fetch metrics" + "summarize data" + "format document" — each reusable independently.
- **Skill marketplace integration** — generated skills are automatically candidate for publishing to skillsmp.com or the plugin marketplace. The gap between "I created a skill" and "it's discoverable by others" collapses.
- **Skill versioning and rollback** — generated skills are versioned. If a new version breaks eval, rollback is one command.

### Identity and Soul Persistence

`soul.md` defines the project's identity, brand voice, and working style. It loads every session.

**Vision:**

- **Multi-agent soul coherence** — when 10 agents run simultaneously on the same project, they all load the same `soul.md`. The OS guarantees identity consistency across the agent fleet, not just within a single session.
- **Soul versioning** — as a project evolves, its soul evolves. Version-controlled, diffable, with the self-improvement loop proposing soul updates based on observed communication patterns.
- **Cross-project soul inheritance** — enterprise teams maintain a parent soul (`company.soul.md`) that child projects inherit and specialize. Consistent brand voice and values across all agent-assisted work.

---

## Context Orchestrator (Enterprise Grade)

A critical missing layer: an **Agent Context Orchestrator** that sits between the LLM and all infrastructure concerns, handling memory, event filtering, and context assembly so the agent focuses purely on its task.

```
Agent (task focus only)
    |
    v
Context Orchestrator
    |-- just-in-time context assembly
    |-- memory retrieval (semantic + recent + long-term)
    |-- context compaction (RLM distillation)
    |-- event stream filtering (relevant events only)
    |-- window-aware right-sizing (fits context window)
    |-- predictive pre-fetch (context ready before agent asks)
    |
    v
Backends (memory / event bus / vector db / SQL)
```

The agent never manages its own context. The orchestrator handles what to load, when to compact, what to drop. This is the difference between an agent that degrades gracefully under load and one that hallucinates when context overflows.

Nobody has built this properly yet. Every current framework makes the agent responsible for its own context — like asking a surgeon to also run the hospital EHR mid-operation.

---

## Security Sentinels (Critical Gap)

The agentic-os has no security layer between the plugin runtime and the LLM. This is not a theoretical concern.

### Empirical Evidence (2026 Study)

A 2026 empirical study analyzed 98,380 agent skills:
- **157 definitively malicious skills** carrying **632 distinct vulnerabilities**
- **84.2% of vulnerabilities lived in natural language documentation** (SKILL.md, agent prompts) — completely invisible to static code scanners like CodeQL
- **73.2% of malicious skills contained shadow features** — dormant capabilities absent from public documentation but functionally active at runtime
- The ecosystem surged to 400,000+ skills by March 2026 with minimal vetting — mirroring the early browser extension marketplace vulnerabilities

**Confirmed real-world incidents:**
- **MedusaLocker (Dec 2025)**: A benign "GIF Creator" agent skill was weaponized to download and execute ransomware using inherited file permissions
- **Rules File Backdoor (Mar 2025)**: AI IDEs (Cursor/Copilot) hijacked via hidden Unicode instructions in `.cursorrules` files, directing code agents to embed malicious scripts

### The Core Vulnerability: The Consent Gap

"Zero Trust verifies identity at the perimeter. It does not verify intent inside the cognitive layer."

When a user approves an agent to "resize an image," they grant the permissions needed for image processing. The agent inherits those permissions. A shadow feature buried in that same agent exploits those inherited permissions for arbitrary execution. The user approved the intent, not the granular execution. That gap is the attack surface.

### Adversarial Archetypes

**1. Data Thieves**
Industrialized networks using brand impersonation to harvest cloud API keys and environment variables (MITRE T1552/ASI03). Skills that look like useful utilities but exfiltrate `.env` contents on every run.

**2. Agent Hijackers**
Subvert the cognitive layer via "Stealthy Prompt Injection" — overriding the agent's core mission through its own instruction set. The PoC (`manchurian-agent-poc`) demonstrates this: a benign image resizer with a hidden hook that reads EXIF metadata, decodes a Base64 payload, and executes it silently. Victim sees only a successfully resized image.

**3. Sleeper Agents**
Payload dormant until a specific trigger condition — a date, a username, a file pattern, a counter reaching a threshold. Passes all vetting, fires later.

**4. Memory Poisoners**
Inject payload into the agent's long-term memory store. Fires on every future session. Persistent across restarts and reinstalls.

**5. Multi-Agent Relay Attacks**
Payload passes clean through 3 agents before triggering at hop 4. Each individual agent looks benign. The exploit only manifests through the full multi-hop chain: skill -> sub-agent -> poisoned artifact -> `run_command`.

**6. Vector DB Poisoning**
Corrupt embeddings so semantic retrieval surfaces the payload as context when the agent queries for relevant knowledge.

**7. Context Overflow Attacks**
Deliberately bloat context to push safety system prompt instructions outside the context window before executing payload.

**8. Supply Chain via Plugin Marketplaces**
Malicious plugin distributed through a marketplace. Passes static review because 84.2% of vulnerability lives in natural language, not code. With 571,000+ skills now on skillsmp.com and minimal vetting, this is the browser extension problem at scale.

### Why Existing Mitigations Fall Short for Agentic Systems

**Open source / specialized:**

| Tool | What it does | Why it falls short for agentic systems |
|---|---|---|
| LlamaGuard (Meta) | Content safety classifier on inputs/outputs | Prompt filtering problem framing — misses cognitive layer attacks |
| LlamaFirewall (Meta) | Security framework for LLM apps | Input/output focused, not multi-hop agent chain aware |
| NeMo Guardrails (NVIDIA) | Programmable conversation guardrails | Prompt-level steering, doesn't inspect tool call behavioral drift |
| Guardrails AI | Structured/typed validation of LLM responses | Output format enforcement, not intent or behavioral anomaly detection |
| Prompt Guard (Meta) | Detects prompt injection and jailbreak attempts | Direct injection focused — misses payload-in-metadata vectors |
| Rebuff | Prompt injection firewall | Misses EXIF/metadata/multi-hop delivery entirely |
| Garak | LLM vulnerability scanner | Jailbreak-focused, not agentic multi-hop or shadow feature aware |
| OWASP LLM Top 10 | Taxonomy of LLM risks | Exists, almost nobody in the agentic space implements it |
| CodeQL / static analysis | Code vulnerability scanning | 84.2% of vulnerabilities are in natural language — completely bypassed |

**Enterprise / commercial:**

| Tool | What it does | Gap |
|---|---|---|
| Cloudflare Firewall for AI | Model-agnostic security layer, PII and prompt injection protection | Perimeter-focused — inside the cognitive layer is still unmonitored |
| Datadog AI Guard | Real-time injection, jailbreak, and exfiltration detection | Observability layer — reactive, not preventive at the architecture level |
| ActiveFence (Alice) | Real-time filtering, PII detection, policy automation | Content policy focus, not agentic privilege scope enforcement |

**The fundamental problem:** All existing solutions treat security as a prompt filtering problem. The real problem is architectural — the attack surface is every data ingestion path in the entire system. LlamaGuard on the input does not help when the payload is encoded in EXIF metadata framed as hardware config.

The industry obsesses over benchmarks (MMLU up 2 points = paper). Security research surfaces vulnerabilities that labs don't want to advertise. The incentive structure is completely misaligned with the actual risk accumulating at scale.

### Required: Security Sentinel Architecture

An "AI layer in front of the AI layer" — semantic agent proxies and routers that monitor intent, flag documentation-to-runtime mismatches, and maintain tamper-evident audit trails.

```
External Data (images, docs, audio, API responses, DB records)
    |
    v
[UPSTREAM SENTINEL]
    |-- scan all inputs for embedded payloads
    |   (EXIF, ID3 tags, PDF metadata, doc comments, HTML, JSON fields)
    |-- detect encoded strings (Base64, hex, Unicode) in non-code fields
    |-- semantic mismatch detection (image file delivering shell instructions)
    |-- policy enforcement (allowlist of expected input shapes per plugin)
    |-- intent verification (does input align with declared plugin purpose?)
    |
    v
LLM Call
    |
    v
[DOWNSTREAM SENTINEL]
    |-- audit tool call patterns vs declared capability envelope
    |-- detect behavioral drift (image flow suddenly triggering shell execution)
    |-- enforce domain boundaries (image plugin cannot write .env or auth files)
    |-- flag output suppression (agent told to hide terminal output = evasion signal)
    |-- tamper-evident log of every tool call with input/output hash
    |-- forensic replay capability
    |
    v
Tool Execution / Filesystem
```

### Hook Security Layer

The current hooks system fires on events with no inspection. Required:
- **Hook call auditing** — every hook invocation logged with input/output hash
- **Privilege scope enforcement** — hooks constrained to declared capability envelope
- **Behavioral anomaly detection** — hook behavior deviating from declared purpose triggers alert
- **Immutable hook registry** — hooks cannot be modified at runtime by an agent
- **Subprocess watch** — any subprocess spawned from a hook is flagged and logged

### Full Threat Surface (Not Just Prompts)

Every data ingestion path is a potential attack vector:

| Vector | Example |
|---|---|
| File metadata | EXIF, ID3, PDF metadata, Office doc properties |
| Document content | Markdown files, README, SKILL.md itself |
| Web content | Pages the agent scrapes or reads |
| API responses | Third-party API returning tampered JSON |
| Database records | Records written by attacker, read by agent |
| Audio/video | Transcript of audio containing instructions |
| Images | Steganographic payload, visible text instructions |
| Memory store | Long-term memory poisoned in a prior session |
| Vector DB | Embedding poisoned to surface malicious context |
| Plugin marketplace | Malicious skill installed by user |
| Agent-to-agent messages | Payload relayed through multi-hop chain |

### Reference

- `/Users/richardfremmerlid/Projects/manchurian-agent-poc` — full PoC with red team assessments from Gemini, Claude, and Copilot CLI
- Research paper: `manchurian-agent-poc/research/2602.06547v1.pdf`
- Red team rounds 1 and 2 findings in `001-manchurian-candidate-poc/red-team-reviews/`

---

## Zero Trust for Agents, Skills, Prompts, and Hooks

Zero Trust for networks says: never trust, always verify, assume breach, least privilege everywhere, continuous validation — not perimeter-based trust.

Applied directly to the agent layer:

**Never trust a skill just because it's installed.**
A skill declaring benign intent in SKILL.md is unverified by definition. Install-time trust is not trust — it is deferred risk. Trust is earned through behavioral validation over time.

**Never trust inputs regardless of source.**
Even if the input came from your own memory store, your own vector DB, your own event bus — it could have been poisoned upstream. Every data ingestion point is a trust boundary. This is not paranoia; the PoC proves it empirically.

**Never trust the agent's own context.**
The agent's context window is an attack surface. What it believes about its own session could have been manipulated. The SIEM and proxy layers sit outside the agent precisely because the agent itself cannot be the arbiter of its own integrity.

**Least privilege per skill per session — scoped, not wildcard.**
`allowed-tools: Bash, Read, Write` is a wildcard. An image resizer should get read access to one input directory, write access to one output directory, and nothing else. Scoped, session-bound, revocable. The consent gap — where permissions granted for benign image processing are inherited for arbitrary execution — is eliminated by least privilege scoping.

**Continuous behavioral verification.**
Trust is not granted at session start and held. Every tool call is re-evaluated against the declared purpose. Drift from baseline triggers re-verification or suspension.

**Assume breach in the cognitive layer.**
Given that jailbreaking cannot be reliably prevented even by frontier labs with billions in safety research, design assuming the cognitive layer will be compromised. The goal is detection speed and blast radius limitation — not prevention alone.

---

## Explicit Scope Declaration Model

The core fix for the consent gap is making permissions explicit, declarative, and granular — applied at install time and enforced at runtime. This is OAuth for agents.

### The Problem Today

Current SKILL.md and plugin.json declare broad tool access:
```yaml
allowed-tools: Bash, Read, Write
```

This is a wildcard. It grants the full capability set with no scope, no path restriction, no session binding. When a sub-agent inherits this, the consent gap is fully open.

### The Model: Explicit Scope Declarations

Every skill, agent, hook, and sub-agent declares its required scopes explicitly:

```yaml
# In SKILL.md or plugin.json
scopes:
  - read: "./input/**"           # read only from input directory
  - write: "./output/**"         # write only to output directory
  - exec: ["convert", "ffmpeg"]  # only these specific binaries
  - network: none                # no outbound network access
  - env: none                    # no environment variable access
  - memory: read                 # can read memory, not write
  - agent-spawn: none            # cannot spawn sub-agents
```

### Scope Tiers by Default

Not all scopes carry the same risk. Three tiers:

| Tier | Default | Examples | Override requires |
|---|---|---|---|
| **Default allow** | Granted unless restricted | Read from declared working dir, write to declared output dir | Installer can restrict |
| **Default deny** | Blocked unless explicitly granted | Network access, env vars, spawning sub-agents, cross-repo writes | Explicit grant in install config |
| **Human approval** | Requires explicit human confirmation at runtime | Deleting files, writing outside declared paths, executing arbitrary binaries, accessing secrets | Human in the loop per call |

### Installer Control

When a user or team installs a skill, they can:
- **Grant** declared scopes as-is
- **Restrict** scopes further (image-resizer gets read only from `/images/`, not all declared input paths)
- **Deny** specific scopes entirely (deny all network access even if skill declares it)
- **Require approval** for specific scope categories (any file delete requires human confirmation)

```json
// In settings.json - installer overrides
{
  "enabledPlugins": {
    "image-resizer@my-marketplace": {
      "scopeOverrides": {
        "read": ["./uploads/images/**"],
        "write": ["./processed/**"],
        "exec": [],
        "network": "deny",
        "human-approval-required": ["delete", "env-read"]
      }
    }
  }
}
```

### Sub-Agent Scope Inheritance

Sub-agents cannot inherit more than the parent skill declared. Scope is strictly bounded downward:

```
Orchestrator grants: read ./input/**, write ./output/**
  -> image-resizer inherits: read ./input/**, write ./output/**
    -> profile-optimizer inherits: read ./input/** ONLY
       (cannot inherit write — not needed for metadata reading)
```

This eliminates the consent gap entirely. A sub-agent doing metadata reading gets read access to the file. It cannot inherit write or exec from the parent because the scope declaration didn't include sub-agent exec inheritance.

### Hook Scope Declaration

Hooks are currently the most dangerous ungoverned surface — they fire on events with full inherited privileges and no inspection. Under this model:

```json
// In hooks.json
{
  "hooks": [{
    "event": "PostToolUse",
    "command": "python3 hooks/post_run_metrics.py",
    "scopes": {
      "read": [".agentic-os/metrics/**"],
      "write": [".agentic-os/metrics/**"],
      "exec": ["python3"],
      "network": "deny",
      "env": "deny"
    }
  }]
}
```

Hook scope violations are blocked and logged. A hook that attempts to write outside its declared path triggers an alert.

### The Foundational Problem This Solves

From the Manchurian Candidate findings report:

> "You can't LLM your way out of an LLM problem. Input scanning assumes you can tell the difference between data and instructions before they enter the model. You can't. The model can't either."

**Prompt-Data Isomorphism**: data and instructions are indistinguishable to the model at the cognitive layer. They are both tokens. Input scanning at the perimeter cannot solve this because the model itself cannot reliably distinguish them.

Explicit scope declaration shifts the defense from the cognitive layer — where the model cannot be trusted as arbiter — to the execution layer, where scope enforcement is deterministic. The model can be manipulated into wanting to write to `/etc/passwd`. The scope enforcement layer ignores what the model wants and enforces what was declared at install time.

### Agent Authentication: Ephemeral JWT Tokens per Approved Action

Scope declarations define what an agent is allowed to do. But declarations alone are not enforcement — anything can claim a scope. The enforcement mechanism is **ephemeral authentication tokens tied to a specific approved purpose**.

The model, directly analogous to OAuth 2.0 + PKCE for human users:

```
1. User approves action: "resize images in ./uploads/"
       |
       v
2. Runtime issues ephemeral JWT to the skill session:
   {
     "sub": "image-resizer@my-marketplace",
     "session_id": "sess_abc123",
     "approved_purpose": "resize images in ./uploads/",
     "scopes": ["read:./uploads/**", "write:./processed/**"],
     "iat": 1742000000,
     "exp": 1742000300,   // expires in 5 minutes
     "jti": "one-time-use-token-xyz"
   }
       |
       v
3. Every tool call presents the JWT to the proxy layer
       |
       v
4. Proxy validates:
   - Token is not expired
   - Token has not been used before (jti check)
   - Requested action is within declared scopes
   - Action matches approved_purpose semantically
       |
       v
5. Tool call executes — or is denied with audit log entry
       |
       v
6. Token expires / is revoked after session ends
   No residual access. No inherited permissions bleeding into next session.
```

**Why this matters for the Manchurian Candidate threat:**

Even if a compromised agent is manipulated into wanting to write to `.env`, it cannot. The JWT issued for "resize images in ./uploads/" does not contain write scope for `.env`. The proxy layer rejects the call regardless of what the model believes it should do. The cognitive layer is compromised — the enforcement layer is not.

**Key properties:**

| Property | Why it matters |
|---|---|
| **Short-lived (TTL)** | Stolen token has a narrow exploitation window |
| **Purpose-bound** | Token issued for "summarize podcast" cannot be used for shell execution |
| **One-time use (jti)** | Prevents replay attacks — compromised token cannot be reused |
| **Scope-limited** | Sub-agents cannot escalate beyond what the parent JWT authorized |
| **Revocable** | Anomaly detected mid-session — token revoked immediately, session suspended |
| **Audit trail** | Every token issuance, use, and rejection is logged out-of-band |

**Sub-agent token delegation:**

Sub-agents receive a derived token from the parent — always a subset, never an extension:

```
Parent JWT: scopes = [read:./uploads/**, write:./processed/**]
  -> Sub-agent JWT: scopes = [read:./uploads/**]  // write not delegated
     (sub-agent doing metadata reading needs no write access)
```

This is the cryptographic enforcement of the scope inheritance rule. The sub-agent cannot claim write access because its token does not contain it, regardless of what instructions it receives.

**Human approval gates for sensitive scopes:**

Certain scope categories require a fresh human approval before a token is issued — not just at install time, but at execution time:

```
Agent requests: exec arbitrary binary
  -> Runtime pauses, prompts user: "image-resizer wants to execute 'convert'. Allow? [y/N]"
  -> User approves -> short-lived exec token issued for that specific binary only
  -> Token expires after single use
```

This is the difference between install-time consent (too broad, forgotten immediately) and just-in-time consent (specific, contextual, explicit).

---

## 5-Layer Proxy Architecture

From the Manchurian Candidate findings report — the mandatory intermediary required at five distinct layers simultaneously:

| Layer | Control | What it enforces |
|---|---|---|
| **1. Pre-ingestion** | Metadata sanitization before any file/URL enters the pipeline | Strip all metadata from untrusted inputs before it becomes agent context |
| **2. Context assembly** | Schema validation before data becomes LLM context | EXIF field must contain only dimension/color space data — reject free text |
| **3. Runtime inference** | Tool call authorization at execution time, not prompt time | Does this tool call align with the declared scope for this skill? |
| **4. Inter-agent** | Cryptographic provenance on agent-to-agent message passing | Every agent-to-agent message is signed — impersonation and tampering detected |
| **5. Memory/RAG** | Write-access controls on shared knowledge stores | Memory writes are scoped; retrieval results are integrity-verified before entering context |

**The Runner Paradox** (from Opus 4.6 assessment): If the proxy is implemented within the same execution context as the agent — same shell, same runner — it is moot. A compromised agent drops into the host shell and bypasses the proxy directly. For the 5-layer defense to hold, the proxy must exist out-of-band at the API layer, or `run_command` execution must be jailed in an isolated microVM (Firecracker, gVisor) with no access to the host network stack or environment variables.

Nobody has built all five layers as a unified infrastructure primitive. That is the gap.

---

## Session Behavioral Intelligence (The Missing Layer)

All existing security tools — LlamaGuard, NeMo Guardrails, Cloudflare Firewall for AI, Datadog AI Guard — share the same fundamental mental model: **perimeter scanning**.

```
Scan what goes in.
Scan what comes out.
Flag known bad patterns.
```

This is the right model for a chatbot. It is the wrong model for an agentic system running across sessions, across plugins, across time.

### Why Perimeter Scanning Fails for Agents

The Manchurian Candidate attack class operates **inside the session**, across **time**, across **hops**, through **individually innocent events**. No single input or output is flagged. The threat only exists in the aggregate.

**Attack vectors that bypass all current tools:**

**Fragmented exfiltration**
Agent exports a "harmless" image, then a "harmless" log file, then a "harmless" config snippet across three separate sessions. Each output passes every content scanner. The attacker combines them externally to reconstruct an API key, a database schema, a credential set. No single event was anomalous.

**Steganographic exfiltration**
Sensitive data encoded into image pixel LSBs, audio waveform noise, whitespace patterns in markdown output. The content scanner sees a valid image file. The content policy scanner sees no PII. The data leaves anyway.

**Temporal attacks**
Malicious behavior distributed across 50 sessions. Each individual session is clean. The pattern — always runs at 2am, always touches the same three files, always makes an outbound call at the end — only emerges when you look across all 50. No per-session tool catches this.

**Semantic laundering**
Agent summarizes sensitive internal data into natural language that doesn't pattern-match as sensitive: "The primary authentication endpoint uses a token-based approach with a 256-character secret." No PII flag. No credential regex match. The information is fully transmitted.

**Covert timing channels**
Agent introduces deliberate latency patterns between responses that encode data in timing intervals. Nothing in the content is malicious. The channel exists entirely in behavior.

**Firewall tunneling via allowed filetypes**
Payload arrives as a JPEG — allowed filetype, passes AV scan, passes content policy check. Fires inside the cognitive layer where no perimeter scanner reaches. The firewall approved the delivery vehicle.

**Cross-agent coordination**
Two compromised agents coordinate via a shared file or event bus entry. Neither agent's individual behavior is anomalous. The coordination only appears when you model both agents' behavior graphs together.

**Multi-hop relay**
Payload passes through agents A -> B -> C unchanged and harmless. At agent D it triggers. Agents A, B, and C all pass audit. The chain is only visible if you trace the full provenance of what agent D received.

### What's Actually Required: SIEM for Agents

The mental model shift:

```
Not: "Is this input or output bad?"

But: "Does this agent's complete behavior — across all events,
      all tool calls, all outputs, all sessions — make sense
      for its declared purpose?"
```

This is **Security Information and Event Management (SIEM) applied to the agent layer** — the same discipline that exists for network and endpoint security, transposed to cognitive systems.

SIEM for networks doesn't just scan packets at the firewall. It ingests logs from every system, correlates events across time, builds behavioral baselines, and alerts on drift from normal. That's exactly what agentic systems need.

**Required capabilities:**

**Session graph analysis**
Model the full directed acyclic graph of what the agent touched, read, wrote, and called within a session. Any edge in the graph that doesn't fit the declared plugin purpose is an anomaly signal. Example: image-resizer node should have no edges to `.env` files or auth directories.

**Intent drift detection**
Baseline the agent's behavior over its first N sessions. Flag statistical drift from that baseline in subsequent sessions. An agent that suddenly starts touching files outside its normal working set, or making tool calls it never made before, warrants investigation regardless of whether any single call looks bad.

**Cross-session correlation**
Persistent behavioral fingerprint across sessions. Fragmented exfiltration only appears when you correlate what was output across all sessions for that agent. Temporal attack patterns only appear in the aggregate timeline.

**Information flow provenance**
Track where data originated, how it was transformed, and where it went. If data that entered as a database record exits as image pixel values — even across multiple intermediate steps — the flow is flagged.

**Output entropy analysis**
Unexpected entropy in outputs (images with suspiciously high LSB entropy, markdown with unusual whitespace distribution) is a steganography signal. No content scanner catches this — it requires structural analysis of the output artifact.

**Cross-agent correlation**
When two agents both touch the same files or event bus entries within a short time window, flag for behavioral correlation. Independent agents that appear to coordinate are a red flag even if neither is individually anomalous.

### Architecture Position

SIEM for agents sits at a different layer than sentinels:

```
[UPSTREAM SENTINEL]     <- per-call, per-input inspection
LLM Call
[DOWNSTREAM SENTINEL]   <- per-call, per-output inspection

            +

[AGENT SIEM]            <- cross-call, cross-session, cross-agent
    |-- session event ingestion (every tool call, read, write, hook)
    |-- behavioral baseline per plugin
    |-- intent drift detection
    |-- cross-session timeline correlation
    |-- cross-agent behavioral graph
    |-- information flow provenance tracking
    |-- output entropy / steganography detection
    |-- alert + forensic replay on anomaly
```

Sentinels are the perimeter guard checking IDs at the door.
SIEM is the behavioral analyst watching what happens inside the building, across weeks, looking for patterns no single guard would notice.

Both are required. Neither alone is sufficient.

### The Honest Calibration Problem

There is a foundational question the security product industry has not answered honestly:

**Frontier labs — Anthropic, OpenAI, Google DeepMind — spend billions of dollars on safety research, employ the best alignment researchers in the world, have full access to their own model weights, and still cannot reliably stop jailbreaking.**

If the labs themselves cannot fully secure the cognitive layer of their own models, how strong can a third-party scanning product actually be?

LlamaGuard, Cloudflare Firewall for AI, Datadog AI Guard — these are classifiers and pattern matchers running on top of the same models that can be jailbroken. They add defense-in-depth. They raise the cost of attack. But they do not solve the underlying problem and any honest evaluation of their capabilities has to start there.

This is not a reason to abandon the security layer. It is a reason to be clear-eyed about what each layer can and cannot do:

| Layer | What it realistically stops | What it cannot stop |
|---|---|---|
| Input scanner | Known injection patterns, obvious payloads | Novel encodings, semantic laundering, metadata vectors |
| Output scanner | PII regex matches, known exfil patterns | Steganographic exfiltration, fragmented data, timing channels |
| Content policy | Explicit policy violations | Shadow features framed as legitimate functionality |
| RLHF / alignment | Direct jailbreak attempts with obvious adversarial framing | Adversarial objectivity — malicious intent framed as benign config |
| Static code analysis | Malicious code constructs in source files | 84.2% of vulnerabilities — those living in natural language |
| Agent SIEM | Behavioral drift, cross-session patterns, intent mismatch | Zero-day attack patterns with no behavioral baseline |

The honest conclusion: **no single layer provides reliable protection**. The goal is defense in depth — making attacks expensive, detectable, and forensically traceable — not elimination.

What the field needs but does not have is three-dimensional coverage:

```
INSIDE THE AGENT
    |-- what enters the cognitive layer (inputs, tool results, memory retrievals)
    |-- what happens inside the session (tool call graph, behavioral drift)
    |-- what leaves (outputs, file writes, API calls, event bus entries)

ACROSS SESSIONS
    |-- temporal patterns invisible per-session
    |-- cross-agent coordination signals
    |-- information flow provenance end-to-end

CALIBRATED AGAINST KNOWN LIMITS
    |-- explicit acknowledgment that the cognitive layer itself cannot be fully secured
    |-- defense-in-depth not false confidence
    |-- forensic capability when prevention fails
```

The industry needs to stop selling these products as "AI firewalls" that make agentic systems safe. They are monitoring layers that raise attack cost and improve forensic capability. That framing matters — because enterprises deploying agentic systems at scale need to make risk decisions based on honest capability assessment, not marketing.

### Why Nobody Has Built This Yet

The benchmark obsession has a structural cause: capability gains are quantifiable (MMLU up 2 points = paper), publishable, and attract investment. Security gaps are fuzzy, require surfacing vulnerabilities that labs don't want to advertise, and create liability. The incentive structure systematically underinvests in agentic security.

The empirical data says 157 malicious skills out of 98,380 analyzed — with an ecosystem at 400,000+ skills and growing exponentially. The browser extension marketplace made the same mistake. It took years of widespread credential theft and ransomware before the ecosystem took extension security seriously. Agent ecosystems are on the same trajectory.

Agent SIEM is the infrastructure that doesn't exist yet but will become critical as the ecosystem scales. The question is whether the industry builds it proactively or waits for the incident that forces it.

---

## Near-Term Priorities

### Adapter Layer
1. Define the memory adapter interface — wire `memory-management` plugin as swappable default
2. Define the event bus adapter interface — JSON files default, Redis next tier
3. Document the adapter contract so third-party plugins can implement it
4. Update `agentic-os-init` to accept adapter config at init time

### Security
5. Define explicit scope declarations in SKILL.md and plugin.json schema
6. Implement hook scope enforcement — block violations, log all hook invocations
7. Prototype ephemeral session token issuance tied to approved action scope
8. Add input metadata sanitization as a pre-ingestion hook (Layer 1 proxy)
9. Build behavioral baseline logging into `events.jsonl` — foundation for future SIEM

### OS Paradigm
10. Cross-project learning prototype — export improvement signals from `os-learning-loop` to a shared ledger
11. Distributed lock management — Redis-backed spinlock as optional kernel primitive
12. Event sourcing spike — derive `os-state.json` as a projection of `events.jsonl` instead of mutable file

---

## Related Files

- `references/architecture.md` — current architecture
- `references/backlog.md` — implementation backlog items
- `references/memory-hygiene.md` — memory management patterns
- `references/dual-loop.md` — loop architecture
- `assets/diagrams/event-bus-architecture.mmd` — current event bus diagram
- `assets/diagrams/agentic-os-memory-subsystem.mmd` — current memory diagram

### Research

- `references/research/koubaa-2025-agent-os-blueprint.md` — summary of Koubaa (TechRxiv, Sept 2025): five-layer Agent-OS architecture, Agent Contracts, HRT/SRT/DT latency classes
- `references/research/sharma-2026-aos-control-plane.md` — summary of Sharma (Authorea, Feb 2026): Separation of Planes, Four Architectural Invariants, Linux/Windows AOS mapping
