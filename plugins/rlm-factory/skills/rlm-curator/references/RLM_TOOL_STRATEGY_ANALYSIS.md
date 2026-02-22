# Analysis: RLM Tool Discovery Strategy

## 1. Executive Summary
This document analyzes the current Recursive Learning Model (RLM) architecture and evaluates options for integrating "Late Binding" Tool Discovery. The goal is to allow the Agent to index and learn from the executable tool inventory (`tool_inventory.json`) without polluting the existing legacy documentation index (`distiller_manifest.json`).

## 2. Current Architecture State

### Core Components
*   **Engine**: `plugins/rlm-factory/scripts/distiller.py`
    *   **Input**: Directory paths defined in `distiller_manifest.json` (or CLI args).
    *   **Processing**: Recursive walk -> Filter (.md/.txt) -> Ollama (Granite 3.2).
    *   **Prompting**: Hardcoded prompt focused on "Business Function" and "Feature Purpose" (Legacy Context).
    *   **Output**: `.agent/learning/rlm_summary_cache.json`.
*   **Manifest**: `tools/standalone/rlm-factory/distiller_manifest.json`
    *   **Scope**: Legacy System Code & Documentation.
    *   **Structure**: `include` directories, `exclude` patterns.
*   **Inventory**: `tools/tool_inventory.json`
    *   **Structure**: Categorized list of executable scripts (.py, .js).
    *   **Metadata**: Manually curated descriptions + status.

### Identified Gaps
1.  **Incompatible Source of Truth**: `distiller.py` expects directory limits, whereas Tools are best defined by the **explicit list** in `tool_inventory.json`.
2.  **Incompatible Prompts**: The current prompt asks "What business function does this serve?". For tools, we need "How do I use this CLI?".
3.  **Cache Contamination**: Mixing "How to run script X" with "How Business Rule Y works" in a single `rlm_summary_cache.json` risks semantic confusion and context poisoning.

## 3. Options for Approach

### Option A: The "Twin Engines" (Separation of Concerns)
Create a dedicated `tool_distiller.py` specifically for the Tool Inventory.
*   **Pros**: 
    *   Zero risk of breaking existing RLM logic.
    *   Can have completely custom input logic (reading JSON inventory directly).
    *   Can have hardcoded "Tool Scientist" prompts without complex mode switching.
*   **Cons**: 
    *   Code duplication (hashing, caching, API calls).
    *   Two scripts to maintain/update if core RLM logic (e.g., Ollama URL) changes.

### Option B: The "Modal Engine" (Unified Distiller)
Refactor `distiller.py` to support distinct **Modes** via CLI arguments.
*   **Mechanism**:
    *   `--mode doc` (Default): Uses `distiller_manifest.json`, Legacy Prompt, `rlm_summary_cache.json`.
    *   `--mode tool`: Uses `tool_inventory.json` (via `--inventory`), Tool Prompt, `rlm_tool_cache.json`.
*   **Pros**:
    *   Single codebase for hashing/caching/API logic.
    *   Centralized configuration.
*   **Cons**:
    *   Increases complexity of `distiller.py`.
    *   Requires careful regression testing to ensure Legacy mode is untouched.

### Option C: The "Hybrid Manifest" (Not Recommended)
Add `tools/` to the existing `distiller_manifest.json`.
*   **Pros**: Simplest code change.
*   **Cons**:
    *   Violates "Dual Source of Truth" requirement.
    *   Pollutes the Legacy Cache with Tool instructions.
    *   Cannot easily apply different Prompts to tools vs docs.

## 4. Recommendation
**Option B (Modal Engine)** is recommended entirely *if and only if* `distiller.py` is refactored cleanly. It balances maintainability with the specialized requirements. 

However, given the user's emphasis on "Systematic" and "No Rework", **Option A (Twin Engines)** might be safer if we want to treat the Tool Discovery system as a distinct "Meta-Skill" subsystem, decoupling it from the Legacy Analysis workflow.

## 5. Integration Point
Regardless of the Engine choice, `plugins/tool-inventory/scripts/manage_tool_inventory.py` will serve as the **Trigger**.
*   **Trigger Event**: `add_tool` or `update_tool` success.
*   **Action**: Spawn subprocess to run the Engine for the specific file.
*   **Result**: Instant consistency between Inventory and Cache.
