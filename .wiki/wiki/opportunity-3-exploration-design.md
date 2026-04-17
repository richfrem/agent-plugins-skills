---
concept: opportunity-3-exploration-design
source: plugin-code
source_file: exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.569396+00:00
cluster: plugin-code
content_hash: e81032f76872d978
---

# Opportunity 3: Exploration & Design

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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

**The `<HARD-GATE>` Protocol:** This is a strict architec

*(content truncated)*

## See Also

- [[exploration-cycle-plugin-design-recommendation]]
- [[design-thinking-artifacts-exploration-context]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[optimizer-engine-patterns-reference-design]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[optimizer-engine-patterns-reference-design]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/README.md`
- **Indexed:** 2026-04-17T06:42:09.569396+00:00
