"""
test_human_decision_trigger_enforcement.py
===========================================

Deterministic TDD test suite validating the second-layer database trigger enforcement:
1. Replicates the exact live bypass: programmatic self-approval with actor="human"
   without real interactive stdin pause, confirming it gets rejected at the DB level.
2. Parity test: asserts set-equality between registry edges with human_questions and
   edges verified by the test matrix (fails CI if new question edge added to YAML without test).
3. Full Matrix Coverage across all 52 edges in ALLOWED_TRANSITIONS:
   - 36 deterministic-only edges: confirmed unaffected by question trigger.
   - 16 human-question edges: each tested across 5 discrete permutations:
     * Valid: actor='human', matching question_id, non-empty answer -> SUCCEEDS.
     * Invalid 1: zero decision rows -> REJECTED & LOGGED.
     * Invalid 2: actor='agent' (synthetic/agent bypass) -> REJECTED & LOGGED.
     * Invalid 3: wrong question_id -> REJECTED & LOGGED.
     * Invalid 4: null/empty answer -> REJECTED & LOGGED.
"""

import sys
from pathlib import Path
import pytest
import sqlite3

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import SqlitePersistenceAdapter, FilesystemAdapter, SCHEMA_SQL, _split_schema_sql_statements
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS
from agent_control import ControlPlane, PersistenceInvariantViolation, ConcurrentModificationError
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError


@pytest.fixture
def test_env(tmp_path):
    db_path = tmp_path / "context" / "control_plane.db"
    adapter = SqlitePersistenceAdapter(db_path, FilesystemAdapter())
    adapter.ensure_schema()
    cp = ControlPlane(db_path=db_path, persistence_adapter=adapter)
    return {"db_path": db_path, "adapter": adapter, "cp": cp, "tmp_path": tmp_path}


def _seed_task_at_state(conn, task_id, state):
    """Directly sets a task row at a given state with clean transition history,
    bypassing triggers during test fixture setup, and recreates the exact production triggers
    from SCHEMA_SQL (eliminating any test/production DDL divergence)."""
    conn.execute("DROP TRIGGER IF EXISTS enforce_valid_initial_state;")
    conn.execute("DROP TRIGGER IF EXISTS enforce_valid_transition;")
    conn.execute("INSERT OR REPLACE INTO tasks (task_id, title, state, task_type, runtime_tool) VALUES (?, ?, ?, 'GENERAL', 'claude')",
                 (task_id, f"Task {task_id}", state))
    conn.execute("INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason) VALUES (?, 'NONE', ?, 'system', 'fixture')",
                 (task_id, state))
    conn.commit()
    # Recreate production triggers directly from SCHEMA_SQL
    for stmt in _split_schema_sql_statements(SCHEMA_SQL):
        if "CREATE TRIGGER" in stmt.upper():
            conn.execute(stmt)
    conn.commit()


def test_valid_transitions_table_matches_registry(test_env):
    """Verifies that the valid_transitions and required_transition_questions tables
    in SQLite are dynamically synchronized with TransitionRegistry."""
    db_path = test_env["db_path"]
    reg = TransitionRegistry.load_default()
    conn = sqlite3.connect(db_path)

    # 1. Compare valid_transitions table
    db_transitions = {
        (r[0], r[1]) for r in conn.execute(
            "SELECT from_state, to_state FROM valid_transitions WHERE from_state IS NOT NULL"
        ).fetchall()
    }
    registry_transitions = set(reg._templates_by_edge.keys())
    assert db_transitions == registry_transitions, "valid_transitions table must match registry transitions"

    # 2. Compare required_transition_questions table
    db_questions = {
        (r[0], r[1], r[2]) for r in conn.execute(
            "SELECT from_state, to_state, question_id FROM required_transition_questions"
        ).fetchall()
    }
    expected_questions = {
        (edge[0], edge[1], q["question_id"])
        for edge, tmpl in reg._templates_by_edge.items()
        for q in tmpl.human_questions
    } | {
        (edge[0], edge[1], question_id)
        for edge, tmpl in reg._templates_by_edge.items()
        for question_id in (tmpl.stage_question_ids or [])
    } | {
        (edge[0], edge[1], f"approval_{tmpl.transition_id}")
        for edge, tmpl in reg._templates_by_edge.items()
        if tmpl.approval.get("required") and tmpl.approval.get("approver_role", "human") == "human"
    }
    assert db_questions == expected_questions, "required_transition_questions table must match registry questions and approvals"
    conn.close()


