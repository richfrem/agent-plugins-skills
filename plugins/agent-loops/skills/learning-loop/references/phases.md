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

## Phase V: Completion & Handoff

> **The specific learning cycle is finished. You must now return control.**

1. **Verify Completion**: Ensure the research or analysis goal you set out to achieve has been genuinely met.
2. **Hand off**: Stop generating new actions and explicitly pass your findings back to the Orchestrator.
3. **DO NOT**:
   - Do not generate `learning_package_snapshot.md` (the Guardian's RLM Synthesizer does this).
   - Do not run `context-bundler` to seal the session (the Guardian does this).
   - Do not push traces to HuggingFace or update Vector DBs (the Guardian does this).
   - Do not commit to Git (the Guardian does this).

## Next Session: The Bridge

The global repository environment (the Guardian) handles sealing your work and waking up the next agent. Your responsibility ends at Phase V.
