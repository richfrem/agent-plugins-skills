#!/usr/bin/env python
"""
test_dual_identity_onboarding.py
================================

Purpose:
    Contracts for dual-identity onboarding (control_plane/simulation_identity.py and os-init):
      - the simulation identity lives in its own folder and trust file
        (<repo>/context/simulation/identity/) and is created, reused and enrolled additively;
      - it never writes the human's production trust file (<repo>/context/identity/allowed_signers);
      - a registered simulation key is refused on real work even if relabelled as a human in the
        production trust file (round-3 review R5.2), both by the approval policy and by the push verifier;
      - a simulation database signs with the simulation key by default, so an agent can run a full
        simulation end to end, and the result is approved only by that key;
      - status reports human approval, simulation and isolation readiness separately.
    Real ssh-keygen keys and signatures; nothing mocked.

Key Input Dependencies:
    plugins/agent-agentic-os/scripts/control_plane/simulation_identity.py
    plugins/agent-agentic-os/scripts/control_plane/approver_policy.py
    plugins/agent-agentic-os/scripts/control_plane/pipeline_simulator.py

Layer: Development / Testing

Functions:
    - test_simulation_identity_is_created_reused_and_additive
    - test_simulation_identity_never_writes_the_production_trust_file
    - test_registered_simulation_key_refused_on_real_work_even_if_relabelled
    - test_simulation_database_signs_with_the_simulation_key_by_default
    - test_dual_identity_status_reports_three_separate_readiness_items

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_dual_identity_onboarding.py
"""

import hashlib
import sys
import sqlite3
import subprocess
import shutil
from pathlib import Path

import pytest

from control_plane import approver_policy as ap
from control_plane import simulation_identity as si
from control_plane.ssh_signing import SIGN_NAMESPACE
from test_one_approver_per_pipeline import _fp, _repo, keys  # noqa: F401 (fixture)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""


def test_simulation_identity_is_created_reused_and_additive(tmp_path):
    repo = tmp_path / "repo"
    first = si.ensure_simulation_identity(repo)
    assert first["created"] is True
    layout = si.simulation_layout(repo)
    assert layout.root == repo / "context" / "simulation" / "identity"
    assert ap.key_role(first["fingerprint"], layout.allowed_signers) == "agent"
    layout.allowed_signers.write_text(layout.allowed_signers.read_text() + 'other@x namespaces="x" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGnTM0YmU5Xa7ZyFm5XQ6k3pTzqg0fJ9nK2vY1gYk7Q0\n')
    again = si.ensure_simulation_identity(repo)
    assert again["created"] is False and again["fingerprint"] == first["fingerprint"]
    assert "other@x" in layout.allowed_signers.read_text()  # additive: existing lines kept
    assert layout.allowed_signers.read_text().count(ap.AGENT_SIMULATION_PRINCIPAL) == 1


def test_simulation_identity_never_writes_the_production_trust_file(tmp_path):
    repo = tmp_path / "repo"
    production = repo / "context" / "identity" / "allowed_signers"
    production.parent.mkdir(parents=True)
    production.write_text("human@x namespaces=\"control-plane@agentic-os.local\" ssh-ed25519 AAAA\n")
    before = _sha(production)
    si.ensure_simulation_identity(repo)
    assert _sha(production) == before


def test_registered_simulation_key_refused_on_real_work_even_if_relabelled(tmp_path, keys):
    root = tmp_path / "r"
    sim = si.ensure_simulation_identity(root)
    sim_pub = Path(str(sim["key"]) + ".pub").read_text().split()[:2]
    relabelled = f'operator@control-plane namespaces="{SIGN_NAMESPACE}" {sim_pub[0]} {sim_pub[1]}'
    cp, allowed = _repo(root, [keys["lines"]["human"], relabelled])
    assert ap.key_role(sim["fingerprint"], allowed) == "human"  # the production file was relabelled
    with sqlite3.connect(cp.db_path) as conn, pytest.raises(ap.ApproverPolicyError, match="registered simulation key"):
        ap.enforce_pipeline_approver(conn, "t1", sim["fingerprint"], "operator@control-plane", allowed, cp.db_path)


def test_simulation_database_signs_with_the_simulation_key_by_default(tmp_path):
    """Outside the test suite's stand-in human, a simulation database's gates are signed by the
    repository's simulation key: an agent can run a full simulation end to end on its own."""
    from control_plane.pipeline_simulator import PipelineSimulator

    db = tmp_path / "repo" / "context" / "simulation" / ap.SIMULATION_DB_NAME
    sim = PipelineSimulator(db)
    sim.create_task("t-sim", "simulation")
    sim.run_standard_happy_path("t-sim")
    status = si.ensure_simulation_identity(tmp_path / "repo")
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT state FROM tasks WHERE task_id = 't-sim'").fetchone()[0] == "DONE"
        assert ap.get_binding(conn, "t-sim")["approver_fingerprint"] == status["fingerprint"]


def test_dual_identity_status_reports_three_separate_readiness_items(tmp_path):
    repo = tmp_path / "repo"
    before = si.dual_identity_status(repo)
    assert set(before) == {"human", "simulation", "isolation"}
    assert before["simulation"]["ready"] is False
    si.ensure_simulation_identity(repo)
    after = si.dual_identity_status(repo)
    assert after["simulation"]["ready"] is True
    assert after["human"]["ready"] is False  # no human key enrolled
    assert "ready" in after["isolation"] and "detail" in after["isolation"]


def test_account_existence_does_not_prove_runtime_isolation(tmp_path, monkeypatch):
    import os
    from control_plane import isolation_check

    monkeypatch.setattr(isolation_check, "_resolve_agent_identity", lambda *args: (os.geteuid() + 1, set()))
    status = si.dual_identity_status(tmp_path)
    assert status["isolation"]["ready"] is False


def test_full_simulation_runs_standalone_from_the_installed_skill(tmp_path):
    """Outside the test suite (no stand-in signer, no fake review menu, real PATH), a simulation runs
    INTAKE -> DONE from the transition-simulator skill's own scripts, approved only by its simulation key."""
    source = Path(__file__).resolve().parents[1] / "skills" / "transition-simulator"
    installed = tmp_path / "installed-skill"
    shutil.copytree(source, installed, symlinks=False)
    assert not any(path.is_symlink() for path in installed.rglob("*"))
    skill_scripts = installed / "scripts"
    db = tmp_path / "repo" / "context" / "simulation" / ap.SIMULATION_DB_NAME
    code = (
        "from pathlib import Path\n"
        "from control_plane.pipeline_simulator import PipelineSimulator\n"
        f"sim = PipelineSimulator(Path({str(db)!r}))\n"
        "sim.create_task('t-standalone', 'standalone simulation')\n"
        "sim.run_standard_happy_path('t-standalone')\n"
    )
    res = subprocess.run([sys.executable, "-B", "-c", code], cwd=skill_scripts, capture_output=True, text=True, timeout=300)
    assert res.returncode == 0, res.stderr[-2000:]
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT state FROM tasks WHERE task_id = 't-standalone'").fetchone()[0] == "DONE"
        assert ap.get_binding(conn, "t-standalone")["approver_fingerprint"] == si.ensure_identity_at(db.parent / "identity")["fingerprint"]