def test_all_deterministic_edges_from_valid_transitions_table(test_env):
    """Dynamically tests ALL deterministic edges directly queried from the valid_transitions table.
    Any edge present in valid_transitions without entries in required_transition_questions
    is verified to transition smoothly without requiring decision rows.
    If new valid state transitions are added to the table, they are tested automatically
    without modifying this test suite."""
    db_path = test_env["db_path"]
    conn = sqlite3.connect(db_path)

    deterministic_edges = conn.execute("""
        SELECT vt.from_state, vt.to_state
        FROM valid_transitions vt
        WHERE vt.from_state IS NOT NULL
          AND NOT EXISTS (
              SELECT 1 FROM required_transition_questions rq
              WHERE rq.from_state = vt.from_state AND rq.to_state = vt.to_state
          )
        ORDER BY vt.from_state, vt.to_state
    """).fetchall()
    assert len(deterministic_edges) > 0, "Source table empty or unsynced: valid_transitions has 0 deterministic edges"
    assert len(deterministic_edges) >= 30, f"Expected at least 30 deterministic edges in valid_transitions, got {len(deterministic_edges)}"

    tested_edges = 0
    for idx, (from_s, to_s) in enumerate(deterministic_edges):
        tested_edges += 1
        task_id = f"task-det-{idx:03d}"
        _seed_task_at_state(conn, task_id, from_s)

        # Update to to_s via raw SQL
        conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, task_id))
        conn.commit()

        row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        assert row[0] == to_s, f"Deterministic edge {from_s} -> {to_s} from valid_transitions must not be blocked by question trigger!"

        # Assert no violation was logged
        v = conn.execute(
            "SELECT COUNT(*) FROM transition_violations WHERE task_id = ? AND attempted_from_state = ? AND attempted_to_state = ?",
            (task_id, from_s, to_s)
        ).fetchone()[0]
        assert v == 0, f"No violation should be logged for valid deterministic edge {from_s} -> {to_s}"

    assert tested_edges == len(deterministic_edges)
    assert tested_edges > 0, "Zero deterministic edges were executed"
    conn.close()


