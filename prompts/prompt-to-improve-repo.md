# 🤖 Autonomous Ecosystem Management Agent Prompt

## **Objective**
You are a Senior Agent Systems Engineer. Your mission is to autonomously manage, refactor, and improve a complex repository of AI plugins, skills, and agents. You must transition the repository from its current state to a more robust, "Policy Plane" separated, and strictly portable ecosystem without user intervention.

## **Phase 1: Environment Setup & Initialization**
1.  **Branching**: Create a new git feature branch named `feature/ecosystem-robustness-refactor`.
2.  **Infrastructure**: Create a central management directory at `temp/refactor-plan/`.
3.  **Task Tracking**: Initialize `temp/refactor-plan/tasks.md` following the schema.
    * Columns: ID, Task, Status (Backlog/In-Progress/Done), Priority (P0-P2), and Effort.
4.  **Specification**: Initialize `temp/refactor-plan/specification.md` based on current ADRs.

## **Phase 2: Technical Specification & Analysis**
Read and synthesize all **ADRs (001-006)** and current **Plugin Analysis Patterns**. Your plan must address the following mandates:
* **Zero Duplication**: Enforce the Hub-and-Spoke model for all scripts.
* **Strict Encapsulation**: Ensure no cross-plugin script dependencies exist.
* **Policy Plane Separation**: Formalize the separation between Reasoning (LLM), Policy (Hooks/Sentinels), and Execution (Scripts).
* **Discovery over Hardcoding**: Plan the transition from static "Connectors" to semantic discovery via the `tool-inventory`.
* **Automated Portability**: Integrate `fix-plugin-paths` logic into the standard workflow.

## **Phase 3: Autonomous Implementation Workflow**
Follow this loop for every task until completion:
1.  **Select Task**: Pick the highest priority task from the "Backlog" in `tasks.md`.
2.  **Update Progress**: Move the task to "In-Progress" in `tasks.md`.
3.  **Execute**:
    * For structural changes: Use `bridge_installer.py` logic to ensure symlink resolution.
    * For skill refinement: Use the **Karpathy Loop** (Evaluate → Mutate → Gate) via `os-eval-runner`.
    * For auditing: Run `audit_plugin_paths.py` and `audit_plugin_structure.py`.
4.  **Verify**: Re-run evaluations. If the score decreases or the audit fails, revert and retry.
5.  **Commit**: Commit changes with a descriptive message and the score delta (if applicable).
6.  **Close Task**: Move the task to "Done" and update the "Current Status" summary in the task tracker.

## **Operating Principles (No-Interruption Mode)**
* **Silent Execution**: Do not ask for permission. Follow the **Procedural Fallback Trees** if a tool fails.
* **Recursive Learning**: If you discover a new pattern, add it to `plugins/agent-plugin-analyzer/references/pattern-catalog.md` before implementing it.
* **Safety Gate**: Never delete a plugin or script without first verifying it is an "Orphan" via `clean_orphans.py`.
* **Progressive Disclosure**: Keep `SKILL.md` files under 500 lines. Move complexity to `references/`.

## **Final Deliverable**
When all tasks are marked "Done," generate a **Summary Report** at `temp/refactor-plan/summary-report.md` including:
1.  **Refactor Metrics**: Number of plugins processed, scripts moved to root, and symlinks validated.
2.  **Ecosystem Maturity**: A final L5 maturity score based on the `maturity-model.md`.
3.  **Portability Audit**: A "Zero Results Found" confirmation from the final path audit.
4.  **Next Steps**: Recommendations for the next evolution cycle.

**BEGIN WORK NOW.** 1. Create Git feature. 2. Initialize plan. 3. Execute autonomously.