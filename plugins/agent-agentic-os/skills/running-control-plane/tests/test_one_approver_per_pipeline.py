#!/usr/bin/env python
"""
test_one_approver_per_pipeline.py
=================================

Purpose:
    Contract tests for one approver per pipeline (control_plane/approver_policy.py) in the
    two-database design: real work lives in control_plane.db (only human keys approve) and
    simulations in a separate simulation_control_plane.db (only the agent key approves). The
    context is a property of the database file, never of a row. Includes a regression for each
    applicable finding of the round-1 and round-2 adversarial reviews
    (temp/_prompt_requests/review-one-approver-per-pipeline-*response.md). Real ssh-keygen keys
    and signatures throughout; nothing is mocked except which key the stand-in human picks in
    the two negative end-to-end tests.

Key Input Dependencies:
    plugins/agent-agentic-os/scripts/control_plane/approver_policy.py — rules under test
    plugins/agent-agentic-os/scripts/control_plane/pipeline_simulator.py — end-to-end pipelines
    plugins/agent-agentic-os/tests/helpers/human_signer.py — stand-in human (operator + agent keys)
    ssh-keygen

Layer: Development / Testing

Functions:
    - test_context_is_decided_by_database_file_name
    - test_real_work_binds_first_human_key
    - test_second_human_key_refused_on_bound_pipeline
    - test_agent_key_refused_in_real_work_database
    - test_agent_key_under_alias_is_still_the_agent
    - test_principal_patterns_fail_closed
    - test_key_enrolled_as_both_agent_and_human_fails_closed
    - test_repository_database_requires_canonical_trust_anchor
    - test_binding_survives_receipt_deletion
    - test_rollout_binds_to_the_key_that_signed_earlier_gates
    - test_foreign_binding_row_fails_closed
    - test_simulation_database_refuses_human_key
    - test_simulation_database_keeps_one_agent_key
    - test_semicolon_principal_keeps_key_continuity
    - test_full_simulation_pipeline_only_agent_approves
    - test_full_real_work_pipeline_only_human_approves
    - test_agent_signature_refused_through_real_commit
    - test_human_signature_refused_through_real_commit_in_simulation

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_one_approver_per_pipeline.py
"""

import sqlite3
import subprocess
from pathlib import Path

import pytest

from agent_control import ControlPlane
from control_plane import approver_policy as ap
from control_plane.ssh_signing import SIGN_NAMESPACE

HUMAN = "operator@control-plane"


def _keygen(path: Path) -> str:
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(path)], check=True)
    kt, kb = Path(str(path) + ".pub").read_text().split()[:2]
    return f"{kt} {kb}"


def _fp(path: Path) -> str:
    return ap.key_fingerprint(Path(str(path) + ".pub").read_text().split()[1])


@pytest.fixture
def keys(tmp_path):
    """Real human, second human, agent and second agent keys."""
    k = {name: tmp_path / f"{name}_key" for name in ("human", "human2", "agent", "agent2")}
    pubs = {name: _keygen(path) for name, path in k.items()}
    k["pubs"] = pubs
    k["lines"] = {
        "human": f'{HUMAN} namespaces="{SIGN_NAMESPACE}" {pubs["human"]}',
        "human2": f'second@control-plane namespaces="{SIGN_NAMESPACE}" {pubs["human2"]}',
        "agent": f'{ap.AGENT_SIMULATION_PRINCIPAL} namespaces="{SIGN_NAMESPACE}" {pubs["agent"]}',
        "agent2": f'{ap.AGENT_SIMULATION_PRINCIPAL} namespaces="{SIGN_NAMESPACE}" {pubs["agent2"]}',
    }
    return k


def _repo(root: Path, lines: list, db_name: str = ap.REPOSITORY_DB_NAME) -> tuple:
    """<root>/context/<db_name> with its allowed_signers at <root>/context/identity/allowed_signers."""
    (root / "context" / "identity" / "challenges").mkdir(parents=True)
    allowed = root / "context" / "identity" / "allowed_signers"
    allowed.write_text("\n".join(lines) + "\n")
    cp = ControlPlane(db_path=root / "context" / db_name)
    cp.init_db()
    cp.create_task("t1", "demo", "claude-code")
    return cp, allowed