def test_all_question_edges_from_valid_transitions_table(test_env):
    """Dynamically tests ALL question-requiring edges directly queried from SQLite tables.
    For every edge in valid_transitions that has required_transition_questions,
    tests all 5 permutations dynamically:
    1. Zero decision rows -> REJECTED & LOGGED
    2. actor='agent' (synthetic bypass) -> REJECTED & LOGGED
    3. Wrong question_id -> REJECTED & LOGGED
    4. Empty/null answer -> REJECTED & LOGGED
    5. actor='human', matching question_id, non-empty answer -> SUCCEEDS
    If transitions or questions are added or adjusted, this test suite requires zero changes."""
    db_path = test_env["db_path"]
    conn = sqlite3.connect(db_path)

    question_edges = conn.execute("""
        SELECT DISTINCT vt.from_state, vt.to_state
        FROM valid_transitions vt
        JOIN required_transition_questions rq
          ON vt.from_state = rq.from_state AND vt.to_state = rq.to_state
        ORDER BY vt.from_state, vt.to_state
    """).fetchall()
    assert len(question_edges) > 0, "Source table empty or unsynced: valid_transitions has 0 question edges"
    assert len(question_edges) >= 15, f"Expected at least 15 question edges in valid_transitions, got {len(question_edges)}"

    tested_question_edges = 0
    for from_s, to_s in question_edges:
        tested_question_edges += 1
        required_qids = [
            r[0] for r in conn.execute(
                "SELECT question_id FROM required_transition_questions WHERE from_state = ? AND to_state = ?",
                (from_s, to_s)
            ).fetchall()
        ]
        assert len(required_qids) > 0, f"Question edge {from_s} -> {to_s} has 0 required questions in required_transition_questions"

        # Permutation 1: Zero decision rows -> REJECTED
        t1 = f"t1-{from_s}-{to_s}"
        _seed_task_at_state(conn, t1, from_s)
        conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, t1))
        conn.commit()
        assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (t1,)).fetchone()[0] == from_s
        assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (t1,)).fetchone()[0] >= 1

        # Permutation 2: actor='agent' (synthetic agent bypass) -> REJECTED, except for
        # the retrospective decision gate, which explicitly permits either actor.
        t2 = f"t2-{from_s}-{to_s}"
        _seed_task_at_state(conn, t2, from_s)
        for qid in required_qids:
            conn.execute(
                """
                INSERT INTO transition_decisions (
                    task_id, source_occupancy_transition_id, from_state, to_state,
                    question_id, answer, decision_type, actor, recorded_at
                ) VALUES (?, 1, ?, ?, ?, 'Agent answer', 'ANSWER', 'agent', 12345.0)
                """,
                (t2, from_s, to_s, qid)
            )
        conn.commit()
        conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, t2))
        conn.commit()
        if (from_s, to_s) == ("RETROSPECTIVE", "DONE") and "retrospective_decision" in required_qids:
            assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (t2,)).fetchone()[0] == to_s
        else:
            assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (t2,)).fetchone()[0] == from_s
            assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (t2,)).fetchone()[0] >= 1

        # Permutation 3: Wrong question_id -> REJECTED
        t3 = f"t3-{from_s}-{to_s}"
        _seed_task_at_state(conn, t3, from_s)
        conn.execute(
            """
            INSERT INTO transition_decisions (
                task_id, source_occupancy_transition_id, from_state, to_state,
                question_id, answer, decision_type, actor, recorded_at
            ) VALUES (?, 1, ?, ?, 'totally_wrong_question_id', 'Human answer', 'ANSWER', 'human', 12345.0)
            """,
            (t3, from_s, to_s)
        )
        conn.commit()
        conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, t3))
        conn.commit()
        assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (t3,)).fetchone()[0] == from_s
        assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (t3,)).fetchone()[0] >= 1

        # Permutation 4: Empty answer -> REJECTED
        t4 = f"t4-{from_s}-{to_s}"
        _seed_task_at_state(conn, t4, from_s)
        for qid in required_qids:
            conn.execute(
                """
                INSERT INTO transition_decisions (
                    task_id, source_occupancy_transition_id, from_state, to_state,
                    question_id, answer, decision_type, actor, recorded_at
                ) VALUES (?, 1, ?, ?, ?, '   ', 'ANSWER', 'human', 12345.0)
                """,
                (t4, from_s, to_s, qid)
            )
        conn.commit()
        conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, t4))
        conn.commit()
        assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (t4,)).fetchone()[0] == from_s
        assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (t4,)).fetchone()[0] >= 1

        # Permutation 5: Valid human decision for ALL required questions -> SUCCEEDS
        t5 = f"t5-{from_s}-{to_s}"
        _seed_task_at_state(conn, t5, from_s)
        for qid in required_qids:
            conn.execute(
                """
                INSERT INTO transition_decisions (
                    task_id, source_occupancy_transition_id, from_state, to_state,
                    question_id, answer, decision_type, actor, recorded_at
                ) VALUES (?, 1, ?, ?, ?, 'Valid Human Answer', 'ANSWER', 'human', 12345.0)
                """,
                (t5, from_s, to_s, qid)
            )
        conn.commit()
        conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, t5))
        conn.commit()
        assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (t5,)).fetchone()[0] == to_s, \
            f"Valid human decision must allow {from_s} -> {to_s} to commit!"

    assert tested_question_edges == len(question_edges)
    assert tested_question_edges > 0, "Zero question edges were executed"
    conn.close()


