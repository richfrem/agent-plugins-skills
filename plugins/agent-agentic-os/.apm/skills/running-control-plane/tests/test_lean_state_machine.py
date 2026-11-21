"""S4 tests: lean 10-state machine invariants, retired-state refusal, and RETIRED_V14_EDGES parity."""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import pytest
import yaml

from agent_control import ControlPlane
from control_plane.constants import (
    ACTIVE_STATES,
    RETIRED_STATES,
    RETIRED_V14_EDGES,
    STATE_INTAKE,
)
from control_plane.state_machine import ALLOWED_TRANSITIONS, InvalidStateTransition, StateMachine


REPO_ROOT = Path(__file__).resolve().parents[6]


def test_retired_targets_are_refused_by_state_machine_and_db_trigger_even_with_recovery(tmp_path):
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.init_db()
    cp.create_task("t-lean-1", "Lean test", "claude")

    sm = StateMachine()
    for retired in RETIRED_STATES:
        with pytest.raises(InvalidStateTransition):
            sm.validate_known_state(retired)
        with pytest.raises(InvalidStateTransition):
            sm.validate_recovery_target("t-lean-1", STATE_INTAKE, retired)

    # Even a raw SQLite UPDATE with a staged human recovery decision must be reverted by the trigger
    conn = sqlite3.connect(str(cp.db_path))
    try:
        occ = conn.execute(
            "SELECT MAX(transition_id) FROM task_transitions WHERE task_id = 't-lean-1'"
        ).fetchone()[0]
        for retired in RETIRED_STATES:
            conn.execute(
                "INSERT INTO transition_decisions (task_id, source_occupancy_transition_id, from_state, to_state, "
                "question_id, answer, decision_type, actor, recorded_at) VALUES (?, ?, 'INTAKE', ?, 'recovery_approval_x', 'approved', 'APPROVAL', 'human', 1.0)",
                ("t-lean-1", occ, retired),
            )
            conn.execute("UPDATE tasks SET state = ? WHERE task_id = 't-lean-1'", (retired,))
            actual = conn.execute("SELECT state FROM tasks WHERE task_id = 't-lean-1'").fetchone()[0]
            assert actual == STATE_INTAKE, f"Trigger failed to revert retired target {retired}!"
    finally:
        conn.close()


def test_hand_inserted_open_migration_run_does_not_allow_non_migration_edges(tmp_path):
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.init_db()
    cp.create_task("t-mig-spoof", "Spoof test", "claude")

    conn = sqlite3.connect(str(cp.db_path))
    try:
        conn.execute(
            "INSERT INTO schema_migration_runs (from_version, to_version, started_at, finished_at) "
            "VALUES (14, 15, '2026-11-21T00:00:00Z', NULL)"
        )
        # Try illegal jump INTAKE -> APPROVED and INTAKE -> DONE
        for illegal_target in ("APPROVED", "DONE", "IN_WORKTREE", "INTERVIEW"):
            conn.execute("UPDATE tasks SET state = ? WHERE task_id = 't-mig-spoof'", (illegal_target,))
            actual = conn.execute("SELECT state FROM tasks WHERE task_id = 't-mig-spoof'").fetchone()[0]
            assert actual == STATE_INTAKE, f"Open migration run allowed illegal target {illegal_target}!"
    finally:
        conn.close()


def test_retired_v14_edges_matches_base_commit_yaml():
    """Verify RETIRED_V14_EDGES covers every v14 edge from base commit 289d1e9f not in v15 active edges."""
    res = subprocess.run(
        [
            "git", "-C", str(REPO_ROOT), "show",
            "289d1e9f:plugins/agent-agentic-os/.apm/skills/running-control-plane/scripts/control_plane/transition_templates.yaml",
        ],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        pytest.skip("Base commit 289d1e9f not present in shallow clone")

    data = yaml.safe_load(res.stdout)
    states15 = list(ACTIVE_STATES) + list(RETIRED_STATES)
    v14 = {}
    for t in data["templates"]:
        fs, ts = t["from_state"], t["to_state"]
        proof = 1 if t.get("requires_cryptographic_proof", False) else 0
        if fs == "*":
            for s in states15:
                if s != ts:
                    v14.setdefault((s, ts), proof)
        else:
            v14[(fs, ts)] = proof

    active = {(fs, ts) for fs, tos in ALLOWED_TRANSITIONS.items() for ts in tos}
    expected_retired = tuple(sorted((fs, ts, proof) for (fs, ts), proof in v14.items() if (fs, ts) not in active))
    assert RETIRED_V14_EDGES == expected_retired
