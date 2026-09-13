#!/usr/bin/env python3
"""
control_plane/wrappers/record_interview_question.py
===================================================

Purpose:
    Fixed-identity wrapper for recording interview questions and answers.
    Hardcodes action identity 'interview_question'. Never allows caller-supplied
    action identity. Authorizes against task's current phase occupancy before
    executing any side effect (zero side effect on denial).
"""

import sys
from pathlib import Path

# Ensure scripts directory is on sys.path for direct script execution
_scripts_dir = str(Path(__file__).resolve().parent.parent.parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from typing import Any, Dict, Optional
from agent_control import ControlPlane, PhaseCapabilityDenied
from control_plane.registry import TransitionRegistry


ACTION_IDENTITY = "interview_question"


def _denial_response(control_plane: ControlPlane, task_id: str, error: Exception) -> Dict[str, Any]:
    """Build the read-only denial envelope required by the recorder contract."""
    task = control_plane.get_task(task_id)
    state = str(task.get("state", "UNKNOWN")) if task else "UNKNOWN"
    last_transition = control_plane.get_last_transition(task_id) if task else None
    occupancy = int(last_transition.transition_id) if last_transition else 0
    if state == "INTERVIEW":
        recovery = (
            "Correct the failed check and retry record_interview_question.py with the canonical "
            "question ID, explicit --answer, and --target-state DRAFT_PLAN."
        )
    else:
        recovery = (
            f"Run transition-guidance --task-id {task_id} and follow one of the legal next actions."
        )
    if isinstance(error, PhaseCapabilityDenied):
        code = "CAPABILITY_DENIED"
    elif isinstance(error, ValueError):
        code = "CONTRACT_DENIED"
    else:
        code = "PERSISTENCE_DENIED"
    return {
        "status": "DENIED",
        "error": {
            "code": code,
            "check": str(error),
            "state": state,
            "occupancy": occupancy,
            "recovery": recovery,
        },
    }


def record_interview_question(
    task_id: str,
    question: str,
    options: Dict[str, str],
    recommended: str,
    answer: Optional[str] = None,
    actor: str = "interviewer",
    control_plane: Optional[ControlPlane] = None,
    target_state: Optional[str] = None,
) -> Dict[str, Any]:
    """Records an interview question turn after verifying phase capability.

    Fails closed if the task's current phase occupancy does not release 'interview_question'.
    Guarantees NO row is created in transition_decisions or any log table on denial.
    """
    cp = control_plane or ControlPlane()

    if target_state is None or not target_state.strip():
        raise ValueError(
            "target_state must be explicit; the recorder will not infer a transition target."
        )
    if answer is None:
        raise ValueError(
            f"Answer for question '{question}' must be explicit; recommended is not an answer."
        )
    requested_target = target_state
    chosen_answer = answer
    if not chosen_answer.strip():
        raise ValueError(f"Answer for question '{question}' must be non-empty.")

    # 1. Authoritative capability & occupancy gate
    # Uses fixed internal ACTION_IDENTITY. Caller cannot supply action identity.
    cap = cp.verify_phase_capability(task_id, ACTION_IDENTITY)

    registry = getattr(cp, "_transition_registry", None) or TransitionRegistry.load_default()
    template = registry.get_template(cap.current_state, requested_target)
    if template is None or requested_target != "DRAFT_PLAN":
        raise ValueError(
            f"Requested interview target '{requested_target}' is not a legal target from "
            f"state '{cap.current_state}'."
        )
    if question not in (template.stage_question_ids or []):
        raise ValueError(
            f"Unknown canonical interview question '{question}' for target '{requested_target}'."
        )

    # 2. Side effect: record into transition_decisions
    # Protected side effect occurs only after authorization passes.
    # Exact binding contract:
    # - task_id: bound to verified task
    # - source_occupancy_transition_id: bound strictly to current occupancy transition ID
    # - from_state / to_state: bound to inbound releasing edge (e.g. INTAKE -> INTERVIEW)
    # - question_id: the exact unique question text
    # - answer: the explicit answer supplied by the human or controller
    # - decision_type: 'ANSWER'
    # - actor: the recorded answering party
    # - recorded_at: wall clock timestamp via ClockPort
    # Rejection contract: Duplicate question_id within the same task occupancy is rejected.
    # Keep the persisted answer canonical so transition gates can compare it
    # with the option keys and free-text values supplied by the user.

    receipt = cp.record_interview_answer(
        task_id=task_id,
        source_occupancy_transition_id=cap.transition_id,
        from_state=cap.current_state,
        to_state=requested_target,
        question_id=question,
        answer=chosen_answer,
        actor=actor,
    )
    answers = cp._persistence.get_unconsumed_transition_answers(
        task_id, cap.current_state, requested_target
    )
    missing = next(
        (qid for qid in (template.stage_question_ids or []) if qid not in answers),
        None,
    )
    if missing:
        next_action = {
            "kind": "question",
            "state": cap.current_state,
            "command": (
                "python3 plugins/agent-agentic-os/scripts/control_plane/wrappers/record_interview_question.py "
                f"--task-id {task_id} --question {missing} "
                f"--target-state {requested_target} --options '{{}}' --recommended '' --answer '<answer>'"
            ),
        }
    else:
        next_action = {
            "kind": "transition",
            "state": requested_target,
            "command": (
                "python3 plugins/agent-agentic-os/scripts/agent_control.py "
                f"coordinate-transition --task-id {task_id} --to {requested_target}"
            ),
        }
    return {
        "status": "RECORDED",
        "decision_id": receipt["decision_id"],
        "task_id": task_id,
        "source_occupancy_transition_id": cap.transition_id,
        "question_id": question,
        "target_state": requested_target,
        "action_identity": ACTION_IDENTITY,
        "artifact_path": receipt["artifact_path"],
        "outline_artifact": receipt["artifact_path"],
        "outline_revision": receipt["outline_revision"],
        "next_action": next_action,
    }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Fixed-identity interview question wrapper")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--question", required=True)
    parser.add_argument("--options", required=True, help="JSON string of options dict")
    parser.add_argument("--recommended", required=True)
    parser.add_argument("--answer", default=None)
    parser.add_argument("--actor", default="interviewer")
    parser.add_argument("--target-state", default=None)

    args = parser.parse_args()
    cp = ControlPlane()
    try:
        options = json.loads(args.options)
        res = record_interview_question(
            task_id=args.task_id,
            question=args.question,
            options=options,
            recommended=args.recommended,
            answer=args.answer,
            actor=args.actor,
            target_state=args.target_state,
            control_plane=cp,
        )
        print(json.dumps(res, indent=2))
    except (PhaseCapabilityDenied, ValueError) as e:
        print(json.dumps(_denial_response(cp, args.task_id, e), indent=2))
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