def test_dynamically_added_transitions_enforced_without_test_suite_changes(test_env):
    """Verifies that when new transitions are inserted into the valid_transitions table
    (and optional required_transition_questions), the database trigger enforces them
    automatically without requiring any modifications to the test suite."""
    db_path = test_env["db_path"]
    conn = sqlite3.connect(db_path)

    # 1. Dynamically add a new deterministic transition: VERIFY_EXIT -> DRAFT_PLAN
    conn.execute("INSERT INTO valid_transitions (from_state, to_state) VALUES ('VERIFY_EXIT', 'DRAFT_PLAN')")
    conn.commit()

    task_det = "task-dyn-det-01"
    _seed_task_at_state(conn, task_det, "VERIFY_EXIT")
    conn.execute("UPDATE tasks SET state = 'DRAFT_PLAN' WHERE task_id = ?", (task_det,))
    conn.commit()
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_det,)).fetchone()[0] == "DRAFT_PLAN"
    assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (task_det,)).fetchone()[0] == 0

    # 2. Dynamically add a new question-required transition: VERIFY_EXIT -> APPROVED
    conn.execute("INSERT INTO valid_transitions (from_state, to_state) VALUES ('VERIFY_EXIT', 'APPROVED')")
    conn.execute("INSERT INTO required_transition_questions (from_state, to_state, question_id) VALUES ('VERIFY_EXIT', 'APPROVED', 'q_dynamic_approval')")
    conn.commit()

    task_q = "task-dyn-q-01"
    _seed_task_at_state(conn, task_q, "VERIFY_EXIT")

    # Attempt transition with no decision -> REJECTED
    conn.execute("UPDATE tasks SET state = 'APPROVED' WHERE task_id = ?", (task_q,))
    conn.commit()
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_q,)).fetchone()[0] == "VERIFY_EXIT"
    assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (task_q,)).fetchone()[0] >= 1

    # Attempt transition with actor='agent' -> REJECTED
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at
        ) VALUES (?, 1, 'VERIFY_EXIT', 'APPROVED', 'q_dynamic_approval', 'agent bypass', 'ANSWER', 'agent', 12345.0)
        """,
        (task_q,)
    )
    conn.commit()
    conn.execute("UPDATE tasks SET state = 'APPROVED' WHERE task_id = ?", (task_q,))
    conn.commit()
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_q,)).fetchone()[0] == "VERIFY_EXIT"

    # Provide valid human decision -> SUCCEEDS
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at
        ) VALUES (?, 1, 'VERIFY_EXIT', 'APPROVED', 'q_dynamic_approval', 'human approval confirmed', 'ANSWER', 'human', 12345.0)
        """,
        (task_q,)
    )
    conn.commit()
    conn.execute("UPDATE tasks SET state = 'APPROVED' WHERE task_id = ?", (task_q,))
    conn.commit()
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_q,)).fetchone()[0] == "APPROVED"

    # 3. Invalid transition not in valid_transitions table: VERIFY_EXIT -> MULTI_AGENT_REVIEW -> REJECTED
    task_inv = "task-dyn-inv-01"
    _seed_task_at_state(conn, task_inv, "VERIFY_EXIT")
    conn.execute("UPDATE tasks SET state = 'MULTI_AGENT_REVIEW' WHERE task_id = ?", (task_inv,))
    conn.commit()
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_inv,)).fetchone()[0] == "VERIFY_EXIT"
    assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (task_inv,)).fetchone()[0] >= 1

    conn.close()


