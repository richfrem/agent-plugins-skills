#!/usr/bin/env python
"""
test_signed_approval_human_receipt.py
=====================================

Purpose:
    Two frictions found moving a real task (InvestmentToolkit nbis-scenario-lines-overlay,
    2026-09-27) from APPROVED to IN_WORKTREE:
      1. The human's signed AWAITING_APPROVAL -> APPROVED did not record the `human_approval`
         receipt that APPROVED -> IN_WORKTREE requires, so a second, typed record-human-approval
         call was needed. The simulator and fixtures hid this by calling record_human_approval()
         by hand after every signed approval.
      2. The transition checklist printed "[✓] Deterministic check satisfied: human_approval (PASS)"
         while the same check denied the transition: YAML checklist lines were ticked without
         being evaluated.

Key Input Dependencies:
    plugins/agent-agentic-os/scripts/control_plane/adapters.py (signed commit path)
    plugins/agent-agentic-os/scripts/control_plane/coordinator.py (checklist display)
    plugins/agent-agentic-os/scripts/control_plane/pipeline_simulator.py

Layer: Development / Testing

Functions:
    - test_signed_approval_alone_is_enough_for_in_worktree
    - test_checklist_does_not_tick_a_failing_check

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_signed_approval_human_receipt.py
"""

import io
import sqlite3

import pytest

from agent_control import ControlPlane
from control_plane.coordinator import TransitionCoordinator, TransitionCoordinatorError
from control_plane.pipeline_simulator import PipelineSimulator


def test_signed_approval_alone_is_enough_for_in_worktree(tmp_path, monkeypatch):
    monkeypatch.setattr(ControlPlane, "record_human_approval", lambda self, task_id, approver: "not-recorded")
    sim = PipelineSimulator(tmp_path / "control_plane.db")
    sim.create_task("t1", "real work")
    sim.run_standard_happy_path("t1")
    with sqlite3.connect(sim.db_path) as conn:
        assert conn.execute("SELECT state FROM tasks WHERE task_id = 't1'").fetchone()[0] == "DONE"
        rows = conn.execute(
            "SELECT command_executed FROM verification_receipts WHERE task_id = 't1' AND gate_name = 'human_approval'"
        ).fetchall()
    assert len(rows) == 1
    assert rows[0][0].startswith("approved-by:") and "key=SHA256:" in rows[0][0]


def test_checklist_does_not_tick_a_failing_check(tmp_path, monkeypatch):
    monkeypatch.setattr(ControlPlane, "record_human_approval", lambda self, task_id, approver: "not-recorded")
    sim = PipelineSimulator(tmp_path / "control_plane.db")
    sim.create_task("t1", "real work")
    with pytest.raises(Exception):  # stop the happy path right after the signed approval
        monkeypatch.setattr(ControlPlane, "update_worktree", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("stop")))
        sim.run_standard_happy_path("t1")
    monkeypatch.undo()
    with sqlite3.connect(sim.db_path) as conn:
        assert conn.execute("SELECT state FROM tasks WHERE task_id = 't1'").fetchone()[0] == "APPROVED"
        conn.execute("DELETE FROM verification_receipts WHERE task_id = 't1' AND gate_name = 'human_approval'")
    out = io.StringIO()
    with pytest.raises(TransitionCoordinatorError):
        TransitionCoordinator(sim.control_plane, registry=sim.registry, input_fn=lambda _p: "YES", output_stream=out).coordinate_transition(
            task_id="t1", to_state="IN_WORKTREE", actor="simulator", reason="checklist check", interactive=True,
        )
    text = out.getvalue()
    # coordinator.py prints "[PASS] <item> (PASS)" / "[FAIL] <item> (FAIL)". This test used to look for
    # the retired "[✓]" / "[✗]" markers, so its first assertion could never fail (vacuous) and its
    # second could never pass.
    assert "[PASS] Deterministic check satisfied: human_approval" not in text
    assert "[FAIL] Deterministic check satisfied: human_approval (FAIL)" in text
