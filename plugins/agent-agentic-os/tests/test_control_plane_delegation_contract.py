"""Contract tests for governed delegation plans and execution receipts."""

import sys
import sqlite3
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane
from control_plane.policy import DelegationContractError


def contract(**overrides):
    value = {
        "objective": "Review the implementation for correctness",
        "scope": ["plugins/agent-agentic-os/**"],
        "authority": {"read": True, "write": False, "commit": False},
        "tool_limits": ["Read", "Bash"],
        "budget": {"max_requests": 2, "cost_tier": "medium"},
        "artifacts": ["review.md"],
        "verifier": {"command": "pytest -q", "required_receipt": True},
        "escalation": {"on_failure": "human", "on_budget_exhaustion": "human"},
        "fallback_candidates": [{"backend": "claude", "model_id": "haiku", "cost_tier": "low", "capability_class": "review"}],
        "backend": "codex",
        "model_id": "gpt-5-mini",
        "cost_tier": "medium",
        "capability_class": "review",
    }
    value.update(overrides)
    return value


@pytest.fixture
def cp(tmp_path):
    control_plane = ControlPlane(db_path=tmp_path / "control_plane.db")
    control_plane.init_db()
    control_plane.create_task("delegation-task", "Delegation contract", "codex")
    return control_plane


def test_delegation_contract_is_persisted_and_requires_approval_for_write_or_high_cost(cp):
    contract_id = cp.create_delegation_plan("delegation-task", contract(
        authority={"read": True, "write": True, "commit": False},
        cost_tier="high",
        budget={"max_requests": 1, "cost_tier": "high"},
    ))
    saved = cp.get_delegation_plan(contract_id)
    assert saved["status"] == "PENDING_APPROVAL"
    assert saved["objective"] == "Review the implementation for correctness"
    with pytest.raises(DelegationContractError, match="approval"):
        cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="high", capability_class="review")

    cp.approve_delegation_plan(contract_id, actor="human")
    receipt_id = cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="high", capability_class="review", write_capable=True)
    assert receipt_id > 0


def test_unavailable_backend_is_rejected(cp):
    contract_id = cp.create_delegation_plan("delegation-task", contract())
    with pytest.raises(DelegationContractError, match="unavailable"):
        cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="medium", capability_class="review", backend_available=False)


def test_budget_exhaustion_is_rejected(cp):
    contract_id = cp.create_delegation_plan("delegation-task", contract(budget={"max_requests": 1, "cost_tier": "medium"}))
    cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="medium", capability_class="review")
    with pytest.raises(DelegationContractError, match="budget"):
        cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="medium", capability_class="review")


def test_out_of_scope_write_is_rejected(cp):
    contract_id = cp.create_delegation_plan("delegation-task", contract(
        authority={"read": True, "write": True, "commit": False},
        scope=["docs/**"],
    ))
    cp.approve_delegation_plan(contract_id, actor="human")
    with pytest.raises(DelegationContractError, match="scope"):
        cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="medium", capability_class="review", written_paths=["src/main.py"])


def test_result_requires_receipt_and_verifier_receipt(cp):
    contract_id = cp.create_delegation_plan("delegation-task", contract())
    with pytest.raises(DelegationContractError, match="receipt"):
        cp.accept_delegation_result(contract_id)
    cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="medium", capability_class="review")
    with pytest.raises(DelegationContractError, match="verifier"):
        cp.accept_delegation_result(contract_id)
    cp.record_delegation_verifier_receipt(contract_id, command="pytest -q", exit_code=0)
    assert cp.accept_delegation_result(contract_id)["status"] == "ACCEPTED"


def test_fallback_substitution_requires_renewed_approval_when_capability_changes(cp):
    contract_id = cp.create_delegation_plan("delegation-task", contract())
    cp.record_delegation_receipt(contract_id, backend="codex", model_id="gpt-5-mini", cost_tier="medium", capability_class="review")
    with pytest.raises(DelegationContractError, match="renewed approval"):
        cp.record_delegation_receipt(contract_id, backend="claude", model_id="haiku", cost_tier="high", capability_class="review")
    assert cp.get_delegation_plan(contract_id)["status"] == "PENDING_APPROVAL"


def test_delegation_schema_is_idempotent_and_raw_state_write_remains_blocked(cp):
    cp.init_db()
    cp.init_db()
    conn = sqlite3.connect(cp.db_path)
    try:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        assert {"delegation_contracts", "delegation_receipts", "delegation_verifier_receipts"} <= tables
        conn.execute("UPDATE tasks SET state = 'DONE' WHERE task_id = ?", ("delegation-task",))
        conn.commit()
        state = conn.execute("SELECT state FROM tasks WHERE task_id = ?", ("delegation-task",)).fetchone()[0]
        assert state == "INTAKE"
        assert conn.execute("SELECT COUNT(*) FROM transition_violations WHERE task_id = ?", ("delegation-task",)).fetchone()[0] >= 1
    finally:
        conn.close()
