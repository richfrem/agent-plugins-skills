#!/usr/bin/env python3
"""
control_plane/inspection.py
===========================

Purpose:
    Canonical READ-ONLY inspection of the control-plane database (auth-ciba-increment-b, issue #639,
    task U3): the recorded human/agent decisions for a task and the source-assisted answer candidates.
    It exists so agents stop running ad-hoc SQL against internal tables (which even guessed column
    names wrong). The connection is opened with SQLite's `mode=ro`, so nothing here can write.
    Used by the `agent_control.py inspect-decisions` and `inspect-candidates` verbs, and by the
    guidance that tells an agent to read the recorded decisions after a human runs a command.

Key Input Dependencies:
    - context/control_plane.db (path from ControlPlane.db_path)
    - Python stdlib only (sqlite3)

Key Functions:
    - open_readonly() -- a read-only sqlite3 connection (rows as sqlite3.Row).
    - inspect_decisions() -- transition_decisions rows for a task, in order, optionally by edge.
    - inspect_candidates() -- source_assisted_answer_candidates rows for a task.
    - format_rows() -- a compact text table.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union


def open_readonly(db_path: Union[str, Path]) -> sqlite3.Connection:
    """Open the database read-only; any write attempt raises sqlite3.OperationalError."""
    conn = sqlite3.connect(f"file:{Path(db_path)}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def inspect_decisions(
    conn: sqlite3.Connection,
    task_id: str,
    *,
    from_state: Optional[str] = None,
    to_state: Optional[str] = None,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    """Decisions for `task_id` in recorded order. `edge` is 'FROM -> TO'; `consumed` is a bool."""
    sql = (
        "SELECT decision_id, from_state, to_state, question_id, answer, decision_type, actor, "
        "recorded_at, consumed_at, bound_transition_id FROM transition_decisions WHERE task_id = ?"
    )
    params: List[Any] = [task_id]
    if from_state:
        sql += " AND from_state = ?"
        params.append(from_state)
    if to_state:
        sql += " AND to_state = ?"
        params.append(to_state)
    sql += " ORDER BY decision_id LIMIT ?"
    params.append(limit)
    return [
        {
            "decision_id": r["decision_id"],
            "edge": f"{r['from_state']} -> {r['to_state']}",
            "question_id": r["question_id"],
            "actor": r["actor"],
            "answer": r["answer"],
            "decision_type": r["decision_type"],
            "recorded_at": r["recorded_at"],
            "consumed": r["consumed_at"] is not None,
            "bound_transition_id": r["bound_transition_id"],
        }
        for r in conn.execute(sql, params).fetchall()
    ]


def inspect_candidates(conn: sqlite3.Connection, task_id: str) -> List[Dict[str, Any]]:
    """Source-assisted answer candidates for `task_id`, with their confirmation state."""
    rows = conn.execute(
        "SELECT candidate_id, stage, round_id, question_id, answer, source_path, source_authorized, "
        "confirmation_status, confirmed_by, confirmed_at FROM source_assisted_answer_candidates "
        "WHERE task_id = ? ORDER BY candidate_id",
        (task_id,),
    ).fetchall()
    return [dict(r) | {"source_authorized": bool(r["source_authorized"])} for r in rows]


def format_rows(rows: Sequence[Dict[str, Any]], columns: Sequence[str], width: int = 60) -> str:
    """A compact plain-text table (long values are truncated)."""
    if not rows:
        return "(no rows)"
    def cell(value: Any) -> str:
        text = "" if value is None else str(value)
        return text if len(text) <= width else text[: width - 1] + "…"
    table = [list(columns)] + [[cell(r.get(c)) for c in columns] for r in rows]
    widths = [max(len(row[i]) for row in table) for i in range(len(columns))]
    return "\n".join("  ".join(v.ljust(widths[i]) for i, v in enumerate(row)) for row in table)
