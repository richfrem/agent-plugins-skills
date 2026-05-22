# The GenAI Double Diamond: Vision-to-Execution Framework

The **GenAI Double Diamond** is the foundational framework for this plugin. It bridges the "Maturity Gap" between a raw idea (The Vibe) and a hardened engineering contract (The Spec).

---

## 🖼️ Framework Overview
The framework supports two distinct operational entry points inside the First Diamond, depending on your starting context:
1. **Path 1: Pre-Build Discovery (Greenfield/Brownfield)**: When starting with *no code*, guiding the SME from pure intent through structured framing, layout blueprinting, and clean component building. See the **[GenAI Double Diamond Flowchart](assets/diagrams/genai-double-diamond.mmd)**.
2. **Path 2: Vibe-to-Enterprise Rescue (Existing Prototypes)**: When starting with an *existing, vibe-coded prototype* (usually containing technical debt or raw code). It runs an automated visual & functional audit, salvages high-value business logic gems, and transitions them into clean enterprise architecture blueprints. See the **[Vibe-to-Enterprise Rescue Diagram](assets/diagrams/vibe-rescue-workflow.mmd)**.

---

## 1. The First Diamond: Exploration (Discovery)
**Goal:** Pure vision translation and "Vibe" capture, adapted to the starting point.
**Role:** The "Scouting Party."

### Path 1: Pre-Build Discovery
- **Cheap Exploration:** We use a `dispatch.py` wrapper to call focused, low-cost sub-agents (like `requirements-doc-agent`) for framing and user stories.
- **Prototype-Led Discovery:** Instead of weeks of meetings, we build functional prototypes in minutes to discover requirements through the code.
- **Eliminating the Bottleneck:** We remove the high-cost BA/UX multi-week gap, allowing visionaries to see their ideas instantly.

### Path 2: Vibe-to-Enterprise Rescue
- **Empathetic Salvaging:** Instead of discarding rapid prototypes, we audit the running system via `vibe-browser-audit` to extract DOM elements, views, and core business equations (the "Preservation Gems").
- **Technical Debt Quarantine:** We isolate insecure, brittle, or monolithic segments of the prototype code as targets for replacement.
- **Architectural Scaffolding:** The `vibe-togaf-architect` translates the findings and interactive BAE input into formal C4 Context maps and Mermaid sequence diagrams.

---

## 2. The Transition: Handoff & Risk Analysis
**Goal:** Collapsing the "Vibe" into a "Spec."
**Logic:** A mandatory filter before any high-rigor engineering begins.
- **Rigor Tiers:** We categorize projects based on the **AI Security & Safety Lab's** assessment:
    - **Tier 1 (Low):** Internal R&D. Agile/Lightweight cycle.
    - **Tier 2 (Moderate):** Internal data + standard tools. Red-Teaming mandatory.
    - **Tier 3 (High):** PII/Sensitive data + High-privilege access. Full architectural audit and hardening required.
- **Gatekeeping:** Ensures Tier 3 projects are handed off to a formalized engineering harness (e.g., spec-kits, superpowers) for lifecycle management.
- **Path 2 Spec Packaging:** For rescue tracks, the `vibe-spec-packager` compiles the specs into a production-grade spec-kit and bootstraps a clean target directory sandbox (purging quarantined debt while cleanly housing salvaged gems).

## 3. The Second Diamond: Execution (Solidification)
**Goal:** Structural builds and enterprise-grade validation.
**Role:** The "Static Map."
- **Solidification:** We use a specification layer and execution harness to convert the exploration's output into formal specifications and verified work packages.
- **Logic Drift Audit:** Our `business-rule-audit-agent` cross-references prototype behavior against captured BRDs to ensure the "Fast" build remains "Safe."

---

## 🔄 Bidirectional Re-Entry
Engineering is non-linear. When an "unknown unknown" surfaces during Diamond 2, we formally trigger a **Re-Entry** to Diamond 1 to resolve the vision gap before continuing.

---

## 📂 Key Architectural Diagrams
- [GenAI Double Diamond](assets/diagrams/genai-double-diamond.mmd)
- [Vibe-to-Enterprise Rescue Workflow](assets/diagrams/vibe-rescue-workflow.mmd)
- [Exploration Workflow](assets/diagrams/exploration-cycle-workflow.mmd)

## 📚 Technical References
- [Core Architecture](references/architecture/architecture.md)
- [Post-Run Survey Workflow](references/post-run-survey.md)

---

*This framework ensures we are **Fast by Default, but Safe by Design.***

