"""Behavioral and parity integration tests for Exploration Cycle onto Agentic OS execution substrate.

Tests the programmatic exploration session adapter, substrate readiness check,
lifecycle boundaries, phase progression, gate validation, re-entry resumption,
authoritative SQLite persistence over JSON projection, fail-closed persistence behavior,
and absence of legacy prompt-based dashboard intercept boilerplate across exploration skills.
"""

from pathlib import Path
import json
import pytest
import sys
import sqlite3

# Ensure exploration-cycle-plugin and agent-agentic-os scripts are importable
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
EXPLORATION_SCRIPTS = PLUGIN_ROOT / "scripts"
AGENTIC_OS_SCRIPTS = REPO_ROOT / "plugins" / "agent-agentic-os" / "scripts"

for p in (str(EXPLORATION_SCRIPTS), str(AGENTIC_OS_SCRIPTS)):
    if p not in sys.path:
        sys.path.insert(0, p)

from exploration_session import (  # type: ignore
    check_substrate_readiness,
    get_exploration_session,
    create_exploration_session,
    advance_exploration_phase,
    enforce_lifecycle_context,
    LifecycleContextError,
    VALID_EXPLORATION_LIFECYCLE_STATES,
    EXPLORATION_PHASES,
)
from agent_control import ControlPlane  # type: ignore


def _set_test_task_state_for_testing(cp: ControlPlane, task_id: str, state: str) -> None:
    """Test fixture helper to inject a task state for testing negative/disallowed lifecycle boundaries.

    Encapsulated at the test fixture boundary so tests avoid ad-hoc schema manipulation.
    """
    conn = cp._persistence.get_connection()
    try:
        with conn:
            conn.execute("DROP TRIGGER IF EXISTS enforce_valid_transition")
            conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (state, task_id))
    finally:
        conn.close()


def _setup_test_control_plane(tmp_path: Path, task_id: str, state: str = "INTAKE") -> Path:
    """Helper to set up an initialized control plane with a task in the specified state."""
    db_path = tmp_path / "context" / "control_plane.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    cp.create_task(task_id, f"Test Task {task_id}", "general")
    if state != "INTAKE":
        _set_test_task_state_for_testing(cp, task_id, state)
    return db_path


def test_readiness_routing_uninitialized(tmp_path):
    """Missing or partial substrate must cleanly route to os-init."""
    ready, message = check_substrate_readiness(tmp_path)
    assert not ready
    assert "os-init" in message.lower()
    assert "substrate is not initialized" in message.lower()


def test_readiness_initialized(tmp_path):
    """Fully initialized substrate must report ready."""
    from control_plane.adapters import CURRENT_SCHEMA_VERSION, LEGAL_INITIAL_STATES  # type: ignore
    from control_plane.state_machine import ALLOWED_TRANSITIONS  # type: ignore

    for rel in (
        ".claude/hooks/hooks.json",
        ".git/hooks/pre-commit-evolution-guard",
        ".github/workflows/verify-evolution-integrity.yml",
    ):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("managed", encoding="utf-8")

    db_path = tmp_path / "context" / "control_plane.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE schema_version (version INTEGER NOT NULL)")
    conn.execute("INSERT INTO schema_version VALUES (?)", (CURRENT_SCHEMA_VERSION,))
    conn.execute("CREATE TABLE valid_transitions (from_state TEXT, to_state TEXT)")
    transitions = [
        (source, target)
        for source, targets in ALLOWED_TRANSITIONS.items()
        for target in targets
    ] + [(None, s) for s in LEGAL_INITIAL_STATES]
    conn.executemany("INSERT INTO valid_transitions VALUES (?, ?)", transitions)
    conn.execute(
        "CREATE TRIGGER enforce_valid_transition AFTER INSERT ON schema_version BEGIN SELECT 1; END"
    )
    conn.commit()
    conn.close()

    ready, message = check_substrate_readiness(tmp_path)
    assert ready
    assert message == ""


def test_lifecycle_context_enforcement():
    """Exploration sessions are permitted strictly within exploratory lifecycle states."""
    assert set(VALID_EXPLORATION_LIFECYCLE_STATES) == {"INTAKE", "INTERVIEW", "DRAFT_PLAN"}
    assert "EXPLORATION" not in VALID_EXPLORATION_LIFECYCLE_STATES

    # Disallowed engineering/execution states
    disallowed = ("IN_WORKTREE", "IMPLEMENTATION", "CODE_REVIEW", "COMPLETED", "EXPLORATION")
    for state in disallowed:
        assert state not in VALID_EXPLORATION_LIFECYCLE_STATES


