#!/usr/bin/env python
"""
test_approver_isolation.py
==========================

Purpose:
    Refusal regressions for the round-3 adversarial review
    (temp/_prompt_requests/review-one-approver-per-pipeline-round3-response.md). Each attack that
    the reviewer reproduced must now be refused, and legitimate real-work and simulation pipelines
    must keep working:
      R1 a database path swapped after the commit connection opened
      R2 a completed simulation symlinked or copied into the production location
      R3 a symlinked production database dropping the canonical trust-anchor rule
      R4 hard-link or case aliases reclassifying a simulation database
      R5.1 an edited binding row switching the approver key
      R5.2 key relabelling in a same-user writable anchor: reported as an isolation gap, not approvable
    Real ssh-keygen keys, signatures, SQLite files and the real pre-push guard script throughout.

Key Input Dependencies:
    plugins/agent-agentic-os/scripts/control_plane/approver_policy.py
    plugins/agent-agentic-os/scripts/control_plane/gate_evidence.py
    plugins/agent-agentic-os/scripts/pre-push-review-guard
    plugins/agent-agentic-os/tests/test_one_approver_per_pipeline.py (shared fixtures)

Layer: Development / Testing

Functions:
    - test_simulation_done_refused_by_production_push_guard (R2, symlink and copy)
    - test_real_work_done_accepted_by_production_push_guard (R2 positive)
    - test_push_guard_refuses_done_without_signed_evidence
    - test_hardlinked_simulation_database_is_refused (R4)
    - test_case_alias_of_simulation_database_is_refused (R4)
    - test_symlinked_production_database_is_refused (R3)
    - test_edited_binding_disagreeing_with_history_is_refused (R5.1)
    - test_database_identity_mismatch_is_refused (R1 at policy level)
    - test_path_swap_after_connection_open_is_refused (R1 end to end)

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_approver_isolation.py
"""

import io
import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

from control_plane import approver_policy as ap
from control_plane.pipeline_simulator import PipelineSimulator
from test_one_approver_per_pipeline import _consumed_request, _enforce, _fp, _repo, keys  # noqa: F401 (fixture)

HOOK = Path(__file__).resolve().parents[1] / "scripts" / "pre-push-review-guard"


def _run_hook(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(HOOK)], cwd=root, capture_output=True, text=True)


def _git_on_branch(root: Path, branch: str) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "symbolic-ref", "HEAD", f"refs/heads/{branch}"], check=True)


@pytest.mark.parametrize("ingress", ["symlink", "copy"])
def test_simulation_done_refused_by_production_push_guard(tmp_path, ingress):
    root = tmp_path / "production"
    root.mkdir()
    simulation = root / "context" / "simulation" / ap.SIMULATION_DB_NAME
    sim = PipelineSimulator(simulation)
    sim.create_task("sim-task", "simulation-only work")
    sim.run_standard_happy_path("sim-task")
    _git_on_branch(root, "sim/sim-task")
    real = root / "context" / "control_plane.db"
    if ingress == "symlink":
        real.symlink_to(simulation)
    else:
        with sqlite3.connect(simulation) as src, sqlite3.connect(real) as dst:
            src.backup(dst)
    result = _run_hook(root)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "BLOCKED" in result.stdout + result.stderr


def test_real_work_done_accepted_by_production_push_guard(tmp_path):
    root = tmp_path / "production"
    root.mkdir()
    real = root / "context" / "control_plane.db"
    sim = PipelineSimulator(real)
    sim.create_task("real-task", "real work")
    sim.run_standard_happy_path("real-task")
    _git_on_branch(root, "sim/real-task")
    result = _run_hook(root)
    assert result.returncode == 0, result.stdout + result.stderr


def test_push_guard_refuses_done_without_signed_evidence(tmp_path):
    root = tmp_path / "production"
    root.mkdir()
    real = root / "context" / "control_plane.db"
    sim = PipelineSimulator(real)
    sim.create_task("real-task", "real work")
    sim.run_standard_happy_path("real-task")
    with sqlite3.connect(real) as conn:
        conn.execute("DELETE FROM signed_gate_evidence WHERE task_id = 'real-task'")
    _git_on_branch(root, "sim/real-task")
    result = _run_hook(root)
    assert result.returncode != 0 and "signed" in (result.stdout + result.stderr).lower()


