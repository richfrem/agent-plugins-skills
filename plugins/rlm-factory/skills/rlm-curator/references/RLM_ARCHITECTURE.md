# Architecture: RLM Late-Binding & Recursive Discovery

## 1. Executive Summary

This architecture implements a **Recursive Learning Model (RLM)** to minimize cognitive load and token overhead. Instead of statically loading hundreds of tool definitions, the agent utilizes a **Late-Binding / Discovery** pattern via a single "Meta-Skill" (The Librarian).

Furthermore, the system implements a **Self-Healing Feedback Loop**, where the Distiller (LLM) not only caches summaries but actively updates the "human-readable" inventory descriptions, keeping documentation synchronized with code.

## 2. The Problem: Static Context Overhead

* **Context Poisoning:** Loading all tools confuses the agent with unrelated noise.
* **Maintenance Drift:** Manual descriptions in `tool_inventory.json` diverge from actual code behavior.
* **Token Cost:** High overhead for unused tools.

## 3. The Solution: Recursive "Librarian" Pattern

### A. The Distillation Layer (Granite LLM)
We utilize **IBM Granite** (via Ollama) to process raw code (Python/JS/SQL).
* **Input:** Raw Source Code.
* **Output:** A high-density **RLM Summary** (Purpose, Usage, Dependencies).
* **Storage:** `rlm_tool_cache.json` (Tools) and `rlm_legacy_cache.json` (Legacy Artifacts).

### B. The Feedback Loop (Enrichment)
**"Code Changes -> Distillation -> Inventory Updates"**

The Distiller pushes the generated "Purpose" back into the Tool Inventory, ensuring the `manage_tool_inventory.py list` command always reflects the latest AI-generated understanding of the tool.

### C. The Execution Flow (Late Binding)
1. **Search:** User/Agent asks "How do I X?" -> Librarian searches RLM Cache.
2. **Retrieve:** Agent retrieves specific usage docs for the best-match tool.
3. **Execute:** Agent runs the tool.

## 4. Technical Implementation

### Directory Structure
```text
.agent/
├── skills/
│   └── tool_discovery/  # The Meta-Skill
├── learning/
│   ├── rlm_tool_cache.json   # Distilled Tool Knowledge
│   └── rlm_legacy_cache.json # Distilled Legacy Knowledge
tools/
├── curate/
│   ├── inventories/manage_tool_inventory.py  # CRUD + Trigger
│   └── rlm/cleanup_cache.py                  # Atomic Consistency
├── codify/
│   └── rlm/distiller.py                      # LLM Engine + Feedback Loop
```

### Sequence Diagram: Tool Enrichment Flow
The following diagram illustrates how adding/updating a tool automatically enriches the inventory description via the RLM Feedback Loop.

![RLM Enrichment Flow](../diagrams/rlm/rlm_tool_enrichment_flow.mmd)

*(See `docs/diagrams/rlm/rlm_tool_enrichment_flow.mmd` for source)*

### Sequence Diagram: Late Binding Flow
The following diagram illustrates how the Agent "discovers" tools just-in-time using the Skill and RLM Query.

![RLM Late Binding Flow](../diagrams/rlm/rlm_late_binding_flow.mmd)

*(See `docs/diagrams/rlm/rlm_late_binding_flow.mmd` for source)*

## 5. Maintenance & Evolution

### The "Self-Healing" Cycle
1. **User updates code** -> `manage_tool_inventory.py update`
2. **Manager triggers Distiller**
3. **Distiller generates new Summary**
4. **Distiller updates Inventory** (via `suppress_distillation=True` to prevent infinite loops)

### Multi-Stack Support
The system supports **Python**, **Node.js**, **SQL**, and **Bash** tools, with generic traversal for inventory management.

## 6. Strategic Benefits

* **Infinite Context:** The library creates an unlimited addressable space of tools.
* **Self-Documenting:** The inventory describes itself based on the actual code.
* **High Precision:** Zero hallucination of non-existent flags.
