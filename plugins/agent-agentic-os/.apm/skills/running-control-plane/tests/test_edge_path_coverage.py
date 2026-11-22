"""S4/S5 test: YAML + DB active edges equal the spec's expected 34-edge table, and retired edges are refused."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from agent_control import ControlPlane
from control_plane.constants import ACTIVE_STATES, RETIRED_V14_EDGES
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS


# Exact 34 active edges from job-scoped-control-plane-spec.md Pillar 1
EXPECTED_ACTIVE_EDGES = {
    # Forward (7)
    ("INTAKE", "DRAFT_PLAN"): False,
    ("DRAFT_PLAN", "PLAN_REVIEW"): False,
    ("PLAN_REVIEW", "APPROVED"): True,
    ("APPROVED", "IN_WORKTREE"): False,
    ("IN_WORKTREE", "WORKTREE_REVIEW"): False,
    ("WORKTREE_REVIEW", "VERIFY_EXIT"): True,
    ("VERIFY_EXIT", "DONE"): True,
    # Revise (5; DRAFT_PLAN->INTAKE is also in Reset)
    ("PLAN_REVIEW", "DRAFT_PLAN"): False,
    ("DRAFT_PLAN", "INTAKE"): False,
    ("WORKTREE_REVIEW", "IN_WORKTREE"): False,
    ("VERIFY_EXIT", "IN_WORKTREE"): False,
    ("VERIFY_EXIT", "WORKTREE_REVIEW"): False,
    # Rollback (4)
    ("IN_WORKTREE", "ROLLED_BACK"): False,
    ("WORKTREE_REVIEW", "ROLLED_BACK"): False,
    ("VERIFY_EXIT", "ROLLED_BACK"): False,
    ("ROLLED_BACK", "PLAN_REVIEW"): False,
    # Escalate (3)
    ("INTAKE", "ESCALATED"): False,
    ("ROLLED_BACK", "ESCALATED"): False,
    ("ESCALATED", "PLAN_REVIEW"): False,
    # Reset -> INTAKE (remaining 7 active non-terminal states)
    ("PLAN_REVIEW", "INTAKE"): False,
    ("APPROVED", "INTAKE"): False,
    ("IN_WORKTREE", "INTAKE"): False,
    ("WORKTREE_REVIEW", "INTAKE"): False,
    ("VERIFY_EXIT", "INTAKE"): False,
    ("ROLLED_BACK", "INTAKE"): False,
    ("ESCALATED", "INTAKE"): False,
    # Force-close -> DONE (remaining 8 active non-terminal states)
    ("INTAKE", "DONE"): True,
    ("DRAFT_PLAN", "DONE"): True,
    ("PLAN_REVIEW", "DONE"): True,
    ("APPROVED", "DONE"): True,
    ("IN_WORKTREE", "DONE"): True,
    ("WORKTREE_REVIEW", "DONE"): True,
    ("ROLLED_BACK", "DONE"): True,
    ("ESCALATED", "DONE"): True,
}


def test_yaml_and_db_active_edges_equal_expected_edge_table(tmp_path):
    assert len(EXPECTED_ACTIVE_EDGES) == 34
    assert set(ALLOWED_TRANSITIONS.keys()) == set(ACTIVE_STATES)

    reg = TransitionRegistry.load_default()
    yaml_edges = {
        (t.from_state, t.to_state): bool(t.requires_cryptographic_proof)
        for t in reg.get_all_templates()
    }
    assert yaml_edges == EXPECTED_ACTIVE_EDGES

    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    cp.init_db()
    conn = sqlite3.connect(str(cp.db_path))
    try:
        db_active = {
            (r[0], r[1]): bool(r[2])
            for r in conn.execute(
                "SELECT from_state, to_state, requires_proof FROM valid_transitions "
                "WHERE from_state IS NOT NULL AND retired = 0 AND kind = 'normal'"
            ).fetchall()
        }
        assert db_active == EXPECTED_ACTIVE_EDGES

        db_retired = {
            (r[0], r[1], int(r[2]))
            for r in conn.execute(
                "SELECT from_state, to_state, requires_proof FROM valid_transitions WHERE retired = 1"
            ).fetchall()
        }
        assert db_retired == set(RETIRED_V14_EDGES)
    finally:
        conn.close()
