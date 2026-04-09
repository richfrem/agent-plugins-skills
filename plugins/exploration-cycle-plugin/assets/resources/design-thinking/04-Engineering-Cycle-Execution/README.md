# Opportunity 4: Engineering CycleExecution

**Value Proposition:** Scalable, Deterministic Code Generation. Done: Fast by Default, Safe by Design.

![The GenAI Double Diamond](../infographics/Opportunities-3-4-Prototyping-and-Engineering.png)

> **Part of the Double Diamond:** This is the *Engineering Cycle & Execution* phase. It relies entirely on the validated spec package from **[Opportunity 3: Exploration & Design](../03-Exploration-and-Design/)** to function.

---

## The Concept: Execution from Ground Truth

Opportunity 4 is where intent becomes production code. Because Opportunities 1 through 3 produce 100% human-verified, immutable specifications, Opportunity 4 simply executes against them. There is no ambiguity for the engineering agent to resolve — the business rules are locked, the design is validated, the spec is the ground truth.

Agentic code generation is only as good as the specifications it receives. This is why the pipeline is sequenced the way it is. Weak or ambiguous specs produce hallucination and logic drift. Immutable, human-validated specs produce deterministic, accurate code.

---

> **Full tooling details, GitHub links, and selection guidance:** [Tooling Reference →](tooling-reference.md)

## The Three-Layer Stack

Opportunity 4 is implemented as a deliberate **three-layer architecture** — each layer has a distinct responsibility, and they are not interchangeable.

### Layer 1 — Spec-Kits (Specification Driven Design)
The spec layer defines *what gets built* and enforces the structure and constraints the engineering agent must follow. These are the frameworks that translate validated human intent into machine-consumable specifications:

- **spec-kit** — lightweight specification structure for smaller scopes
- **spec-kitty** — proven reference implementation with strict workflow enforcement, live `implementation_plan.md`, and `.clinerules` for agent boundary enforcement
- **OpenSpec** — open specification standard for interoperability across tooling
- **BMAD-Method** — structured agentic methodology for breaking complex features into bounded, sequenced work units

The spec layer is the contract. Engineering agents are not permitted to deviate from it.

### Layer 2 — Agentic Frameworks (Cognitive & Orchestration)
The orchestration layer determines *how the engineering agent thinks and coordinates*. These are the SDK-level frameworks that give the agent its reasoning and tool-use capabilities:

- **Claude Code Agent SDK** — Anthropic's agentic SDK; the primary orchestration layer for Claude-based engineering agents
- **Microsoft Agentic SDK** — Microsoft's agentic framework; enables deployment in Azure-hosted or GitHub Copilot-integrated engineering environments

The choice of framework is driven by the target deployment environment, not by preference. Both operate against the same spec layer above.

### Layer 3 — Agentic Harnesses (Execution & Safety Wrappers)
The harness layer controls *how code is safely generated, tested, and delivered*. These wrappers exist specifically to prevent unverified or broken code from reaching the main repository:

- **obra/superpowers** — execution harness providing enhanced agentic tooling and capability boundaries
- **gsd-build / get-shit-done** — pragmatic build harness for rapid, constrained execution within defined spec boundaries
- **Execution Sandbox** — isolated containerised environment (Podman + Postgres or equivalent) where generated code is deployed, tested against integration tests derived from Phase 2/3 specs, and verified before any delivery to the main repository

**Blast radius control:** Code never exits the sandbox until it explicitly passes spec verification. This is not optional.

---

## The Execution Flow

1. **Ingestion** — the framework consumes the formal spec package exported from Opportunity 3's Handoff & Risk Gate. Business rules, user stories, workflow specs, and the implementation plan are all loaded as ground truth.
2. **Implementation Planning (The 2-5 Minute Rule)** — the agent translates functional business rules and user stories into a sequenced implementation plan. The framework enforces extreme granularity: every task must be broken down into atomic, 2-5 minute micro-tasks. Spec-Kitty maintains a live `implementation_plan.md` that tracks progress and enforces boundaries.
3. **Deterministic Generation (Context Isolation)** — the orchestration framework extracts individual micro-tasks and dispatches them to *blank-slate subagents*. By isolating tasks, subagents only see the immediate objective without conversation pollution or exploration context. The spec layer acts as a hard constraint boundary.
4. **Sandbox Verification (The Two-Stage Review)** — generated code is deployed into the Execution Sandbox. It must first pass a **Spec Compliance Check** (did the subagent build exactly what was asked without scope creep?), followed by a **Code Quality Check** (integration tests derived from Phase 2/3 specs). Failures route back for correction.
5. **Delivery** — code that passes the complete two-stage verification loop is delivered to the main repository. Done.

---

## ReEntry: When Unknowns Surface

Engineering execution sometimes reveals gaps or contradictions that weren't visible at the spec level. A business rule that seemed clear turns out to be ambiguous when implemented. A workflow step has an edge case nobody described.

When unknowns are found during Opportunity 4 execution, the specific work package is **paused** and a **ReEntry** is triggered:

- The affected spec is flagged and routed back to Opportunity 2 (if it's a business rule or validation question) or Opportunity 3 (if it's a design question)
- The BAE or SME resolves the ambiguity through the standard HITL validation process
- Once the spec is updated and re-validated, the Gatekeeper updates the ledger, and engineering resumes with the corrected context

ReEntry is not a failure — it is the pipeline working as designed. The human remains the source of truth at every stage.

---

## The Outcome

A production-ready, formally engineered system built from validated human intent — with full traceability from every line of code back to the business rule or user story that required it.
