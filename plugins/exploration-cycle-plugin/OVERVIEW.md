# The GenAI Double Diamond: Vision-to-Execution Framework

The **GenAI Double Diamond** is the foundational framework for this plugin. It bridges the "Maturity Gap" between a raw idea (The Vibe) and a hardened engineering contract (The Spec).

---

## 🖼️ Framework Overview

```mermaid
flowchart TB
    Start([Idea, need, problem, objective]) --> Phase0

    %% --- PROCESS 1: THE EXPLORATION LOOP (Scouting Party) ---
    subgraph Diamond1 [Diamond 1:<BR> <B>exploration-cycle-plugin</B><BR>Exploration Loop]
        direction TB
        Phase0[intake-agent<BR>Skill: exploration-session-brief] --> Phase1[Requirements Capture<BR>Script: dispatch.py CLI passes]
        
        %% Documentation Sub-agents
        subgraph Documentation [The Scribes]
            Pass1[Agent: requirements-doc-agent<BR>Mode: problem-framing]
            Pass2[Agent: requirements-doc-agent<BR>Mode: business-requirements]
            Pass3[Skill: user-story-capture]
        end

        %% UI & Vision Prototyping
        subgraph Design [The Jam Session]
            Phase2[Skill: prototype-builder]
            Phase2 --> Companion[Agent: prototype-companion<BR>Capture Implied Req]
        end

        Phase1 --> Pass1
        Pass1 --> Pass2
        Pass2 --> Pass3
        Phase1 --> Phase2
        
        Companion --> Audit[Agent: business-rule-audit-agent<BR>Logic Drift Check]
    end

    %% --- THE TRANSITION: RISK & RIGOR GATE ---
    subgraph Transition [Handoff & Risk Gate]
        direction TB
        Audit --> NarrowGate{Narrowing Gate<BR>Script: check_gaps.py}
        NarrowGate -->|Not Ready| Phase1
        NarrowGate -->|Ready| TierGate{Skill: exploration-handoff<BR>Rigor Tier Assessment}
    end

    %% --- PROCESS 2: THE ENGINEERING CYCLE (The Factory / Black Box) ---
    subgraph Diamond2 [Diamond 2: Engineering Cycle]
        direction TB
        TierGate -->|High Rigor| BlackBox[Engineering 'Black Box'<BR>spec-kitty / spec-kit]
        TierGate -->|Low Rigor| Agile[Agile / Lightweight<BR>Dev Cycle]
        
        BlackBox --> Solidify[Solidification:<BR>Specs & Work Packages]
        Solidify --> Implementation[Production-Grade Build]
    end

    %% --- BIDIRECTIONAL RE-ENTRY ---
    Implementation -.->|Unknown Unknown Found| ReEntry[Agent: planning-doc-agent<BR>Mode: re-entry-scope]
    ReEntry -.->|New Session Brief| Phase0

    %% Final Output
    Implementation --> Done([Fast by Default, Safe by Design])

    %% Styles
    style Start fill:#f3f4f6,stroke:#374151
    style Diamond1 fill:#e0f2fe,stroke:#0369a1,stroke-width:2px
    style Transition fill:#fff7ed,stroke:#c2410c,stroke-width:2px
    style Diamond2 fill:#f0fdf4,stroke:#15803d,stroke-width:2px
    style Done fill:#fef3c7,stroke:#d97706,stroke-width:3px
    style ReEntry fill:#fee2e2,stroke:#b91c1c,stroke-dasharray: 5 5
```

---

## 1. The First Diamond: Exploration (Discovery)
**Goal:** Pure vision translation and "Vibe" capture.
**Role:** The "Scouting Party."
- **Cheap Exploration:** We use a `dispatch.py` wrapper to call focused, low-cost sub-agents (like `requirements-doc-agent`) for framing and user stories.
- **Prototype-Led Discovery:** Instead of weeks of meetings, we build functional prototypes in minutes to discover the requirements through the code.
- **Eliminating the Bottleneck:** We remove the high-cost BA/UX multi-week gap, allowing visionaries to see their ideas instantly.

## 2. The Transition: Handoff & Risk Analysis
**Goal:** Collapsing the "Vibe" into a "Spec."
**Logic:** A mandatory filter before any high-rigor engineering begins.
- **Rigor Tiers:** We categorize projects based on the **AI Security & Safety Lab's** assessment:
    - **Tier 1 (Low):** Internal R&D. Agile/Lightweight cycle.
    - **Tier 2 (Moderate):** Internal data + standard tools. Red-Teaming mandatory.
    - **Tier 3 (High):** PII/Sensitive data + High-privilege access. Full architectural audit and hardening required.
- **Gatekeeping:** Ensures Tier 3 projects are forced into the full `spec-kitty` engineering lifecycle.

## 3. The Second Diamond: Execution (Solidification)
**Goal:** Structural builds and enterprise-grade validation.
**Role:** The "Static Map."
- **Solidification:** We use the `spec-kitty-plugin` to convert the exploration's output into formal specifications and verified work packages.
- **Logic Drift Audit:** Our `business-rule-audit-agent` cross-references prototype behavior against captured BRDs to ensure the "Fast" build remains "Safe."

---

## 🔄 Bidirectional Re-Entry
Engineering is non-linear. When an "unknown unknown" surfaces during Diamond 2, we formally trigger a **Re-Entry** to Diamond 1 to resolve the vision gap before continuing.

---

## 📂 Key Architectural Diagrams
- [GenAI Double Diamond (Evolved)](assets/diagrams/genai-double-diamond-evolved.mmd)
- [Dual-Loop Architecture](assets/diagrams/dual_loop_architecture.mmd)
- [Exploration Workflow](assets/diagrams/exploration-cycle-workflow.mmd)

## 📚 Technical References
- [Core Architecture](references/architecture.md)
- [Dual-Loop Architecture Pattern](references/dual-loop-architecture.md)
- [Learning-Loop Architecture Pattern](references/learning-loop-architecture.md)
- [Post-Run Survey Workflow](references/post-run-survey.md)

---

*This framework ensures we are **Fast by Default, but Safe by Design.***