def test_stale_json_ignored_when_authoritative_ledger_has_no_record(tmp_path):
    """Authoritative lookup returns no record + stale JSON exists on disk -> get_exploration_session returns None.

    Prevents stale JSON projection on disk from being promoted to authoritative session state.
    """
    task_id = "test-task-no-ledger-rec"
    db_path = _setup_test_control_plane(tmp_path, task_id, state="INTAKE")
    session_file = tmp_path / "context" / "exploration_session.json"

    # Create stale JSON projection on disk for this task_id, but write NOTHING to SQLite
    stale_data = {
        "session_id": f"exp-{task_id}",
        "task_id": task_id,
        "active_phase": "1-discovery",
        "phase_state": "STALE_PROJECTION",
    }
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(json.dumps(stale_data), encoding="utf-8")

    # Authoritative ledger query must be definitive: no record in SQLite -> returns None
    retrieved = get_exploration_session(task_id=task_id, storage_path=session_file, db_path=db_path)
    assert retrieved is None, "Stale JSON projection must not be promoted to authority when ledger has no record"


def test_authoritative_read_failure_fails_closed_and_rejects_stale_json(tmp_path, monkeypatch):
    """Authoritative read error -> get_exploration_session raises/fails closed -> stale JSON is NEVER returned."""
    task_id = "test-task-read-err"
    db_path = _setup_test_control_plane(tmp_path, task_id, state="INTAKE")
    session_file = tmp_path / "context" / "exploration_session.json"

    # Create stale JSON projection on disk
    stale_data = {
        "session_id": f"exp-{task_id}",
        "task_id": task_id,
        "active_phase": "1-discovery",
        "phase_state": "STALE_PROJECTION",
    }
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(json.dumps(stale_data), encoding="utf-8")

    cp = ControlPlane(db_path=db_path)

    def failing_read(*args, **kwargs):
        raise sqlite3.OperationalError("Simulated database lock or I/O failure during authoritative read")

    monkeypatch.setattr(cp._persistence, "get_latest_asymmetric_persistence", failing_read)

    import exploration_session
    monkeypatch.setattr(exploration_session, "get_control_plane", lambda db_path=None: cp)

    # Must fail closed: raise exception rather than swallowing and falling back to stale JSON
    with pytest.raises(sqlite3.OperationalError):
        get_exploration_session(task_id=task_id, storage_path=session_file, db_path=db_path)


def test_lifecycle_context_enforcement_denies_disallowed_states(tmp_path):
    """Proves an actual disallowed OS state cannot create or advance exploration session state."""
    task_id = "test-task-in-worktree"
    db_path = _setup_test_control_plane(tmp_path, task_id, state="IN_WORKTREE")
    session_file = tmp_path / "context" / "exploration_session.json"

    # Creation in disallowed state must raise LifecycleContextError
    with pytest.raises(LifecycleContextError) as exc_info:
        create_exploration_session(
            task_id=task_id,
            storage_path=session_file,
            db_path=db_path,
        )
    assert "IN_WORKTREE" in str(exc_info.value)
    assert "not permitted" in str(exc_info.value).lower()
    assert not session_file.exists()

    # Advancement in disallowed state must also raise LifecycleContextError
    with pytest.raises(LifecycleContextError) as exc_info:
        advance_exploration_phase(
            task_id=task_id,
            target_phase="2-requirements",
            storage_path=session_file,
            db_path=db_path,
        )
    assert "IN_WORKTREE" in str(exc_info.value)


def test_authoritative_persistence_failure_fails_closed(tmp_path, monkeypatch):
    """If authoritative persistence fails, it must fail closed and NOT write/mutate JSON projection."""
    task_id = "test-task-fail-closed"
    db_path = _setup_test_control_plane(tmp_path, task_id, state="INTAKE")
    session_file = tmp_path / "context" / "exploration_session.json"

    cp = ControlPlane(db_path=db_path)

    def failing_persistence(*args, **kwargs):
        raise sqlite3.OperationalError("Simulated disk error during authoritative write")

    monkeypatch.setattr(cp._persistence, "insert_asymmetric_persistence", failing_persistence)

    # Patch get_control_plane to return our failing instance
    import exploration_session
    monkeypatch.setattr(exploration_session, "get_control_plane", lambda db_path=None: cp)

    with pytest.raises(sqlite3.OperationalError):
        create_exploration_session(
            task_id=task_id,
            storage_path=session_file,
            db_path=db_path,
        )

    # Crucial assertion: JSON projection must NOT have been written
    assert not session_file.exists()


def test_session_persistence_and_retrieval(tmp_path):
    """Session creation persists derived JSON projection and retrieves active session."""
    task_id = "test-task-123"
    db_path = _setup_test_control_plane(tmp_path, task_id, state="INTAKE")
    session_file = tmp_path / "context" / "exploration_session.json"

    session = create_exploration_session(
        task_id=task_id,
        session_type="greenfield",
        storage_path=session_file,
        db_path=db_path,
    )

    assert session["task_id"] == task_id
    assert session["active_phase"] == "1-discovery"
    assert session["phase_state"] == "IN_PROGRESS"
    assert session_file.exists()

    retrieved = get_exploration_session(task_id=task_id, storage_path=session_file, db_path=db_path)
    assert retrieved is not None
    assert retrieved["session_id"] == session["session_id"]
    assert retrieved["active_phase"] == "1-discovery"


