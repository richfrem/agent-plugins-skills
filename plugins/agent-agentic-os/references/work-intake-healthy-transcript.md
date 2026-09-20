# Healthy Transcript: Frictionless Work-Intake

This reference provides a turn-by-turn example transcript demonstrating frictionless progression through `INTAKE -> INTERVIEW -> DRAFT_PLAN -> PLAN_REVIEW -> AWAITING_APPROVAL`.

| Turn | Agent Reads / Does | Human Sees / Types | Notes & Rules Enforced |
|---|---|---|---|
| **Turn 1: Intake** | 1. Reads `transition_templates.yaml` stage contract (`stages.INTAKE`).<br>2. Reads edge guidance for `intake_to_interview`.<br>3. Checks DB rules and running directives ledger.<br>4. Detects context already provided in user's prompt. Logs prior art scan automatically.<br>5. Runs transition: `coordinate-transition --task-id <task-id> --to INTERVIEW`. | Sees:<br>"Task `<task-id>` initialized and prior art scanned. Entering INTERVIEW." | **AGENT-RUNNABLE**: Deterministic checks satisfied. Agent runs command directly. Zero questions asked to human for known context. |
| **Turn 2: Interview** | 1. Reads `stages.INTERVIEW` stage contract.<br>2. Inspects ledger/context: answers 4 of 5 baseline questions directly.<br>3. Asks the SINGLE remaining genuine gap with recommendation. | Sees:<br>"Based on your prompt, problem summary, scope, and verification are mapped. Question 1 of 1: For the planning phase, would you like to use the recommended low-cost model or specify another? [Recommended: current model, low effort]"<br><br>Types:<br>`1` (Accept recommendation) | **ONE question at a time**: Answers from context, never re-asks known facts. |
| **Turn 3: Outline & Draft Plan** | 1. Updates `docs/plans/work-tasks/<task-id>/<task-id>-plan-outline.md`.<br>2. Executes transition to `DRAFT_PLAN`.<br>3. Compiles specification and implementation plan under `docs/plans/work-tasks/<task-id>/`.<br>4. Coordinates transition to `PLAN_REVIEW`. | Sees:<br>"Interview outline updated at `docs/plans/work-tasks/<task-id>/<task-id>-plan-outline.md`. Plan compiled. Transitioning to PLAN_REVIEW." | **Artifact location rule**: Task artifacts always live in `docs/plans/work-tasks/<task-id>/`, never flat in plans root. |
| **Turn 4: Plan Review** | 1. Reads `stages.PLAN_REVIEW` and edge `plan_review_to_awaiting_approval`.<br>2. Asks the human once in chat if they accept the plan or want changes. | Sees:<br>"Do you accept the plan as written, or do you require revisions or an optional agent review?"<br><br>Types in chat:<br>"Yes, plan accepted." | **SOFT Approval**: Human approves in chat. Agent does NOT hand command to human. |
| **Turn 5: Advance to Awaiting Approval** | 1. Agent runs `coordinate-transition --task-id <task-id> --to AWAITING_APPROVAL`.<br>2. Reads `awaiting_approval_to_approved` (HARD/crypto gate).<br>3. Prepares complete, pasteable OpenSSH signing command for the human. | Sees:<br>"Plan accepted. Moving to AWAITING_APPROVAL.<br>Next step requires your OpenSSH signature (Gate 1). Please run this exact command in your terminal:<br>`python3 plugins/agent-agentic-os/scripts/agent_control.py coordinate-transition --task-id <task-id> --to APPROVED --interactive --key $HOME/.ssh/agentic-os_signing`" | **HARD Gate**: Only cryptographic proof or reserved human policies require human command execution. Command provided in full, ready to paste, no back-references. |

---

## Guidance Blocks and Recovery

If a task enters a guidance block (`guidance_block_reason != null`), the control plane refuses all transitions.
* **Why**: A guidance block indicates an explicit deviation from protocol or human disagreement on process rules.
* **Cost**: Every transition is blocked until explicitly cleared by the human.
* **Resolution**: The human (and only the human) runs:
  ```bash
  python3 plugins/agent-agentic-os/scripts/agent_control.py clear-guidance-block --task-id <task-id> --human-confirmed "HUMAN-CONFIRMED: block resolved"
  ```
