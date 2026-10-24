#!/usr/bin/env python3
"""
control_plane/review_selection.py
=================================

Purpose:
    Shared helpers for the review-selection-v1 contract (auth-ciba-increment-b T17, issue #639) on BOTH
    review edges. Review needed -> method -> (internal methods only) runtime -> model -> effort. The three
    internal selections are YAML human questions with an `asked_when` condition on the method answer.
    They are asked only when the condition holds, human-typed only, and are NOT in the database's
    required-question set (an external-bundle review has nothing to record), so their presence is
    enforced here instead: a reviewer outcome cannot be recorded for an internal review without them.

Key Input Dependencies:
    - control_plane/transition_templates.yaml (`asked_when: {question_id, answer_contains}`)
    - control_plane/registry.py (TransitionRegistry); transition_decisions rows

Key Functions:
    - conditional_questions()  -- the template's questions that carry an asked_when condition
    - condition_holds()        -- whether a question's asked_when is satisfied by the answers so far
    - review_selection_gaps()  -- conditional question ids that should have a human decision but do not
    - review_edge_into()       -- the review edge that leads into a review state, or None

Constants:
    - REVIEW_EDGES
"""

import sqlite3
from typing import Any, Dict, List, Mapping, Optional, Tuple

REVIEW_EDGES: Tuple[Tuple[str, str], ...] = (
    ("PLAN_REVIEW", "MULTI_AGENT_REVIEW"),
    ("WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW"),
)


def conditional_questions(template: Any) -> List[Dict[str, Any]]:
    """Return the human questions of a template that are conditional (have `asked_when`)."""
    return [q for q in template.human_questions if q.get("asked_when")]


def condition_holds(question: Mapping[str, Any], answers: Mapping[str, str]) -> bool:
    """True when the question's asked_when is satisfied by the answers given so far."""
    condition = question.get("asked_when")
    if not condition:
        return True
    answer = answers.get(condition["question_id"])
    return answer is not None and condition["answer_contains"] in answer


def review_edge_into(review_state: str) -> Optional[Tuple[str, str]]:
    """Return the review edge whose destination is review_state, or None."""
    for edge in REVIEW_EDGES:
        if edge[1] == review_state:
            return edge
    return None


def review_selection_gaps(conn: sqlite3.Connection, registry: Any, task_id: str, from_state: str, to_state: str) -> List[str]:
    """Conditional question ids that the recorded method answer requires but that have no human decision."""
    template = registry.get_template(from_state, to_state)
    if template is None:
        return []
    rows = conn.execute(
        "SELECT question_id, answer, actor FROM transition_decisions WHERE task_id = ? AND from_state = ? AND to_state = ? ORDER BY decision_id",
        (task_id, from_state, to_state),
    ).fetchall()
    answers = {r[0]: r[1] for r in rows}
    human = {r[0] for r in rows if r[2] == "human" and r[1] and str(r[1]).strip()}
    return [q["question_id"] for q in conditional_questions(template) if condition_holds(q, answers) and q["question_id"] not in human]