def _enforce(cp, key, allowed, principal=HUMAN, request_id=None):
    with sqlite3.connect(cp.db_path) as conn:
        ap.enforce_pipeline_approver(conn, "t1", _fp(key), principal, allowed, cp.db_path, request_id)


def test_context_is_decided_by_database_file_name(tmp_path):
    assert ap.pipeline_context(tmp_path / "context" / "control_plane.db") == ap.CONTEXT_REAL
    assert ap.pipeline_context(tmp_path / "anything-else.db") == ap.CONTEXT_REAL  # unknown names fail safe
    assert ap.pipeline_context(tmp_path / "context" / "simulation" / ap.SIMULATION_DB_NAME) == ap.CONTEXT_SIMULATION


def test_real_work_binds_first_human_key(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]])
    _enforce(cp, keys["human"], allowed)
    with sqlite3.connect(cp.db_path) as conn:
        b = ap.get_binding(conn, "t1")
    assert (b["context"], b["approver_fingerprint"], b["source"]) == (ap.CONTEXT_REAL, _fp(keys["human"]), "first_gate")
    _enforce(cp, keys["human"], allowed)  # same key: later gates pass


def test_second_human_key_refused_on_bound_pipeline(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["human2"]])
    _enforce(cp, keys["human"], allowed)
    with pytest.raises(ap.ApproverPolicyError, match="One approver per pipeline"):
        _enforce(cp, keys["human2"], allowed, principal="second@control-plane")


def test_agent_key_refused_in_real_work_database(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]])
    with pytest.raises(ap.ApproverPolicyError, match="cannot approve real work"):
        _enforce(cp, keys["agent"], allowed, principal=ap.AGENT_SIMULATION_PRINCIPAL)


def test_agent_key_under_alias_is_still_the_agent(tmp_path, keys):
    alias = f'alias,{ap.AGENT_SIMULATION_PRINCIPAL} namespaces="{SIGN_NAMESPACE}" {keys["pubs"]["agent"]}'
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], alias])
    assert ap.key_role(_fp(keys["agent"]), allowed) == "agent"
    with pytest.raises(ap.ApproverPolicyError, match="cannot approve real work"):
        _enforce(cp, keys["agent"], allowed, principal="alias")


@pytest.mark.parametrize("principals", ["test-*@local", "test-hum?n@local", "*", "!someone@x,test-human@local"])
def test_principal_patterns_fail_closed(tmp_path, keys, principals):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], f'{principals} namespaces="{SIGN_NAMESPACE}" {keys["pubs"]["agent"]}'])
    with pytest.raises(ap.ApproverPolicyError, match="principal pattern"):
        _enforce(cp, keys["human"], allowed)


def test_key_enrolled_as_both_agent_and_human_fails_closed(tmp_path, keys):
    both = f'sneaky@control-plane namespaces="{SIGN_NAMESPACE}" {keys["pubs"]["agent"]}'
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["agent"], both])
    with pytest.raises(ap.ApproverPolicyError, match="both as the agent"):
        _enforce(cp, keys["agent"], allowed, principal="sneaky@control-plane")


def test_repository_database_requires_canonical_trust_anchor(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"]])
    stray = tmp_path / "stray_allowed_signers"
    stray.write_text(f'{HUMAN} namespaces="{SIGN_NAMESPACE}" {keys["pubs"]["agent"]}\n')  # agent key labelled human
    with pytest.raises(ap.ApproverPolicyError, match="must be verified against"):
        _enforce(cp, keys["agent"], stray)
    assert ap.canonical_anchor(cp.db_path) == allowed.resolve()
    _enforce(cp, keys["human"], allowed)


def test_binding_survives_receipt_deletion(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["human2"]])
    _enforce(cp, keys["human"], allowed)
    with sqlite3.connect(cp.db_path) as conn:  # what invalidation and an INTAKE reset do to evidence
        conn.execute("UPDATE verification_receipts SET invalidated_at = 1 WHERE task_id = 't1'")
        conn.execute("DELETE FROM verification_receipts WHERE task_id = 't1'")
    with pytest.raises(ap.ApproverPolicyError, match="One approver per pipeline"):
        _enforce(cp, keys["human2"], allowed, principal="second@control-plane")


