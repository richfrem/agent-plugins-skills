"""
tests/interview_helpers.py -- Shared Interview-Contract Test Helpers
=======================================================================

Purpose:
    Shared helpers for staging and recording the standard interview contract in
    control-plane tests, plus re-exports of the test-only REASON_* free-text
    constants from control_plane/constants.py (single source of truth -- see
    config-driven-constants-over-hardcoding.md).

Key Input Dependencies:
    - control_plane/registry.py's TransitionRegistry (transition_templates.yaml)
    - control_plane/constants.py (REASON_* constants)
    - A ControlPlane instance and sqlite3 access to its db_path, passed in by callers

Key Functions:
    - sequential_answers_for_edge() -- builds an interactive input_fn for one
      coordinate_transition() call, deriving the guidance-confirmation requirement
      from the live TransitionRegistry rather than hardcoding it per test.
    - stage_interview_answers() -- stages a complete human-answered interview using
      registry-derived question IDs.
    - REASON_* -- re-exported from control_plane.constants for backward compatibility
      with existing `from interview_helpers import REASON_*` call sites.
"""

import sqlite3
import time
from typing import List, Optional

from control_plane.registry import TransitionRegistry
# Re-exported so existing `from interview_helpers import REASON_INTERVIEW_COMPLETE`
# call sites keep working; the constants themselves are defined once in the shared
# control_plane/constants.py, not here (per config-driven-constants-over-hardcoding.md).
from control_plane.constants import (  # noqa: F401
    REASON_INTERVIEW_COMPLETE,
    REASON_WORKTREE_CREATED,
    REASON_WORKTREE_ISOLATED,
    REASON_NOT_NEEDED_FOR_TEST,
    REASON_PLAN_DISPOSITION,
    REASON_ENTER_DRAFT_PLAN,
    REASON_ATTEMPT_COMPLETE,
)


def sequential_answers_for_edge(
    from_state: str,
    to_state: str,
    own_answers: List[str],
    *,
    registry: Optional[TransitionRegistry] = None,
):
    """Builds an interactive input_fn for one coordinate_transition() call, deriving
    whether the mandatory guidance-compliance confirmation is needed from the LIVE
    registry (transition_templates.yaml) rather than hardcoding it per test -- so a
    future change to what's asked on an edge, or to the guidance gate itself, only
    needs updating here, not in every test that exercises that edge.

    `own_answers` must supply every answer the edge itself asks for, in order: its
    declared `human_questions`, THEN the approval y/n prompt if `template.approval`
    is required (the coordinator asks that immediately after human_questions). Only
    the trailing mandatory guidance-compliance confirmation is appended
    automatically by this helper (and only when the edge isn't a cryptographic-proof edge, which takes a signature
    instead of typed answers).
    """
    reg = registry or TransitionRegistry.load_default()
    template = reg.get_template(from_state, to_state)
    assert template is not None, f"No template registered for {from_state} -> {to_state}"

    answers = list(own_answers)
    if not template.requires_cryptographic_proof:
        answers.append("YES")

    it = iter(answers)
    return lambda _prompt: next(it)


def stage_interview_answers(
    cp, task_id: str, to_state: str = "DRAFT_PLAN", classification: str = "STANDARD"
) -> None:
    """Stage a complete human-answered interview using registry-derived IDs."""
    answers = {
        "interview_classification": classification,
        "interview_summary": "Implement and verify the requested control-plane change.",
        "interview_scope": "The files covered by the current task and its tests.",
        "interview_verification": "The focused and full test suites pass.",
        "interview_acceptance_criteria": "Preserve existing gates and enforce the new contract.",
        "interview_planning_model_effort": "Confirm current model and medium effort for planning.",
        "interview_trivial_evidence": "The focused tests and diff identify the smallest verified change.",
    }
    registry = TransitionRegistry.load_default()
    template = registry.get_template("INTERVIEW", to_state)
    assert template is not None
    question_ids = list(template.stage_question_ids or [])

    conn = sqlite3.connect(cp.db_path)
    try:
        occupancy = conn.execute(
            "SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1",
            (task_id,),
        ).fetchone()
        assert occupancy is not None
        now = time.time()
        for question_id in question_ids:
            conn.execute(
                """
                INSERT INTO transition_decisions (
                    task_id, source_occupancy_transition_id, from_state, to_state,
                    question_id, answer, decision_type, actor, recorded_at
                ) VALUES (?, ?, 'INTERVIEW', ?, ?, ?, 'ANSWER', 'human', ?)
                """,
                (task_id, occupancy[0], to_state, question_id, answers[question_id], now),
            )
        conn.commit()
    finally:
        conn.close()

    if cp.get_task(task_id)["state"] == "INTERVIEW":
        for question_id in question_ids:
            cp.update_interview_plan_outline(task_id, question_id, answers[question_id], actor="human")
