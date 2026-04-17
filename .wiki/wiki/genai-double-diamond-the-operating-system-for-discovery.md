---
concept: genai-double-diamond-the-operating-system-for-discovery
source: plugin-code
source_file: exploration-cycle-plugin/README.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.562339+00:00
cluster: superpowers
content_hash: 7ad1a630542f29f3
---

# GenAI Double Diamond: The Operating System for Discovery

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# GenAI Double Diamond: The Operating System for Discovery

The **exploration-cycle-plugin** is a technical implementation of the **GenAI Double Diamond** framework — a structured but adaptive system that puts AI-powered exploration directly into the hands of Subject Matter Experts (SMEs) and Business Area Experts (BAEs).

It bridges the maturity gap between raw intent (*The Vibe*) and a hardened engineering contract (*The Spec*), while recognizing that **not every problem needs software, and not every solution needs formal engineering.**

![The GenAI Double Diamond — Opportunities 3 & 4](assets/resources/design-thinking/infographics/Opportunities-3-4-Prototyping-and-Engineering.png)

**Opportunity 3** (this plugin) is the Discovery Loop: explore, define, prototype, validate.
**Opportunity 4** is the Engineering Factory: spec-driven development, security hardening, production deployment. The **Handoff & Risk Gate** between them determines whether Opportunity 4 is even needed.

See also: [GenAI Double Diamond Flowchart](assets/diagrams/genai-double-diamond.mmd) | [Hybrid Workflow Diagram](assets/diagrams/hybrid-workflow.mmd)

---

## The Belief: Democratizing AI

This plugin exists because of a simple belief: **the people closest to the problem should be the ones exploring the solution.**

Today, when a business expert has an idea — a process improvement, a new internal tool, a workflow fix — they enter a queue. They wait for a Business Analyst to translate their vision. Then a UX designer interprets it. Then a developer builds what they understood. Each handoff introduces translation errors, delays, and cost. A $5,000 problem gets a $200,000 solution that doesn't quite solve it.

The exploration-cycle-plugin changes the equation:

- **Any SME** can run a structured discovery session with AI guidance — no technical background required
- **A fleet of cheap AI sub-agents** handles the work that used to require a full BA/UX/dev team: requirements gathering, process documentation, prototyping, user story capture, workflow mapping
- **The SME stays in control** — the AI asks questions, the human makes decisions. Every phase has a hard gate requiring explicit SME approval before proceeding
- **The output is whatever the problem actually needs** — a software prototype, a process map, a policy recommendation, a requirements document, or a "don't build this" conclusion. All are valid, high-value outcomes

The cost of exploration drops from tens of thousands of dollars and weeks of calendar time to a single afternoon conversation. Ideas that would never have been worth a formal project can now be explored, validated, and either shipped or killed — cheaply and safely.

---

## Core Principles

### 1. Right Problem First (The Inner Double Diamond)

The most expensive mistake in software development is building the right thing for the wrong problem. The UK's Blue Badge digitization project nearly built a sophisticated document verification portal — until service designers discovered the real problem was confusing policy language. A rewrite of the questions saved millions.

Phase 1 of the exploration loop contains its own double diamond:

```
Phase 1: Discovery Planning
├── DIVERGE: What's the problem? Who's affected? What does good look like?
├── CONVERGE: Intervention Check — is this a technology problem, a process
│   problem, a policy problem, or a communication problem?
├── DIVERGE: What must the solution deliver? What are the constraints?
└── CONVERGE: Discovery Plan — approved by SME before anything else happens
```

The **Intervention Check** (Q4) is the moment where the Scouting Party earns its keep. It explicitly asks: *"Is building something the right intervention here, or could this be solved by changing a rule, simplifying a process, or removing a step entirely?"*

If the answer is "don't build" — that's a success, not a failure. You discovered it in 20 minutes instead of 6 months.

### 2. Output-Agnostic

Not every exploration 

*(content truncated)*

## See Also

- [[the-genai-double-diamond-vision-to-execution-framework]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[the-exploration-cycle-plugin-democratizing-discovery]]
- [[recursive-logic-discovery-the-infinite-context-ecosystem]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/README.md`
- **Indexed:** 2026-04-17T06:42:09.562339+00:00
