"""Shared helpers for recording the standard interview contract in tests."""

import sqlite3
import time

from control_plane.registry import TransitionRegistry


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