@pytest.mark.parametrize("missing_gate", ["APPROVED", "VERIFY_EXIT"])
def test_push_guard_refuses_missing_earlier_gate_evidence(tmp_path, missing_gate):
    root = tmp_path / "production"
    root.mkdir()
    real = root / "context" / "control_plane.db"
    sim = PipelineSimulator(real)
    sim.create_task("real-task", "real work")
    sim.run_standard_happy_path("real-task")
    with sqlite3.connect(real) as conn:
        cursor = conn.execute(
            "DELETE FROM signed_gate_evidence WHERE task_id = ? AND to_state = ?",
            ("real-task", missing_gate),
        )
        assert cursor.rowcount == 1
    _git_on_branch(root, "sim/real-task")
    result = _run_hook(root)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "evidence" in (result.stdout + result.stderr).lower()


@pytest.mark.parametrize("tamper", ["nonce", "request_status", "occupancy", "fingerprint"])
def test_push_guard_refuses_evidence_request_mismatch(tmp_path, tamper):
    """A genuine human signature cannot authenticate altered request metadata."""
    root = tmp_path / "production"
    root.mkdir()
    real = root / "context" / "control_plane.db"
    sim = PipelineSimulator(real)
    sim.create_task("real-task", "real work")
    sim.run_standard_happy_path("real-task")
    statements = {
        "nonce": "UPDATE transition_request SET nonce = 'tampered' WHERE to_state = 'APPROVED'",
        "request_status": "UPDATE transition_request SET status = 'DENIED' WHERE to_state = 'APPROVED'",
        "occupancy": "UPDATE transition_request SET occupancy_id = -1 WHERE to_state = 'APPROVED'",
        "fingerprint": "UPDATE signed_gate_evidence SET fingerprint = 'SHA256:other' WHERE to_state = 'APPROVED'",
    }
    with sqlite3.connect(real) as conn:
        assert conn.execute(statements[tamper]).rowcount == 1
    _git_on_branch(root, "sim/real-task")
    result = _run_hook(root)
    assert result.returncode != 0, result.stdout + result.stderr


def test_hardlinked_simulation_database_is_refused(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]], db_name=ap.SIMULATION_DB_NAME)
    os.link(cp.db_path, Path(cp.db_path).with_name("another-name.db"))
    assert ap.classify_path(cp.db_path) == ap.CONTEXT_AMBIGUOUS
    for key, principal in ((keys["human"], "operator@control-plane"), (keys["agent"], ap.AGENT_SIMULATION_PRINCIPAL)):
        with pytest.raises(ap.ApproverPolicyError, match="ambiguous"):
            _enforce(cp, key, allowed, principal=principal)


def test_case_alias_of_simulation_database_is_refused(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]], db_name=ap.SIMULATION_DB_NAME)
    upper = Path(cp.db_path).with_name("Simulation_Control_Plane.db")
    assert ap.classify_path(upper) == ap.CONTEXT_AMBIGUOUS
    if upper.exists() and upper.samefile(cp.db_path):  # case-insensitive filesystem: same file, different spelling
        with sqlite3.connect(upper) as conn, pytest.raises(ap.ApproverPolicyError, match="ambiguous"):
            ap.enforce_pipeline_approver(conn, "t1", _fp(keys["human"]), "operator@control-plane", allowed, upper)


def test_symlinked_production_database_is_refused(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]])
    real = Path(cp.db_path)
    renamed = real.with_name("renamed.db")
    real.rename(renamed)
    real.symlink_to(renamed)
    assert ap.is_repository_db(real)
    with sqlite3.connect(real) as conn, pytest.raises(ap.ApproverPolicyError, match="symlink"):
        ap.enforce_pipeline_approver(conn, "t1", _fp(keys["human"]), "operator@control-plane", allowed, real)


