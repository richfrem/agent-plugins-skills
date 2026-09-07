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


ACTION_IDENTITY = "interview_question"


def record_interview_question(
    task_id: str,
    question: str,
    options: Dict[str, str],
    recommended: str,
    answer: Optional[str] = None,
    actor: str = "interviewer",
    control_plane: Optional[ControlPlane] = None,
) -> Dict[str, Any]:
    """Records an interview question turn after verifying phase capability.

    Fails closed if the task's current phase occupancy does not release 'interview_question'.
    Guarantees NO row is created in transition_decisions or any log table on denial.
    """
    cp = control_plane or ControlPlane()

    # 1. Authoritative capability & occupancy gate
    # Uses fixed internal ACTION_IDENTITY. Caller cannot supply action identity.
    cap = cp.verify_phase_capability(task_id, ACTION_IDENTITY)

    # 2. Side effect: record into transition_decisions
    # Protected side effect occurs only after authorization passes.
    # Exact binding contract:
    # - task_id: bound to verified task
    # - source_occupancy_transition_id: bound strictly to current occupancy transition ID
    # - from_state / to_state: bound to inbound releasing edge (e.g. INTAKE -> INTERVIEW)
    # - question_id: the exact unique question text
    # - answer: formatted Option <recommended/chosen>: <rationale>
    # - decision_type: 'ANSWER'
    # - actor: the recorded answering party
    # - recorded_at: wall clock timestamp via ClockPort
    # Rejection contract: Duplicate question_id within the same task occupancy is rejected.
    chosen_answer = answer if answer is not None else recommended
    formatted_answer = f"Option {chosen_answer}: {options.get(chosen_answer, '')}"

    decision_id = cp.record_decision(
        task_id=task_id,
        source_occupancy_transition_id=cap.transition_id,
        from_state=cap.releasing_edge[0],
        to_state=cap.releasing_edge[1],
        question_id=question,
        answer=formatted_answer,
        decision_type="ANSWER",
        actor=actor,
    )
    return {
        "status": "RECORDED",
        "decision_id": decision_id,
        "task_id": task_id,
        "transition_id": cap.transition_id,
        "action_identity": ACTION_IDENTITY,
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

    args = parser.parse_args()
    try:
        options = json.loads(args.options)
        res = record_interview_question(
            task_id=args.task_id,
            question=args.question,
            options=options,
            recommended=args.recommended,
            answer=args.answer,
            actor=args.actor,
        )
        print(json.dumps(res, indent=2))
    except PhaseCapabilityDenied as e:
        print(f"CAPABILITY DENIED: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
