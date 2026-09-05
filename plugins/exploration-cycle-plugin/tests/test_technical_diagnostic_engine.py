"""
test_technical_diagnostic_engine.py
Unit and integration tests for technical diagnostic brief generation,
read-only sandbox compliance, and control_plane.db task state advancement.

Purpose:
    Verifies technical_diagnostic_engine.py stays read-only, renders a valid
    DIAGNOSTIC_BRIEF.md, and correctly advances control_plane.db task state.

Key Input Dependencies:
    - ../scripts/technical_diagnostic_engine.py (module under test)
"""

import sqlite3
import pytest
from pathlib import Path
import sys

# Ensure exploration-cycle scripts are on sys.path
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from technical_diagnostic_engine import render_diagnostic_brief, sync_to_control_plane


def test_render_diagnostic_brief_contract():
    """Verify render_diagnostic_brief produces the full 4-section contract."""
    brief = render_diagnostic_brief(
        task_id="task-diag-001",
        title="Test Coupling Diagnostic",
        target_paths=["plugins/foo/bar.py", "plugins/foo/scripts/baz.py"],
        state_boundaries=["context/control_plane.db"],
        sqlite_tables=["tasks", "task_transitions"],
        cross_plugin_symlinks=["plugins/foo/skills/bar/scripts/baz.py"],
        hidden_assumptions=[
            {"assumption": "SQLite WAL active", "risk": "Lock timeouts", "mitigation": "Busy timeout"}
        ],
        candidate_forks=[
            {
                "title": "Fork 1: In-Memory Adapter",
                "description": "Zero filesystem persistence",
                "pros": ["Fast", "No leaks"],
                "cons": ["Lost on restart"]
            },
            {
                "title": "Fork 2: SQLite Control Plane",
                "description": "Persistent WAL state",
                "pros": ["Crash resilient", "Multi-process"],
                "cons": ["Requires file write"]
            }
        ]
    )

    assert "# DIAGNOSTIC BRIEF: Test Coupling Diagnostic" in brief
    assert "`task-diag-001`" in brief
    assert "READ_ONLY_SANDBOX" in brief
    assert "## 1. Coupling Surface" in brief
    assert "`plugins/foo/bar.py`" in brief
    assert "## 2. Hidden Assumptions & Omissions" in brief
    assert "SQLite WAL active" in brief
    assert "## 3. Candidate Architectural Forks" in brief
    assert "Fork 1: In-Memory Adapter" in brief
    assert "Fork 2: SQLite Control Plane" in brief
    assert "## 4. Handoff Contract to `interview-spec`" in brief
    assert "INTAKE` -> `INTERVIEW" in brief


def test_sync_to_control_plane_advances_state(tmp_path):
    """Verify sync_to_control_plane updates task to INTERVIEW in control_plane.db."""
    db_file = tmp_path / "control_plane.db"
    
    # Initialize minimal schema
    conn = sqlite3.connect(str(db_file))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("""
    CREATE TABLE tasks (
        task_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        state TEXT NOT NULL,
        runtime_tool TEXT NOT NULL,
        worktree_path TEXT,
        worktree_branch TEXT,
        worktree_state TEXT,
        spec_path TEXT,
        model_tier TEXT,
        model_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.execute("""
    CREATE TABLE task_transitions (
        transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id TEXT NOT NULL REFERENCES tasks(task_id),
        from_state TEXT NOT NULL,
        to_state TEXT NOT NULL,
        actor TEXT NOT NULL,
        reason TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

    task_id = "task-sync-100"
    brief_path = str(tmp_path / "DIAGNOSTIC_BRIEF.md")

    # Sync to control plane
    res = sync_to_control_plane(
        task_id=task_id,
        title="Sync Test",
        brief_path=brief_path,
        db_path=db_file,
        runtime_tool="claude"
    )
    assert res is True

    # Verify task state in database
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    task = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    assert task["state"] == "INTERVIEW"
    assert task["spec_path"] == brief_path

    # Verify transition log
    transitions = conn.execute("SELECT * FROM task_transitions WHERE task_id = ?", (task_id,)).fetchall()
    assert len(transitions) == 2
    assert transitions[0]["from_state"] == "NONE"
    assert transitions[0]["to_state"] == "INTAKE"
    assert transitions[1]["from_state"] == "INTAKE"
    assert transitions[1]["to_state"] == "INTERVIEW"
    conn.close()


def test_read_only_diagnostic_does_not_mutate_workspace(tmp_path):
    """Verify generating a diagnostic brief only writes to designated output."""
    workspace_file = tmp_path / "repo_code.py"
    workspace_file.write_text("ORIGINAL_CONTENT = True\n", encoding="utf-8")
    
    output_brief = tmp_path / "exploration" / "DIAGNOSTIC_BRIEF.md"
    output_brief.parent.mkdir(parents=True, exist_ok=True)

    content = render_diagnostic_brief(
        task_id="task-ro-1",
        title="Read-Only Verification",
        target_paths=[str(workspace_file)],
        state_boundaries=[],
        sqlite_tables=[],
        cross_plugin_symlinks=[],
        hidden_assumptions=[],
        candidate_forks=[]
    )
    output_brief.write_text(content, encoding="utf-8")

    # Verify target workspace file was untouched
    assert workspace_file.read_text(encoding="utf-8") == "ORIGINAL_CONTENT = True\n"
    assert output_brief.exists()
    assert "READ_ONLY_SANDBOX" in output_brief.read_text(encoding="utf-8")
