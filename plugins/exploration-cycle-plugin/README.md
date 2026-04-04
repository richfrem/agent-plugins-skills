# GenAI Double Diamond: The Operating System for Discovery

The **exploration-cycle-plugin** is a technical implementation of the **GenAI Double Diamond** framework. It provides a non-linear "Scouting Party" for the fuzzy front end of development, bridging the maturity gap between raw intent (The Vibe) and a hardened engineering contract (The Spec).

---

## 🖼️ Framework Overview
See the **[GenAI Double Diamond Flowchart](references/genai-double-diamond.mmd)** for a visual representation of the Scouting Party (Diamond 1) and Engineering Factory (Diamond 2) cycle.

---

## 🧭 Core Philosophy: The Scouting Party

Standard specification kits (like GitHub's `spec-kit`) serve as a "Static Map" for engineering. They are world-class at recording the destination, but they often suffer from **Blank Page Syndrome**—they require structured input to function.

The **exploration-cycle-plugin** solves this by acting as the **Scouting Party**. It is designed for Diamond 1 (Discovery):
- **Vision Translation**: Pulls ambiguous intent out of a visionary's head and converts it into structured captures before a spec even exists.
- **Cheap Exploration**: Uses the `dispatch.py` wrapper to call focused, cheap-model sub-agents for framing, BRDs, and user stories. This eliminates the multi-week BA/UX bottleneck.
- **Non-Linear Iteration**: Allows for "breaking things," hallucinating UIs, and testing "What if?" scenarios without premature architectural solidification.

---

## 🛡️ Safety & Governance: The Rigor Gate

Accountability and traceability are not optional in public sector or enterprise GenAI. This plugin mandates a **Risk & Rigor Assessment** during the handoff phase to determine the appropriate delivery path:

| Rigor Tier | Risk Profile | Execution Path (Diamond 2) |
| :--- | :--- | :--- |
| **Tier 1 (Low)** | Internal R&D, limited/no PII. | Lightweight Agile dev cycle. |
| **Tier 2 (Moderate)** | Internal data, standard tools. | Requires Security review & mandatory Red Teaming. |
| **Tier 3 (High)** | PII/Sensitive data, high-privilege tools (Bash). | **Mandatory** full `spec-kitty` cycle with architectural hardening. |

This gate ensures that we remain **Fast by Default, but Safe by Design.**

---

## 🔄 Bidirectional Re-Entry: Navigating the Unknown

Engineering is rarely linear. A core design feature of this plugin is the **Bidirectional Re-Entry loop**. 

When Diamond 2 (Execution) uncovers an "unknown unknown"—unresolved ambiguity in the spec, a missed edge case in the data model, or a shift in vision—the `planning-doc-agent` triggers a re-entry cycle back to Diamond 1. This allows the team to resolve the vision gap in a low-cost discovery mode without losing momentum in the production factory.

---

## 🏗️ Technical Architecture

### CLI Invocation Pattern (Cheap Sub-Agents)
To maintain the "Cheap Exploration" economic advantage, all documentation sub-agents are invoked via a dedicated `dispatch.py` wrapper. This avoids context truncation and ensures precise subprocess execution.

```bash
python3 ./skills/exploration-workflow/scripts/dispatch.py \
  --agent ./agents/requirements-doc-agent.md \
  --context exploration/session-brief.md exploration/captures/problem-framing.md \
  --instruction "Mode: business-requirements. Extract functional requirements." \
  --output exploration/captures/brd-draft.md
```

### Directory Structure
```text
exploration-cycle-plugin/
├── OVERVIEW.md             # GenAI Double Diamond framework overview
├── README.md                 # Entry point and philosophy
├── agents/                   # Vision Translators and Scribes
├── assets/diagrams/          # Technical and philosophical flowcharts
├── references/               # Architectural patterns (Dual-Loop, Learning-Loop)
├── skills/                   # Technical capabilities
│   ├── business-requirements-capture/
│   ├── business-workflow-doc/
│   ├── exploration-handoff/
│   ├── exploration-optimizer/
│   ├── exploration-session-brief/
│   ├── exploration-workflow/
│   ├── user-story-capture/
│   └── deferred/             # Planned future capabilities
│       ├── exploration-orchestrator/
│       └── prototype-builder/
└── requirements.in           # Python dependencies
```

---

---

*See [OVERVIEW.md](OVERVIEW.md) for a deeper conceptual dive into the GenAI Double Diamond.*