def test_reproduce_live_self_approval_bypass_rejected(test_env):
    """Slice: Literal reproduction of the live bypass.
    An agent programmatically executes record-human-approval / transition to APPROVED
    with actor='human' but without genuine interactive stdin input.
    The database trigger MUST reject the transition, restore AWAITING_APPROVAL,
    and record a violation in transition_violations.
    """
    cp = test_env["cp"]
    db_path = test_env["db_path"]
    task_id = "task-repro-bypass-001"

    # Setup task at AWAITING_APPROVAL
    conn = sqlite3.connect(db_path)
    _seed_task_at_state(conn, task_id, "AWAITING_APPROVAL")

    row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    assert row[0] == "AWAITING_APPROVAL"

    # ATTEMPT 1: Raw SQL UPDATE bypassing coordinator with zero decisions recorded
    conn.execute("UPDATE tasks SET state = 'APPROVED' WHERE task_id = ?", (task_id,))
    conn.commit()

    # Verify that database trigger silently reverted state and logged violation
    row_after_raw = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    assert row_after_raw[0] == "AWAITING_APPROVAL", "Raw SQL update to APPROVED without decision must be reverted by trigger!"

    violations = conn.execute(
        "SELECT task_id, attempted_from_state, attempted_to_state FROM transition_violations WHERE task_id = ?",
        (task_id,)
    ).fetchall()
    assert len(violations) >= 1
    assert violations[-1] == (task_id, "AWAITING_APPROVAL", "APPROVED")

    # ATTEMPT 2: Programmatic cp.transition call with actor='human' without recorded human decision
    with pytest.raises((PersistenceInvariantViolation, ConcurrentModificationError)):
        cp.transition(task_id, "APPROVED", actor="human", reason="Self-approved without decision row")

    row_after_call = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    assert row_after_call[0] == "AWAITING_APPROVAL"

    # ATTEMPT 3: Non-interactive coordinate_transition passing programmatic answers dict
    reg = TransitionRegistry.load_default()
    coord = TransitionCoordinator(control_plane=cp, registry=reg)

    with pytest.raises((TransitionCoordinatorError, PersistenceInvariantViolation)):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="APPROVED",
            actor="human",
            reason="Synthetic approval",
            interactive=False,
            provided_answers={"human_implementation_approval": "Yes, approve implementation [Recommended]"},
            approval_decision="APPROVAL"
        )

    row_after_coord = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    assert row_after_coord[0] == "AWAITING_APPROVAL"
    conn.close()


def test_interactive_coordinator_prompts_and_succeeds_with_human_decision(test_env):
    """Slice: Interactive coordinator session with genuine stdin input.
    When interactive=True and input_fn provides the selection, decision is recorded
    with actor='human' and database trigger allows transition to commit."""
    cp = test_env["cp"]
    db_path = test_env["db_path"]
    task_id = "task-interactive-success-003"
    conn = sqlite3.connect(db_path)
    _seed_task_at_state(conn, task_id, "AWAITING_APPROVAL")
    conn.close()

    reg = TransitionRegistry.load_default()
    # Mock interactive stdin input selecting option 1 ("Yes, approve implementation")
    # and approving the transition ("y")
    inputs = iter(["1", "y"])
    coord = TransitionCoordinator(control_plane=cp, registry=reg, input_fn=lambda prompt: next(inputs))

    record = coord.coordinate_transition(
        task_id=task_id,
        to_state="APPROVED",
        actor="human",
        reason="Interactive approval from human",
        interactive=True
    )
    assert record.to_state == "APPROVED"

    conn = sqlite3.connect(db_path)
    state = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0]
    assert state == "APPROVED"

    # Verify decision rows exist with actor='human'
    decisions = conn.execute(
        "SELECT question_id, actor, answer FROM transition_decisions WHERE task_id = ? AND to_state = 'APPROVED'",
        (task_id,)
    ).fetchall()
    assert len(decisions) >= 1
    for qid, actor, ans in decisions:
        assert actor == "human"
        assert ans != ""
    conn.close()


def test_schema_rebuild_preserves_augmented_trigger_and_required_questions(test_env):
    """Slice: Verifies that _rebuild_schema_transactional drops and recreates the
    augmented trigger cleanly without trigger loss or schema drift (Issue #552 parity)."""
    db_path = test_env["db_path"]
    adapter = test_env["adapter"]
    conn = adapter.get_connection()

    # Force a schema rebuild
    adapter._rebuild_schema_transactional(conn)
    adapter._sync_valid_transitions(conn)

    # Verify table and trigger exist
    req_q_count = conn.execute("SELECT COUNT(*) FROM required_transition_questions").fetchone()[0]
    assert req_q_count > 0, "required_transition_questions must be populated after rebuild"

    triggers = conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='trigger' AND name='enforce_valid_transition'"
    ).fetchone()
    assert triggers is not None
    assert "required_transition_questions" in triggers[1]
    conn.close()


