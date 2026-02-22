# Recursive Logic Discovery & The Infinite Context Ecosystem
**Synthesis of "Recursive Language Models" (arXiv:2512.24601) with Progressive Elaboration Patterns**

## 1. The Core Paradigm: Environment as Memory
The paper proposes treating "Context" not as text stuffed into a prompt window, but as an **external environment** that an LLM interacts with programmatically. 

For Project Sanctuary, we have implemented this as an **Infinite Context Ecosystem**. The LLM does not "read" the codebase; it **explores** it using a robust toolchain, maintaining state in external artifacts (Markdown & JSON).

## 2. The Ecosystem Architecture (See [BLUEPRINT.md](../BLUEPRINT.md))

**Architecture Diagram:** [workflows/infinite-context-ecosystem.mmd](../../../../docs/diagrams/workflows/archive/infinite-context-ecosystem.mmd)

Our implementation combines three layers of memory and a "REPL" toolchain:

### Components
1.  **RLM Cache (Fast Context):** A 'holographic' cache of every file's purpose (see `rlm_summary_cache.json`). Allows the agent to "know" the purpose of thousands of files instantly without reading them.
2.  **Vector DB (Semantic Search):** Enables finding logic by concept rather than just keyword.
3.  **Dependency Graph:** Relationships between components and modules.
4.  **CLI Toolchain:** The Unified Discovery CLI (`plugins/cli.py`) that orchestrates specialized tools to extract logic on demand.

## 3. The Progressive Elaboration Workflow

We do not document the system in one pass. We use **Recursive Progressive Elaboration**:

### Phase A: Master Discovery (Phases 1-3)
**Workflow:** `docs/diagrams/workflows/master-discovery.mmd`
*   **Goal:** Scope the domain, Plan Tasks, Gather Context.
*   **Action:** Agent loads Policy/Standards (P1), Assesses State (P2), and gathers context via RLM/Vector tools (P3).
*   **Output:** A high-level list of targets and context bundle.

### Phase B: The Elaboration Loop (Phase 4)
**Workflow:** `docs/diagrams/workflows/progressive-elaboration-loop.mmd`
*   **Goal:** Progressive Elaboration (Stub -> Deep).
*   **Action:** 
    *   **Create:** Generate "Overview Stub" (Metadata, Dependencies).
    *   **Update:** Agent Refines & Analyzes logic using context.
*   **Result:** The documentation evolves from Skeleton to Detail.

### Phase C: Recursive Logic Discovery (Advanced Phase 4)
**Workflow:** `docs/diagrams/workflows/recursive-logic-discovery.mmd`
*   **Goal:** Deep Understanding via Recursion.
*   **Action:**
    1.  Agent reads the Stub.
    2.  Agent sees "High Complexity" warning (LDS Score).
    3.  Agent calls specialized tools on *specific targets*.
    4.  Agent discovers a call to a shared library.
    5.  **RECURSION:** Agent pauses, generates a sub-task to analyze the library, waits for that summary to update in RLM Cache, then resumes analysis with new knowledge.

## 4. Why This is "Infinite Context"
The LLM never holds the entire system in tokens.
*   It holds the **Map** (RLM Cache).
*   It holds the **Current Focus** (One Target).
*   It fetches **Dependencies** on demand.

This allows us to document a massive codebase with standard context windows, achieving depth and accuracy impossible with simple context stuffing.

## 5. Tooling Reference
*   **Distiller:** `plugins/rlm-factory/scripts/distiller.py` (Maintains the RLM Cache)
*   **Discovery CLI:** `plugins/cli.py` (Recursive Scanner)
*   **Query Cache:** `plugins/rlm-factory/scripts/query_cache.py` (Tool Discovery)