def test_edited_binding_disagreeing_with_history_is_refused(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["human2"]])
    _enforce(cp, keys["human"], allowed)
    _consumed_request(cp, _fp(keys["human"]), request_id=1)
    with sqlite3.connect(cp.db_path) as conn:
        conn.execute("UPDATE task_approver_binding SET approver_fingerprint = ? WHERE task_id = 't1'", (_fp(keys["human2"]),))
    with pytest.raises(ap.ApproverPolicyError, match="disagrees with"):
        _enforce(cp, keys["human2"], allowed, principal="second@control-plane", request_id=2)


def test_database_identity_mismatch_is_refused(tmp_path, keys):
    """A database stamped as a simulation, opened under a real-work name (copied or swapped in), is refused."""
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]], db_name=ap.SIMULATION_DB_NAME)
    with sqlite3.connect(cp.db_path) as conn:
        assert ap.database_identity(conn) == ap.CONTEXT_SIMULATION
    copied = Path(cp.db_path).with_name("control_plane.db")
    with sqlite3.connect(cp.db_path) as src, sqlite3.connect(copied) as dst:
        src.backup(dst)
    with sqlite3.connect(copied) as conn, pytest.raises(ap.ApproverPolicyError, match="identity"):
        ap.enforce_pipeline_approver(conn, "t1", _fp(keys["human"]), "operator@control-plane", allowed, copied)


@pytest.mark.no_auto_signer
def test_path_swap_after_connection_open_is_refused(tmp_path, keys, monkeypatch):
    from control_plane.gate1_approval import GateApprovalError, approve_transition
    from test_approve_transition import TASK, Gate

    gate = Gate(tmp_path)
    with gate.layout.allowed_signers.open("a") as f:
        f.write(keys["lines"]["agent"] + "\n")
    real = Path(gate.cp.db_path)
    alias = tmp_path / "entry" / ap.SIMULATION_DB_NAME
    alias.parent.mkdir()
    alias.symlink_to(real)
    gate.cp.db_path = alias
    gate.cp._persistence.db_path = alias
    challenge, _ = gate.show()
    gate.sign(challenge, key=keys["agent"])
    original_get = gate.cp._persistence.get_connection
    swapped = []

    def traced_get():
        conn = original_get()

        def trace(sql):
            if sql.strip().upper().startswith("BEGIN IMMEDIATE") and not swapped:
                alias.unlink()
                with sqlite3.connect(alias):
                    pass
                swapped.append(True)

        conn.set_trace_callback(trace)
        return conn

    monkeypatch.setattr(gate.cp._persistence, "get_connection", traced_get)
    with pytest.raises((ap.ApproverPolicyError, GateApprovalError)):
        approve_transition(
            gate.cp, gate.request_id, layout=gate.layout, principal=ap.AGENT_SIMULATION_PRINCIPAL,
            agent_identity=gate.identity, out=io.StringIO(),
        )
    assert swapped
    with sqlite3.connect(real) as conn:
        assert conn.execute("SELECT state FROM tasks WHERE task_id = ?", (TASK,)).fetchone()[0] == "AWAITING_APPROVAL"
        assert conn.execute("SELECT status FROM transition_request WHERE request_id = ?", (gate.request_id,)).fetchone()[0] == "PENDING"


COMMIT_HOOK = Path(__file__).resolve().parents[1] / "scripts" / "pre-commit-pipeline-guard"


@pytest.mark.parametrize("ingress", ["symlink", "copy"])
def test_commit_guard_refuses_simulation_database_in_production_location(tmp_path, ingress):
    root = tmp_path / "production"
    root.mkdir()
    simulation = root / "context" / "simulation" / ap.SIMULATION_DB_NAME
    sim = PipelineSimulator(simulation)
    sim.create_task("sim-task", "simulation-only work")
    _git_on_branch(root, "feature/x")
    real = root / "context" / "control_plane.db"
    if ingress == "symlink":
        real.symlink_to(simulation)
    else:
        with sqlite3.connect(simulation) as src, sqlite3.connect(real) as dst:
            src.backup(dst)
    result = subprocess.run(["bash", str(COMMIT_HOOK)], cwd=root, capture_output=True, text=True)
    assert result.returncode != 0 and "BLOCKED" in result.stdout + result.stderr, result.stdout + result.stderr