def test_phase_progression_and_hard_gate(tmp_path):
    """Phase progression validates prerequisites before moving to prototyping."""
    task_id = "test-task-progression"
    db_path = _setup_test_control_plane(tmp_path, task_id, state="INTERVIEW")
    session_file = tmp_path / "context" / "exploration_session.json"

    create_exploration_session(
        task_id=task_id,
        session_type="greenfield",
        storage_path=session_file,
        db_path=db_path,
    )

    # 1-discovery -> 2-requirements is allowed
    success, msg = advance_exploration_phase(
        task_id=task_id,
        target_phase="2-requirements",
        storage_path=session_file,
        db_path=db_path,
    )
    assert success

    # 2-requirements -> 3-prototyping requires approved_plan=True
    success, msg = advance_exploration_phase(
        task_id=task_id,
        target_phase="3-prototyping",
        storage_path=session_file,
        approved_plan=False,
        db_path=db_path,
    )
    assert not success
    assert "approved plan" in msg.lower()

    # Now approve plan and advance
    success, msg = advance_exploration_phase(
        task_id=task_id,
        target_phase="3-prototyping",
        storage_path=session_file,
        approved_plan=True,
        db_path=db_path,
    )
    assert success
    session = get_exploration_session(task_id=task_id, storage_path=session_file, db_path=db_path)
    assert session["active_phase"] == "3-prototyping"
    assert session["approved_plan"] is True


def test_sqlite_ledger_authoritative_over_json_projection(tmp_path):
    """Asserts that Agentic OS SQLite persistence is the single authoritative source of truth.

    If the JSON projection file is corrupted, drifted, or deleted, get_exploration_session
    retrieves the authoritative SQLite state and repairs the projection file.
    """
    task_id = "test-authoritative-task"
    db_path = _setup_test_control_plane(tmp_path, task_id, state="DRAFT_PLAN")
    session_file = tmp_path / "context" / "exploration_session.json"

    # 1. Create session with authoritative SQLite backing
    create_exploration_session(
        task_id=task_id,
        session_type="spike",
        storage_path=session_file,
        db_path=db_path,
    )

    # 2. Advance phase authoritatively
    advance_exploration_phase(
        task_id=task_id,
        target_phase="2-requirements",
        storage_path=session_file,
        db_path=db_path,
    )

    # 3. Simulate drift / corruption in the JSON projection file
    corrupted_data = {
        "session_id": f"exp-{task_id}",
        "task_id": task_id,
        "session_type": "spike",
        "active_phase": "DRIFTED_OLD_PHASE",
        "phase_state": "CORRUPTED",
    }
    session_file.write_text(json.dumps(corrupted_data), encoding="utf-8")

    # 4. Read session: SQLite must take precedence and repair the JSON projection
    retrieved = get_exploration_session(task_id=task_id, storage_path=session_file, db_path=db_path)
    assert retrieved is not None
    assert retrieved["active_phase"] == "2-requirements", (
        f"Expected authoritative phase '2-requirements', got '{retrieved['active_phase']}'"
    )

    # Verify JSON projection was repaired on disk
    repaired_json = json.loads(session_file.read_text(encoding="utf-8"))
    assert repaired_json["active_phase"] == "2-requirements"


def test_absence_of_legacy_dashboard_boilerplate_across_skills():
    """Asserts removal of legacy prompt-orchestration boilerplate while preserving cognitive intelligence."""
    skills_dir = PLUGIN_ROOT / "skills"
    candidate_names = (
        "discovery-planning",
        "exploration-handoff",
        "subagent-driven-prototyping",
        "visual-companion",
        "exploration-workflow",
    )

    discovered = []
    for name in candidate_names:
        skill_file = skills_dir / name / "SKILL.md"
        if skill_file.exists():
            discovered.append(skill_file.resolve())

    # Anti-vacuity check
    assert len(discovered) >= 4, f"Expected at least 4 exploration skills, found {len(discovered)}"

    legacy_boilerplate_markers = [
        "## Dashboard Intercept",
        "<ORCHESTRATOR_DISPATCH>",
    ]

    for skill_path in discovered:
        content = skill_path.read_text(encoding="utf-8")
        for marker in legacy_boilerplate_markers:
            assert marker not in content, (
                f"Legacy boilerplate marker '{marker}' still present in {skill_path.relative_to(REPO_ROOT)}"
            )

        # Cognitive intelligence preservation check
        assert len(content.splitlines()) >= 30, (
            f"Skill {skill_path.relative_to(REPO_ROOT)} was truncated below cognitive threshold"
        )
