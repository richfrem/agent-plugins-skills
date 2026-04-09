# Opportunity 3: Exploration & Design

**Value Proposition:** Transformational impact. Fast by Default, Safe by Design.

![The GenAI Double Diamond](../infographics/Opportunities-3-4-Prototyping-and-Engineering.png)

> **Part of the Double Diamond:** This is the *Exploration & Design* phase. It links directly with **[Opportunity 4: Engineering Cycle Execution](../04-Engineering-Cycle-Execution/)** for formal execution.

---

## The Concept: Democratizing Design

Opportunity 3 puts exploration and design directly into the hands of Business Area Experts (BAEs) and Subject Matter Experts (SMEs).

Do not force your SMEs to wait on engineering, UX teams, or external contractors. Instead, deploy AI tools that let the business independently explore, document, and prototype the solution they actually need. We use the **GenAI Double Diamond** framework to bridge the gap between a raw idea and a structured, validated output — whether that output is a software specification, a documented business process, an automation workflow, or a strategic plan.

GenAI is a force multiplier for non-engineers. It automates the heavily manual work: documentation generation, requirements gathering, functional prototyping, workflow mapping, UI/UX design, and core business analysis. This drastically lowers costs and accelerates execution. Teams solve more problems, faster and cheaper.

### The Right Place for "Vibe Coding"
While the industry correctly identified that unstructured "vibe coding" is a massive liability for formal software execution (a problem that Opportunity 4 actively solves), the backlash has gone too far. People fail to see that **vibe coding has a proper, highly valuable place in the enterprise, provided it has the right guardrails.**

Guarded vibe coding is the ultimate mechanism to safely democratize AI. It gives non-engineers a safe sandbox to explore messy ideas, generate functional prototypes, document business rules, and access what is essentially a "Business Analyst and UI/UX Developer in a box." 

This unstructured exploration makes things economical that were completely uneconomical before (e.g., throwing an entire dev team at a minor operational problem). In short: GenAI agents are force multipliers for engineers. The Exploration Loop is a force multiplier for *non-engineers*.

**The boundary:** AI-generated prototypes are perfect for articulating design and intent. They are not production-ready enterprise systems. The output of Opportunity 3 is structured, validated intent. Complex, secure systems require formal engineering and a strict SDLC footprint. That is what Opportunity 4 delivers.

---

## The Exploration Loop