def _consumed_request(cp, fingerprint: str, request_id: int) -> None:
    """A signed gate committed before this policy existed: a consumed request, no binding row."""
    with sqlite3.connect(cp.db_path) as conn:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(transition_request)")]
        conn.execute("PRAGMA foreign_keys = OFF")
        values = {c: None for c in cols}
        values.update(request_id=request_id, task_id="t1", status="CONSUMED", jti=f"sshsig:{fingerprint}")
        notnull = {r[1]: r[3] for r in conn.execute("PRAGMA table_info(transition_request)")}
        for c in cols:
            if values[c] is None and notnull[c]:
                values[c] = 0
        conn.execute(f"INSERT INTO transition_request ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", tuple(values[c] for c in cols))


def test_rollout_binds_to_the_key_that_signed_earlier_gates(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["human2"]])
    _consumed_request(cp, _fp(keys["human"]), request_id=1)
    with pytest.raises(ap.ApproverPolicyError, match="earlier signed gate"):
        _enforce(cp, keys["human2"], allowed, principal="second@control-plane", request_id=2)
    _enforce(cp, keys["human"], allowed, request_id=2)
    with sqlite3.connect(cp.db_path) as conn:
        assert ap.get_binding(conn, "t1")["source"] == "history"


def test_foreign_binding_row_fails_closed(tmp_path, keys):
    """A binding row that does not match this task and database (copied, stale, or forged) grants nothing."""
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]])
    with sqlite3.connect(cp.db_path) as conn:
        ap.ensure_binding_table(conn)
        conn.execute(
            "INSERT INTO task_approver_binding VALUES ('t1', (SELECT created_at FROM tasks WHERE task_id='t1'), 'simulation', ?, 'x', 'first_gate', 0)",
            (_fp(keys["agent"]),),
        )
    with pytest.raises(ap.ApproverPolicyError, match="cannot approve real work"):
        _enforce(cp, keys["agent"], allowed, principal=ap.AGENT_SIMULATION_PRINCIPAL)
    with pytest.raises(ap.ApproverPolicyError, match="does not belong"):
        _enforce(cp, keys["human"], allowed)


def test_simulation_database_refuses_human_key(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]], db_name=ap.SIMULATION_DB_NAME)
    with pytest.raises(ap.ApproverPolicyError, match="a human key cannot"):
        _enforce(cp, keys["human"], allowed)
    _enforce(cp, keys["agent"], allowed, principal=ap.AGENT_SIMULATION_PRINCIPAL)


def test_simulation_database_keeps_one_agent_key(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["agent"], keys["lines"]["agent2"]], db_name=ap.SIMULATION_DB_NAME)
    _enforce(cp, keys["agent"], allowed, principal=ap.AGENT_SIMULATION_PRINCIPAL)
    with pytest.raises(ap.ApproverPolicyError, match="One approver per pipeline"):
        _enforce(cp, keys["agent2"], allowed, principal=ap.AGENT_SIMULATION_PRINCIPAL)


def test_semicolon_principal_keeps_key_continuity(tmp_path, keys):
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"]])
    _enforce(cp, keys["human"], allowed, principal="odd;name@x")
    _enforce(cp, keys["human"], allowed, principal="odd;name@x")
    with sqlite3.connect(cp.db_path) as conn:
        assert ap.get_binding(conn, "t1")["approver_principal"] == "odd;name@x"


# ---- complete pipelines through the real signed commit path ----

def _state_and_binding(sim, task):
    with sqlite3.connect(sim.db_path) as conn:
        state = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task,)).fetchone()[0]
        return state, ap.get_binding(conn, task)


def test_full_simulation_pipeline_only_agent_approves(tmp_path):
    from control_plane.pipeline_simulator import PipelineSimulator
    from helpers.human_signer import get_test_human

    from control_plane.simulation_identity import ensure_identity_at

    sim = PipelineSimulator(tmp_path / ap.SIMULATION_DB_NAME)  # signs with its own simulation key by default
    sim.create_task("t-sim", "simulation")
    sim.run_standard_happy_path("t-sim")
    state, b = _state_and_binding(sim, "t-sim")
    assert state == "DONE"
    sim_key = ensure_identity_at(tmp_path / "identity")["fingerprint"]
    assert (b["context"], b["approver_fingerprint"]) == (ap.CONTEXT_SIMULATION, sim_key)
    assert sim_key != _fp(get_test_human().key)  # its own generated key, not the suite's


