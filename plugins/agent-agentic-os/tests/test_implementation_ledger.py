"""Tests for the plan-to-implementation completeness contract."""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.implementation import validate_implementation_ledger
from agent_control import ControlPlane
from control_plane import policy


def _plan(entries):
    payload = json.dumps(entries, indent=2)
    return f"# Implementation plan\n\n## Implementation Task Ledger\n```json\n{payload}\n```\n"


def test_incomplete_ledger_is_rejected_even_when_artifact_exists(tmp_path):
    artifact = tmp_path / "implemented.py"
    artifact.write_text("# implemented\n", encoding="utf-8")
    plan = tmp_path / "implementation-plan.md"
    plan.write_text(
        _plan([{
            "id": "task-1",
            "status": "PENDING",
            "artifacts": ["implemented.py"],
            "evidence": "pytest -q",
        }]),
        encoding="utf-8",
    )

    error = validate_implementation_ledger(plan, tmp_path)

    assert error is not None
    assert "task-1" in error
    assert "COMPLETE" in error


def test_complete_ledger_requires_evidence_and_existing_artifacts(tmp_path):
    artifact = tmp_path / "implemented.py"
    artifact.write_text("# implemented\n", encoding="utf-8")
    plan = tmp_path / "implementation-plan.md"
    plan.write_text(
        _plan([{
            "id": "task-1",
            "status": "COMPLETE",
            "artifacts": ["implemented.py"],
            "evidence": "pytest -q tests/test_implemented.py",
        }]),
        encoding="utf-8",
    )

    assert validate_implementation_ledger(plan, tmp_path) is None


def test_verify_exit_policy_uses_the_ledger_gate(tmp_path):
    context = tmp_path / "context"
    context.mkdir()
    cp = ControlPlane(db_path=context / "control_plane.db")
    cp.repo_root = tmp_path
    cp.create_task("ledger-task", "Ledger gate", "codex")
    plan = tmp_path / "docs" / "plans" / "ledger-task-implementation-plan.md"
    plan.parent.mkdir(parents=True)
    plan.write_text(
        _plan([{
            "id": "task-1",
            "status": "PENDING",
            "artifacts": ["docs/plans/ledger-task-implementation-plan.md"],
            "evidence": "pytest -q",
        }]),
        encoding="utf-8",
    )

    ctx = cp._build_transition_policy_ctx(
        "ledger-task", cp.get_task("ledger-task"), "VERIFY_EXIT", "RETROSPECTIVE"
    )
    with pytest.raises(policy.PolicyViolation, match="not COMPLETE"):
        policy.evaluate_check("implementation_completeness", ctx)


@pytest.mark.parametrize(
    "entry, expected",
    [
        ({"id": "task-1", "status": "COMPLETE", "artifacts": [], "evidence": "pytest"}, "artifacts"),
        ({"id": "task-1", "status": "COMPLETE", "artifacts": ["missing.py"], "evidence": "pytest"}, "missing"),
        ({"id": "task-1", "status": "COMPLETE", "artifacts": ["ok.py"], "evidence": ""}, "evidence"),
    ],
)
def test_ledger_rejects_missing_completion_proof(tmp_path, entry, expected):
    (tmp_path / "ok.py").write_text("# ok\n", encoding="utf-8")
    plan = tmp_path / "implementation-plan.md"
    plan.write_text(_plan([entry]), encoding="utf-8")

    error = validate_implementation_ledger(plan, tmp_path)

    assert error is not None
    assert expected in error