> **Architectural Attribution:** The Conversational Dashboard pattern, sub-agent spawning logistics, and rigid `<HARD-GATE>` mechanisms utilized in this toolkit were inspired by and adapted from the execution mechanics of the [`obra/superpowers`](https://github.com/obra/superpowers) continuous development framework (MIT License). We have adapted their technical execution paradigm to serve non-technical Subject Matter Experts.

Opportunity 3 is not a linear process — it is an iterative discovery loop managed by the **Conversational Dashboard Pattern**. The orchestrator (`exploration-workflow`) maintains state via an `exploration-dashboard.md` artifact, enforcing strict phase gates. The BAE and AI cycle through design and refinement until the output converges on something that accurately represents the future state.

### Phase 1: Problem Framing
The loop begins with the `discovery-planning` skill, which establishes the ground truth context before any design work begins. This intake is flexible by design — it accepts any starting point (a raw idea, a process problem, or an Opportunity 2 handoff). The agent acts as a Business Analyst, asking one question at a time to clarify the problem statement, stakeholders, success criteria, must-haves, and constraints.

**The `<HARD-GATE>` Protocol:** This is a strict architectural constraint. The orchestrator is explicitly prohibited from moving to the execution or domain-capture phases until the SME explicitly approves the written Discovery Plan. The `<HARD-GATE>` ensures downstream agents don't hallucinate features that were never requested.

### Phase 2: Visual Blueprinting
Before any functional prototyping begins, the `visual-companion` skill presents layout options adapted to the Discovery Plan. The SME makes a selection to ensure the structural direction is correct before the build loop starts.

### Phase 3: Prototyping
Instead of a single agent struggling with complex context, prototype generation is democratized via `subagent-driven-prototyping`. 
1. **Context Isolation:** The prototype is broken down into components. A fresh, blank-slate subagent is dispatched for each component with exactly the context it needs.
2. **Two-Stage Review:** Before the SME sees it, the component undergoes a *Spec Compliance Check* (did it match the approved intent?) and a *Code Quality Check* (does it syntactically work?).
3. **Interactive Validation:** The swarm produces a **runnable, interactive software prototype**. This is critical—wireframes are insufficient. The SME must be able to click through the business flows to validate edge cases.

### Phase 4: Handoff & Specs
Once the prototype is validated by the SME, the `exploration-handoff` skill coordinates a documentation sweep. It absorbs the previous manual "Scribe Phase" activities directly into the handoff sequence, producing formal artifacts:
- **Workflow Documentation** (`business-workflow-doc`) — mapping the future-state process flows interactively
- **User Requirements Documentation** (`user-story-capture`) — capturing functional constraints and Agile user stories
- **Spec Generation** — converting agreed intent into structured specification artifacts

### Quality Validation Checks (The TDD of Specs)
Before the exploration phase can conclude, the system performs a **Placeholder Scan**. The agent automatically scans its own emerging spec documents for ambiguity, "TODOs", or contradictory rules. Any vagueness that would crash the Opp 4 execution phase is caught and resolved here.

---

## The Handoff & Risk Gate

Before any output from Opportunity 3 moves to Opportunity 4, it passes through a mandatory **Handoff & Risk Gate**. This is the guardrail between fast exploration and formal engineering. It has three components:

### 1. Harm & Risk Assessment
Evaluates the proposed design for potential harms — security risks, data privacy implications, regulatory compliance exposure, and operational risks of the proposed system. Not a rubber stamp. If harm vectors are identified, the design goes back into the loop.

### 2. Feasibility Filter
Assesses whether the proposed design is technically and operationally feasible to build within the constraints of the target environment. Filters out designs that are sound conceptually but undeliverable in practice.

### 3. TierGate (Tier Assessment)
Determines the complexity tier of the proposed output to explicitly authorize safe projects, rather than just blocking them. This dictates the right-sized level of engineering rigor required:
*   **Tier 1 (Low Risk):** Internal, low-risk utilities or tools. No formal engineering required; the BAE deploys via a lightweight self-assessment.
*   **Tier 2 (Moderate Risk):** Internal tools requiring data access or broader user exposure. Requires a security team review and mandatory Red Teaming before deployment.
*   **Tier 3 (High Risk):** Complex enterprise transactions or public-facing systems requiring strict SDLC rigor, manual security testing, and formal governance via Opportunity 4.

### The Four Outcomes of Exploration
Because the Exploration Loop is democratized and open to any business problem, the Handoff Gate ultimately yields one of four financial and operational outcomes:

*   **The Throwaway Prototype (Fail Fast & Cheap):** The prototype reveals the original idea was flawed. Instead of spending months on procurement and massive Agile sprints to discover a failure, the idea is safely killed at near-zero cost.
*   **Tier 1 (Direct Deployment):** The output is authorized as low-risk. The business implements and captures untapped capacity instantly without waiting on formal engineering.
*   **Tier 2 (Security Review & Red Team):** The output requires internal data access or broader exposure, but is not a complex transactional system. It enters a security review and mandatory Red Team assessment before deployment.
*   **Tier 3 (SDLC Handoff):** The output passes all gates but is high-risk or high-complexity. The BAE's validated spec package is formally handed off to Opportunity 4 for deterministic engineering execution.

---

## The Toolkit

The **Exploration-Cycle Plugin** orchestrates this process with a suite of conversational and structural skills managed via a central dashboard pattern:

- **`exploration-workflow`** — The canonical state machine and orchestrator. It manages the `exploration-dashboard.md`, routes work to child skills, and enforces Phase Gates.
- **`exploration-optimizer`** — evaluates and improves the exploration-cycle skills, prompts, routing, and artifact quality
- **`discovery-planning`** — runs Phase 1 (Problem Framing) and enforces the first `<HARD-GATE>`
- **`visual-companion`** — governs Phase 2 (Visual Blueprinting), validating layout direction
- **`subagent-driven-prototyping`** — governs Phase 3 (Prototyping), managing the decentralized subagent swarm that builds the functional prototype
- **`exploration-session-brief`** — captures core context and problem framing 
- **`business-workflow-doc`** — tracks and maps proposed workflows interactively
- **`business-requirements-capture`** — extracts functional constraints and business rules as the design evolves
- **`user-story-capture`** — breaks agreed behaviours into structured user stories
- **`exploration-handoff`** — governs Phase 4 (Handoff & Specs), formatting the SME's output into the exact Layer 1 Spec-Kit artifacts (Spec-Kitty, OpenSpec, superpowers) required by Opportunity 4
- **`deferred`** — parks capabilities dynamically when exploration is incomplete

---

## The Outcome

These autonomous artifacts act as a mandatory filter before any high-rigor engineering begins. Stakeholders get a tangible, interactive vision of the future state. The Handoff & Risk Gate ensures only feasible, safe designs proceed.

Once the gate passes, the formal spec package moves to **[Opportunity 4: Engineering Cycle Execution](../04-Engineering-Cycle-Execution/)** for deterministic engineering execution.