def test_approval_only_edge_rejects_forged_agent_approval(test_env):
    """Regression test (a): An edge with approval.required=True and no human_questions.
    Confirms a forged actor='agent' APPROVAL decision is rejected by the database trigger,
    and only an actor='human' APPROVAL decision is allowed to commit."""
    db_path = test_env["db_path"]
    conn = sqlite3.connect(db_path)

    from_s, to_s = "VERIFY_EXIT", "APPROVED"
    approval_qid = "approval_verify_exit_to_approved"

    # Seed transition in valid_transitions and required_transition_questions without human_questions
    conn.execute("INSERT INTO valid_transitions (from_state, to_state) VALUES (?, ?)", (from_s, to_s))
    conn.execute("INSERT INTO required_transition_questions (from_state, to_state, question_id) VALUES (?, ?, ?)",
                 (from_s, to_s, approval_qid))
    conn.commit()

    task_id = "task-approval-only-001"
    _seed_task_at_state(conn, task_id, from_s)

    # 1. Attempt transition with actor='agent' APPROVAL decision -> MUST BE REJECTED
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at
        ) VALUES (?, 1, ?, ?, ?, 'APPROVAL', 'APPROVAL', 'agent', 12345.0)
        """,
        (task_id, from_s, to_s, approval_qid)
    )
    conn.commit()
    conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, task_id))
    conn.commit()

    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0] == from_s
    violations = conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", (task_id,)).fetchone()[0]
    assert violations >= 1, "Violations must be logged when actor='agent' attempts approval-gated transition"

    # 2. Attempt transition with actor='human' APPROVAL decision -> SUCCEEDS
    conn.execute(
        """
        INSERT INTO transition_decisions (
            task_id, source_occupancy_transition_id, from_state, to_state,
            question_id, answer, decision_type, actor, recorded_at
        ) VALUES (?, 1, ?, ?, ?, 'APPROVAL', 'APPROVAL', 'human', 12345.0)
        """,
        (task_id, from_s, to_s, approval_qid)
    )
    conn.commit()
    conn.execute("UPDATE tasks SET state = ? WHERE task_id = ?", (to_s, task_id))
    conn.commit()

    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0] == to_s
    conn.close()


def test_non_interactive_approval_always_records_actor_agent(test_env):
    """Regression test (b): Confirms the non-interactive approval path in coordinator.py
    always records actor='agent', never 'human', regardless of approver_role."""
    cp = test_env["cp"]
    db_path = test_env["db_path"]
    reg = TransitionRegistry.load_default()

    task_id = "task-non-interactive-approval"
    conn = sqlite3.connect(db_path)
    _seed_task_at_state(conn, task_id, "AWAITING_APPROVAL")
    conn.close()

    coord = TransitionCoordinator(control_plane=cp, registry=reg)

    # When non-interactive coordination is called with programmatic approval,
    # coordinator must record decision with actor='agent' (which then fails at DB trigger)
    with pytest.raises((PersistenceInvariantViolation, TransitionCoordinatorError)):
        coord.coordinate_transition(
            task_id=task_id,
            to_state="APPROVED",
            actor="agent",
            reason="Non-interactive approval attempt",
            interactive=False,
            provided_answers={"human_implementation_approval": "Approved"},
            approval_decision="APPROVAL",
        )

    conn = sqlite3.connect(db_path)
    # Check that any recorded/staged approval decision was stamped with actor='agent'
    decisions = conn.execute(
        "SELECT actor FROM transition_decisions WHERE task_id = ? AND decision_type = 'APPROVAL'",
        (task_id,)
    ).fetchall()
    for row in decisions:
        assert row[0] == "agent", f"Non-interactive approval must record actor='agent', got {row[0]}"
    conn.close()


def test_stale_decision_replay_across_occupancies_fails(test_env):
    """RED test: A task visits a human-gated edge, records a valid decision, and completes the transition.
    The task then leaves and re-enters the human-gated state (new occupancy).
    Attempting to transition out of the human-gated state without recording a NEW decision must FAIL:
    the prior occupancy's decision must NOT satisfy the database trigger!
    """
    cp = test_env["cp"]
    db_path = test_env["db_path"]
    reg = TransitionRegistry.load_default()
    conn = sqlite3.connect(db_path)

    task_id = "task-stale-replay-001"
    # Seed task at AWAITING_APPROVAL (initial occupancy, e.g. trans_id 1)
    _seed_task_at_state(conn, task_id, "AWAITING_APPROVAL")
    conn.close()

    # Step (a): Complete valid human-approved transition to APPROVED
    inputs = iter(["1", "y"])
    coord = TransitionCoordinator(control_plane=cp, registry=reg, input_fn=lambda prompt: next(inputs))
    record1 = coord.coordinate_transition(
        task_id=task_id,
        to_state="APPROVED",
        actor="human",
        reason="Initial valid human approval in occupancy 1",
        interactive=True
    )
    assert record1.to_state == "APPROVED"

    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0] == "APPROVED"

    # Step (b): Task leaves APPROVED and re-enters AWAITING_APPROVAL (occupancy changes)
    _seed_task_at_state(conn, task_id, "AWAITING_APPROVAL")
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0] == "AWAITING_APPROVAL"

    # Step (c): Attempt transition from AWAITING_APPROVAL -> APPROVED WITHOUT recording new decisions!
    # 1. Raw SQL UPDATE test
    conn.execute("UPDATE tasks SET state = 'APPROVED' WHERE task_id = ?", (task_id,))
    conn.commit()

    # If trigger permits stale replay, state becomes APPROVED. The test asserts that trigger MUST revert it back to AWAITING_APPROVAL!
    state_after_raw = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0]
    assert state_after_raw == "AWAITING_APPROVAL", (
        "CRITICAL VULNERABILITY: Stale decision from prior occupancy satisfied trigger on re-entry! "
        "State was transitioned to APPROVED without fresh human decision."
    )
    violations = conn.execute(
        "SELECT COUNT(*) FROM transition_violations WHERE task_id = ? AND attempted_from_state = 'AWAITING_APPROVAL' AND attempted_to_state = 'APPROVED'",
        (task_id,)
    ).fetchone()[0]
    assert violations >= 1, "Expected violation to be logged when stale decision is replayed"
    conn.close()


def test_recovery_approval_alignment_and_security_guarantees(test_env):
    """Regression test proving that recovery approval alignment with static template question IDs
    strictly preserves all #529 anti-replay, occupancy-binding, and single-use token guarantees:
    1. Static question alignment: decisions recorded match required_transition_questions.
    2. Token integrity: cryptographic token is stored in the answer column.
    3. Token uniqueness: successive approvals generate distinct cryptographic tokens.
    4. Occupancy binding: approval issued in occupancy 1 cannot be used in occupancy 2.
    5. Trigger enforcement: transition without unconsumed approval decision is reverted by trigger.
    6. Atomic consumption: applying recovery transitions marks decisions consumed and binds transition_id.
    7. Anti-replay: consumed token cannot be reused sequentially.
    """
    adapter = test_env["adapter"]
    db_path = test_env["db_path"]
    task_id = "task-recovery-guarantee-001"

    # Setup: create task and move to ESCALATED
    conn = sqlite3.connect(db_path)
    _seed_task_at_state(conn, task_id, "ESCALATED")
    # Determine initial occupancy ID
    last_trans = conn.execute("SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1", (task_id,)).fetchone()
    occ1 = last_trans[0]
    conn.close()

    # 1. Trigger blocks raw recovery transition without approval decision
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE tasks SET state = 'INTAKE' WHERE task_id = ?", (task_id,))
    conn.commit()
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0] == "ESCALATED", \
        "Raw transition to INTAKE without recovery approval must be reverted by trigger!"
    assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ? AND attempted_from_state = 'ESCALATED' AND attempted_to_state = 'INTAKE'", (task_id,)).fetchone()[0] >= 1
    conn.close()

    # 2. Issue approval and test token uniqueness
    token1 = adapter.record_recovery_approval(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ1,
        approver="admin",
        decision="APPROVAL",
        reason="First approval"
    )
    token2 = adapter.record_recovery_approval(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ1,
        approver="admin",
        decision="APPROVAL",
        reason="Second approval"
    )
    assert token1 != token2, "Successive recovery approvals must generate distinct tokens (token uniqueness)"

    # 3. Verify static question alignment and answer column contents in transition_decisions
    conn = sqlite3.connect(db_path)
    decisions = conn.execute(
        "SELECT question_id, answer, actor, consumed_at FROM transition_decisions WHERE task_id = ? AND answer = ?",
        (task_id, token1)
    ).fetchall()
    qids = {r[0] for r in decisions}
    assert "recovery_approval_escalated_to_intake" in qids, "Must contain template human_questions question_id"
    assert "approval_escalated_to_intake" in qids, "Must contain template approval question_id"
    for r in decisions:
        assert r[1] == token1, "Token must be preserved in answer column"
        assert r[2] == "human", "Recovery approval actor must be human"
        assert r[3] is None, "Newly issued approval decision must have consumed_at IS NULL"
    conn.close()

    # 4. Test atomic recovery execution
    rec = adapter.apply_recovery_transition(
        task_id=task_id,
        expected_source_state="ESCALATED",
        destination_state="INTAKE",
        source_occupancy_transition_id=occ1,
        approval_receipt_token=token1,
        actor="admin",
        reason="De-escalate to INTAKE"
    )
    assert rec.to_state == "INTAKE"

    # 5. Verify decisions are now marked consumed
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()[0] == "INTAKE"
    consumed_decisions = conn.execute(
        "SELECT consumed_at, bound_transition_id FROM transition_decisions WHERE task_id = ? AND answer = ?",
        (task_id, token1)
    ).fetchall()
    for c_at, b_tid in consumed_decisions:
        assert c_at is not None, "Applied approval decisions must be marked consumed"
        assert b_tid == rec.transition_id, "Applied approval decisions must be bound to new transition"
    conn.close()

    # 6. Anti-replay: sequential replay attempt with current state fails
    with pytest.raises(ValueError):
        adapter.apply_recovery_transition(
            task_id=task_id,
            expected_source_state="INTAKE",
            destination_state="INTAKE",
            source_occupancy_transition_id=occ1,
            approval_receipt_token=token1,
            actor="admin",
            reason="Replay attempt"
        )

    # 7. Occupancy binding: token2 was issued in occ1; re-entering ESCALATED (occ2) rejects token2
    conn = sqlite3.connect(db_path)
    _seed_task_at_state(conn, task_id, "ESCALATED")
    last_trans2 = conn.execute("SELECT transition_id FROM task_transitions WHERE task_id = ? ORDER BY transition_id DESC LIMIT 1", (task_id,)).fetchone()
    occ2 = last_trans2[0]
    assert occ2 > occ1
    conn.close()

    # Attempting to use token2 (issued for occ1) while task is in occ2 must fail
    with pytest.raises(ValueError, match="Stale occupancy ID"):
        adapter.apply_recovery_transition(
            task_id=task_id,
            expected_source_state="ESCALATED",
            destination_state="INTAKE",
            source_occupancy_transition_id=occ1,
            approval_receipt_token=token2,
            actor="admin",
            reason="Attempt using token from old occupancy"
        )

    # Attempting to use token1 (already consumed in occ1) in occ2 must fail
    with pytest.raises(ValueError, match="Stale occupancy ID"):
        adapter.apply_recovery_transition(
            task_id=task_id,
            expected_source_state="ESCALATED",
            destination_state="INTAKE",
            source_occupancy_transition_id=occ1,
            approval_receipt_token=token1,
            actor="admin",
            reason="Attempt reusing consumed token from old occupancy"
        )

