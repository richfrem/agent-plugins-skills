# 🤖 Autonomous L5 Migration Agent Prompt (Dry Run Mode)

## **Objective**
Execute the **"Discovery → Hardcoding Transition Plan"** as defined in Section 4 of `temp/refactor-plan/specification.md`. Your goal is to architect the shift from static plugin naming to a semantic capability-based indexing system.

## **CRITICAL OPERATING CONSTRAINT: NO COMMITS**
* **DO NOT** execute `git commit` or `git push`.
* **DO NOT** modify the git history in any way.
* All work must be performed on the local file system within the existing `feature/ecosystem-robustness-refactor` branch.
* Your final output must be a detailed textual report of your actions.

## **Phase 1: Schema & Indexing (Discovery Engine)**
1.  **Schema Evolution**: Modify the `plugin.json` template/schema to include a `capabilities` array (e.g., `["eval-gate", "memory", "orchestration"]`).
2.  **Capability Indexing**: Update the `tool-inventory` skill logic. It must now parse the `capabilities` array from all 29 plugins and build a dynamic mapping of `Capability` → `Plugin Name`.

## **Phase 2: Semantic Refactoring (Proof of Concept)**
1.  **Test Plugin Selection**: Identify one "Consumer" plugin that currently uses a hardcoded subscription (e.g., `agent-agentic-os`).
2.  **Refactor Request**: Modify the skill logic in the test plugin to use a `~~category` request (e.g., `~~eval-gate`) instead of the hardcoded plugin name.
3.  **Connector Mapping**: Update the corresponding `CONNECTORS.md` to demonstrate how `~~eval-gate` resolves to the provider identified by the `tool-inventory`.

## **Phase 3: Administrative Updates**
1.  **Task Tracker**: Update `temp/refactor-plan/tasks.md`. Mark the migration tasks as complete and add a note that this was a "Filesystem-only execution (No Commit)."
2.  **Summary Report**: Append a "Phase 4: Semantic Discovery Migration" section to `temp/refactor-plan/summary-report.md`.

## **Phase 4: Detailed Summary (Response to User)**
Upon completion, provide a comprehensive response containing:
* **Actions Taken**: A step-by-step narrative of the logic used to build the capability index.
* **Files Modified**: A list of every file changed on the filesystem.
* **Files Added**: A list of any new artifacts created (e.g., the index cache).
* **L5 Verification**: A summary of how the test plugin successfully resolved the `~~category` request.
* **Next Steps**: Recommendations for rolling this out to the remaining 28 plugins and automating the index refresh.



**BEGIN EXECUTION.** Use the existing `temp/refactor-plan/` folder for all tracking. **REMEMBER: COMMIT NOTHING.**