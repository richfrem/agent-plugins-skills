# Healthy Transcript: Frictionless Work-Intake

This reference provides a turn-by-turn example transcript demonstrating frictionless progression through `INTAKE -> DRAFT_PLAN -> PLAN_REVIEW -> APPROVED` (schema v15 lean 10-state machine).

| Turn | Agent Reads / Does | Human Sees / Types | Notes & Rules Enforced |
|---|---|---|---|
| **Turn 1: Intake & Scoping** | 1. Reads `transition_templates.yaml` stage contract (`stages.INTAKE`).<br>2. Inspects ledger/context: answers known questions directly.<br>3. Asks the SINGLE remaining genuine gap with recommendation and updates `docs/plans/work-tasks/<task-id>/<task-id>-plan-outline.md`. | Sees:<br>"Based on your prompt, problem summary, scope, and verification are mapped. Question 1 of 1: For the planning phase, would you like to use the recommended low-cost model or specify another? [Recommended: current model, low effort]"<br><br>Types:<br>`1` (Accept recommendation) | **ONE question at a time**: Answers from context, never re-asks known facts. Scoping and outline happen inside `INTAKE`. |
| **Turn 2: Draft Plan & Enter Plan Review** | 1. Confirms outline and transitions `INTAKE -> DRAFT_PLAN`.<br>2. Compiles specification, implementation plan, and execution strategy under `docs/plans/work-tasks/<task-id>/`.<br>3. Coordinates transition `DRAFT_PLAN -> PLAN_REVIEW`. | Sees:<br>"Outline confirmed (`DRAFT_PLAN`). Spec and plan compiled under `docs/plans/work-tasks/<task-id>/`. Transitioning to `PLAN_REVIEW`." | **Artifact location rule**: Task artifacts always live in `docs/plans/work-tasks/<task-id>/`, never flat in plans root. |
| **Turn 3: Plan Review & Adversarial Audit** | 1. Reads `stages.PLAN_REVIEW`.<br>2. Runs adversarial plan audit (`plan_audit.py`) or records human's signed review waiver (`signed_decisions`).<br>3. Presents plan and audit verdict to the human. | Sees:<br>"Plan audit verdict: PASS. Ready for Gate 1 approval." | **Review evidence**: Adversarial audit runs inside `PLAN_REVIEW` (no separate `MULTI_AGENT_REVIEW` or `AWAITING_APPROVAL` hop). |
| **Turn 4: Gate 1 Approval (HARD)** | 1. Agent runs `coordinate-transition --task-id <task-id> --to APPROVED` (halts with `HUMAN_PROOF_REQUIRED`).<br>2. Reads `plan_review_to_approved` (HARD/crypto gate).<br>3. Prepares complete, pasteable OpenSSH signing commands for the human. | Sees:<br>"Gate 1 requires your OpenSSH signature (`PLAN_REVIEW -> APPROVED`). Run `show-challenge`, `ssh-keygen -Y sign`, and `approve-transition` in your terminal." | **HARD Gate**: Only cryptographic proof or reserved human policies require human command execution. Command provided in full, ready to paste, no back-references. |

---

## Guidance Blocks and Recovery

If a task enters a guidance block (`guidance_block_reason != null`), the control plane refuses all transitions.
* **Why**: A guidance block indicates an explicit deviation from protocol or human disagreement on process rules.
* **Cost**: Every transition is blocked until explicitly cleared by the human.
* **Resolution**: The human (and only the human) runs:
  ```bash
  python3 plugins/agent-agentic-os/skills/running-control-plane/scripts/agent_control.py clear-guidance-block --task-id <task-id> --human-confirmed "HUMAN-CONFIRMED: block resolved"
  ```
