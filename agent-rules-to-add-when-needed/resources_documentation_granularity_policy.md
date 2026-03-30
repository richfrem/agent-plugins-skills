---
trigger: always_on
---

# Documentation Granularity & Execution Standard
**JUSTIN Modernization Project**

## 1. Objective
Ensures that all analysis and documentation tasks are executed with maximum fidelity, traceability, and "ground truth" verification. High-level summaries are insufficient; granular subtasks are mandatory.

## 2. Granular Task Management
Every documentation task created via `/maintenance-task` or manual markdown must follow the **Subtask Hierarchy**.

### 2.1 Pattern: Phase -> Subtask
Tasks must not simply list "Phase 1: Setup". They must list actionable, verifiable checkpoints:
*   **Subtask 1.1**: Initialize Context Manifest (`plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py`).
*   **Subtask 1.2**: Generate context bundle (`plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py bundle`).
*   **Subtask 1.3**: Validate bundle content (Ensure raw source and existing docs are present).

### 2.2 Verifiable Checkboxes
- Use `[ ]` for pending tasks.
- Use `[/]` for in-progress tasks (running background commands).
- Use `[x]` for completed tasks.
- **Never** mark a high-level phase as done if any subtask is incomplete.

## 3. Mandatory Intelligence Sync
Documentation in this repository is not just "human readable"; it feeds the Agent's context.

### 3.1 RLM Distillation
Every time an Overview or Business Rule is created/modified, you MUST run:
```bash
python plugins/rlm-factory/scripts/distiller.py --file [FILE_PATH]
```
This updates the LLM-optimized summary cache.

### 3.2 Vector DB Ingestion
Every technical source (SQL dumps, XML-MD) and human-written documentation MUST be ingested:
```bash
wsl python3 plugins/vector-db/scripts/ingest.py --file [FILE_PATH]
```
This enables semantic "RAG" search for future analysis.

### 3.3 Inventory Rebuilding
After creating new artifacts, rebuild the master object collection:
```bash
python scripts/inventory/build_master_collection.py --full
```

## 4. Human Review & Quality Gate
The "Human-in-the-loop" is a mandatory firewall before state changes.

### 4.1 The Approval Gate
Before executing any `git commit` or `git push` for finalized documentation:
1.  **Draft Approval**: Present the updated documentation link (Overviews).
2.  **Checklist Approval**: Present the Granular Checklist showing all completed subtasks.
3.  **Wait for Confirm**: Do not move files to `tasks/done/` without explicit user approval.
4.  **Post-Merge Cleanup**: AFTER the PR is merged:
    - **Step 4.1**: **CRITICAL**: Confirm with the USER that the Pull Request (PR) and Merge are complete. Do NOT proceed until you have explicit confirmation.
    - **Step 4.2**: Pull the latest `main` (`git pull origin main`) and switch to it.
    - **Step 4.3**: Delete the local and remote feature branch.

## 5. Continuous Improvement (The Optimizer)
Reflect on every task:
- **Tooling Gaps**: If you had to manually extract data, update the corresponding tool or create a new one.
- **Rule Updates**: If a standard was ambiguous, update the `plugins/legacy system/resources/rules/`.
- **Diagram Updates**: Keep process diagrams (`.mmd`) in sync with workflow changes.

## 6. Ground Truth Verification
- **Distrust Summaries**: Always verify against the raw PL/SQL source or XML-MD.
- **Verify Infrastructure**: If a package or table is referenced but not in the codebase, use `sqlplus` to extract it from the database immediately. Do not guess.

## 7. Task Content & Artifact Linking
To facilitate efficient Human Review, every analysis task file MUST include a **"Review Items"** section.

### 7.1 Mandatory Links
- **Temporary Context Bundle**: Provide the absolute or relative path to the generated bundle (e.g., `temp/context-bundles/[ID]_context.md`). This allows the user to see the "Ground Truth" the Agent used for analysis.
- **Final Artifacts**: Provide direct links to all new or modified documentation (e.g., `[Overview Page](plugins/legacy system/resources/docs/modernization/overview.md)`).
- **Sub-Tasks**: Phases and Sub-tasks MUST match the specific workflow (e.g., `codify-library` or `codify-form`) but with specific filenames where possible.

### 7.2 Verification Protocol
The Agent must present these links to the USER during the **Human Review Gate** (Phase 6).
