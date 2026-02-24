# Learning Loop - Detailed Phase Instructions

## Loop Controls (Ralph-Inspired)

Every loop instance should track:

| Control | Purpose | Default |
|---------|---------|---------|
| **Iteration Counter** | Tracks which pass you're on. Helps detect stalls. | Starts at 1, increments each cycle. |
| **Max Iterations** | Hard safety cap. Prevents runaway loops. | Unlimited (recommend setting 10-50). |
| **Completion Promise** | Deterministic exit condition. Only output when genuinely true. | None (manual closure). |

> **Anti-Lying Rule** (from Ralph): Do NOT declare completion unless the acceptance criteria are genuinely met. Premature closure means the next agent starts blind.

---

## Phase I: The Learning Scout (Orientation)

> **Mandatory first step for every session.**

1. **Access Mode Check**: Read any local `cognitive_primer` or orientation documentation.
2. **Context Load**: Execute the environment's Wakeup / Context Load tool to retrieve the current historical state.
3. **Integrity Check**: Validate the loaded context is coherent and not corrupted. If FAIL → Safe Mode (read-only). If PASS → proceed.
4. **Truth Anchor**: Locate and ingest the `learning_package_snapshot.md` (or equivalent Cognitive Hologram) embedded in the waking context.
5. **Iteration Check**: If resuming a loop, read the iteration counter. Log: `"Loop iteration N of M"`.

## Phase II: Intelligence Synthesis

1. **Context Check**: Review existing topic notes in your designated `learning/` or `memory/` directories.
2. **Mode Selection**:
   - **Standard**: Record Architecture Decision Records (ADRs), update protocols, write to permanent memory.
   - **Evolutionary**: Apply mutation algorithms, evaluate through adversary gates, and store in an archive.
3. **Conflict Resolution**:
   - New confirms old? → Update/Append.
   - New contradicts old? → Create a resolution/disputes document.
4. **Content Hygiene**: Ensure all generated diagrams are saved as separate files (e.g., `.mmd`), not inline text.

## Phase III: Strategic Gate (HITL Required)

1. **Strategic Review**: Human reviews the updated architecture and learning documents.
2. **Align Intent**: Ensure autonomous research matches session goals.
3. **Approval**: Explicit "Approved" or "Proceed" required.
4. **Backtrack**: If FAIL → return to Self-Correction phase.

## Phase IV: Red Team Audit Loop

> **Iterative cycle until "Ready" verdict.**
> Can optionally be run as a **subagent** in a forked context to keep the main session clean.

1. **Agree on Topic**: Confirm research focus with user.
2. **Create Storage**: Generate isolated topic folders (e.g., `learning/topics/[topic]/`).
3. **Capture Research**: Write analysis, questions, and sources logic.
4. **Bundle Generation**: Compile all research into a centralized packet or manifest.
5. **Red Team Feedback**: Present the audit packet to the user or an adversarial sub-agent.
   - "More Research" → Capture feedback, loop back to step 3.
   - "Ready" → Proceed to Phase V.

## Phase V: Sovereign Context Synthesis

> **Generate the cognitive hologram summarizing the session.**

1. **Trigger Synthesis**: Call the configured RLM (Representation Learning Model) or summarizing agent.
2. **Map Phase**: Read all protocols, ADRs, and code modified during the session.
3. **Reduce Phase**: Generate a concise, holistic summary of the newly created knowledge.
4. **Write Hologram**: Output this synthesized truth to `learning_package_snapshot.md`.

## Phase VI: Seal

1. **Completion Promise Gate**: Before sealing, explicitly verify acceptance criteria are met.
   - If a completion promise was set → Is the statement genuinely true? If NO → loop back.
   - If max iterations reached → Document what's blocking and what was attempted. Seal as incomplete.
2. **Bundle Session Artifacts**: Gather all files produced during the loop into a coherent session package using the `context-bundler`.
3. **Verify Completeness**: Ensure all expected outputs are accounted for.
4. **Increment Counter**: Update iteration count. Log: `"Sealed at iteration N"`.
5. **Tag**: Mark the session bundle with a timestamp and summary.

## Phase VII: Persistence

1. **Dual-Path Broadcast**: Transport the short-term session memory into long-term persistence storage.
2. **Persistence Modes**:
   - **Incremental**: Append recent traces to a structured log (e.g., `jsonl`).
   - **Full Sync**: Regenerate all known records for massive architectural shifts.
3. **Remote Sync**: If configured, push traces to an external store (e.g., vector database, model registry, or remote repository).

## Phase VIII: Self-Correction

> **Mandatory retrospective cycle.**

1. **Deploy & Policy Update**: If code changed, verify testing and container states.
2. **Loop Retrospective**: Analyze what went right and wrong during the session. Generate a retro document.
3. **Share Knowledge**: Ensure the retro is visible for the next orientation cycle.
4. **Backtrack Target**: Failed gates from earlier phases loop back here for correction.

## Phase IX: Relational Ingestion & Closure

1. **Knowledge Ingest**: Execute commands to update the local RAG / Vector Database with the finalized texts.
2. **Version Control**: Run standard git add, commit, and push protocols to sync to remote.
3. **Closure**: Formally declare the loop terminated and wait for next wakeup.

## Phase X: Model Forge (Optional)

> **Long-running: Fine-tuning from accumulated session traces.**

1. **HITL Gate**: Human decides if enough traces exist to fine-tune a specialized model.
2. **Forge Dataset**: Convert accumulated `jsonl` traces into training data.
3. **Execution**: Run localized parameter-efficient fine-tuning (e.g., QLoRA).
4. **Deployment**: Export model (e.g., GGUF) and deploy it back into the agent ecosystem.
5. **Loop Back**: Return to Phase VIII for final retrospective of the tuning session.

## Next Session: The Bridge

1. **Boot**: The next agent session loads the environment Wakeup tool.
2. **Retrieve**: It receives the most recently sealed `learning_package_snapshot.md`.
3. **Resume**: The agent continues seamlessly from its predecessor's preserved state.
