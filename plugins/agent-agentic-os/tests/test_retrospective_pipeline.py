"""Failing contracts for the pipeline-close retrospective gate (issue #547)."""

import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import FilesystemAdapter, SqlitePersistenceAdapter
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS, CANONICAL_STATES
from control_plane.wrappers.record_retrospective import record_retrospective
from agent_control import ControlPlane


def test_retrospective_is_a_first_class_completion_state():
    registry = TransitionRegistry.load_default()

    assert "RETROSPECTIVE" in CANONICAL_STATES
    assert "RETROSPECTIVE" in ALLOWED_TRANSITIONS["VERIFY_EXIT"]
    assert "RETROSPECTIVE" in ALLOWED_TRANSITIONS["INTAKE"]
    assert "DONE" not in ALLOWED_TRANSITIONS["VERIFY_EXIT"]
    assert "DONE" not in ALLOWED_TRANSITIONS["INTAKE"]
    assert registry.get_template("VERIFY_EXIT", "RETROSPECTIVE") is not None
    assert registry.get_template("INTAKE", "RETROSPECTIVE") is not None
    assert registry.get_template("RETROSPECTIVE", "DONE") is not None


def test_retrospective_tables_are_created(tmp_path):
    db_path = tmp_path / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()

    conn = sqlite3.connect(str(db_path))
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "retrospective_entries" in tables
        assert "retrospective_follow_ups" in tables
    finally:
        conn.close()


def test_retrospective_entry_is_unique_per_task(tmp_path):
    db_path = tmp_path / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "INSERT INTO tasks (task_id, title, state, runtime_tool) VALUES (?, ?, ?, ?)",
            ("task-547", "Reflection", "INTAKE", "codex"),
        )
        conn.execute(
            """
            INSERT INTO retrospective_entries
                (task_id, decision, completion_mode, actor, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("task-547", "opt_in", "draft", "human", 1.0, 1.0),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO retrospective_entries
                    (task_id, decision, completion_mode, actor, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("task-547", "skip", "skipped", "human", 2.0, 2.0),
            )
    finally:
        conn.close()


def test_retrospective_capture_wrapper_records_agent_completion(tmp_path):
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task("task-547-wrapper", "Reflection", "codex")
    from control_plane.coordinator import TransitionCoordinator

    TransitionCoordinator(
        control_plane=cp,
        input_fn=lambda prompt: "TRIVIAL: wrapper contract, files=1, diff=test",
    ).coordinate_transition(
        task_id="task-547-wrapper",
        to_state="RETROSPECTIVE",
        actor="human",
        reason="Enter retrospective",
        interactive=True,
    )
    result = record_retrospective(
        "task-547-wrapper",
        {
            "decision": "opt_in",
            "completion_mode": "completed",
            "actor": "agent",
            "outcome": "completed",
            "strengths": "none",
            "friction": "none",
            "learning": "none",
            "improvement": "none",
            "follow_up": "none",
        },
        [],
        control_plane=cp,
    )
    assert result["action_identity"] == "retrospective_capture"
    assert cp._persistence.has_complete_retrospective("task-547-wrapper") is True


def test_confirmed_issue_follow_up_blocks_done_until_deduped_and_created(tmp_path):
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.create_task("task-547-issue", "Reflection", "codex")
    entry = {"decision": "opt_in", "completion_mode": "completed", "actor": "human"}
    cp.save_retrospective(
        "task-547-issue",
        entry,
        [{"kind": "issue", "description": "Follow-up", "status": "confirmed"}],
    )
    assert cp._persistence.has_complete_retrospective("task-547-issue") is False

    cp.save_retrospective(
        "task-547-issue",
        entry,
        [{
            "kind": "issue",
            "description": "Follow-up",
            "status": "created",
            "duplicate_checked": True,
            "issue_url": "https://github.com/example/repo/issues/1",
        }],
    )
    assert cp._persistence.has_complete_retrospective("task-547-issue") is True