def test_full_real_work_pipeline_only_human_approves(tmp_path):
    from control_plane.pipeline_simulator import PipelineSimulator
    from helpers.human_signer import get_test_human

    sim = PipelineSimulator(tmp_path / "control_plane.db")
    sim.create_task("t-real", "real work")
    sim.run_standard_happy_path("t-real")
    state, b = _state_and_binding(sim, "t-real")
    assert state == "DONE"
    assert (b["context"], b["approver_fingerprint"]) == (ap.CONTEXT_REAL, _fp(get_test_human().operator_key))


def test_agent_signature_refused_through_real_commit(tmp_path, monkeypatch):
    from control_plane.gate1_approval import GateApprovalError
    from control_plane.pipeline_simulator import PipelineSimulator
    from helpers.human_signer import TestHuman, get_test_human

    human = get_test_human()
    monkeypatch.setattr(TestHuman, "signer_for", lambda self, cp, rid: (human.key, ap.AGENT_SIMULATION_PRINCIPAL))
    sim = PipelineSimulator(tmp_path / "control_plane.db")
    sim.create_task("t-real", "real work")
    with pytest.raises((ap.ApproverPolicyError, GateApprovalError), match="cannot approve real work"):
        sim.run_standard_happy_path("t-real")
    state, b = _state_and_binding(sim, "t-real")
    assert state == "AWAITING_APPROVAL" and b is None


def test_human_signature_refused_through_real_commit_in_simulation(tmp_path, monkeypatch):
    from control_plane.gate1_approval import GateApprovalError
    from control_plane.pipeline_simulator import PipelineSimulator
    from helpers.human_signer import OPERATOR_PRINCIPAL, TestHuman, get_test_human

    human = get_test_human()
    monkeypatch.setattr(TestHuman, "signer_for", lambda self, cp, rid: (human.operator_key, OPERATOR_PRINCIPAL))
    sim = PipelineSimulator(tmp_path / ap.SIMULATION_DB_NAME, human_signer=human.sign_request)
    sim.create_task("t-sim", "simulation")
    with pytest.raises((ap.ApproverPolicyError, GateApprovalError), match="a human key cannot"):
        sim.run_standard_happy_path("t-sim")
    state, b = _state_and_binding(sim, "t-sim")
    assert state == "AWAITING_APPROVAL" and b is None


def test_simulation_name_pointing_at_real_database_is_refused(tmp_path, keys):
    """A symlink or hard link NAMED simulation_control_plane.db that reaches the real database is
    ambiguous: refused for every key, never treated as a simulation (and never reassigned)."""
    cp, allowed = _repo(tmp_path / "r", [keys["lines"]["human"], keys["lines"]["agent"]])
    real = Path(cp.db_path)
    symlinked = real.parent / "sym" / ap.SIMULATION_DB_NAME
    symlinked.parent.mkdir()
    symlinked.symlink_to(real)
    hardlinked = real.parent / "hard" / ap.SIMULATION_DB_NAME
    hardlinked.parent.mkdir()
    import os
    os.link(real, hardlinked)
    for alias in (symlinked, hardlinked):
        assert ap.pipeline_context(alias) == ap.CONTEXT_AMBIGUOUS, alias
        for key, principal in ((keys["agent"], ap.AGENT_SIMULATION_PRINCIPAL), (keys["human"], HUMAN)):
            with sqlite3.connect(alias) as conn, pytest.raises(ap.ApproverPolicyError, match="ambiguous"):
                ap.enforce_pipeline_approver(conn, "t1", _fp(key), principal, allowed, alias)


def test_simulation_name_case_variant_is_ambiguous(tmp_path):
    assert ap.pipeline_context(tmp_path / "Simulation_Control_Plane.db") == ap.CONTEXT_AMBIGUOUS
