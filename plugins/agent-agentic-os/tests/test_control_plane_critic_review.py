"""Task 6 contract tests for canonical critic verdict recording."""

import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane, _build_parser, _dispatch_command
from control_plane.registry import TransitionRegistry
from control_plane.constants import (
    STATE_MULTI_AGENT_CODE_REVIEW, STATE_VERIFY_EXIT,
)


@pytest.fixture
def control_plane(tmp_path):
    control_plane = ControlPlane(db_path=tmp_path / "control_plane.db")
    control_plane.init_db()
    return control_plane


def test_cli_dispatch_persists_canonical_revise_and_reports_it(control_plane, capsys):
    task_id = "critic-cli-001"
    control_plane.create_task(task_id=task_id, title="Critic", runtime_tool="codex")
    args = _build_parser().parse_args([
        "record-critic-review",
        "--task-id", task_id,
        "--iteration", "1",
        "--model", "gpt-5-mini",
        "--verdict", "REQUEST_CHANGES",
        "--findings", "Revise the scope.",
        "--human-confirmed", "HUMAN-CONFIRMED: test fixture",
    ])

    _dispatch_command(control_plane, args)

    output = capsys.readouterr().out
    assert "verdict=REVISE" in output
    with sqlite3.connect(control_plane.db_path) as conn:
        assert conn.execute(
            "SELECT verdict FROM critic_reviews WHERE task_id = ?", (task_id,)
        ).fetchone()[0] == "REVISE"


def test_only_pass_satisfies_critic_approval_gate(control_plane):
    task_id = "critic-gate-001"
    control_plane.create_task(task_id=task_id, title="Critic", runtime_tool="codex")
    control_plane.record_critic_review(task_id, 1, "gpt-5-mini", "REVISE", "Needs changes")
    assert control_plane._persistence.has_passing_critic_review(task_id) is False

    control_plane.record_critic_review(task_id, 2, "gpt-5-mini", "PASS", "Approved")
    assert control_plane._persistence.has_passing_critic_review(task_id) is True


def test_undeclared_critic_verdict_is_rejected(control_plane):
    task_id = "critic-invalid-001"
    control_plane.create_task(task_id=task_id, title="Critic", runtime_tool="codex")
    with pytest.raises(ValueError, match="Invalid verdict"):
        control_plane.record_critic_review(task_id, 1, "gpt-5-mini", "APPROVE", "bad")


def test_code_review_exit_requires_a_passing_review_and_a_human_signature_never_a_skip():
    """The selected code-review stage must not be an unenforced state sink, and (auth-ciba-increment-b) it has no
    skip: the edge keeps the passing-review check and the human's signed acceptance, and the old
    code_review_or_skip receipt path (which an agent could satisfy by recording a skip) is gone."""
    registry = TransitionRegistry.load_default()
    template = registry.get_template(STATE_MULTI_AGENT_CODE_REVIEW, STATE_VERIFY_EXIT)
    assert template is not None
    assert "critic_review_pass" in template.deterministic_checks
    assert "code_review_or_skip" not in template.deterministic_checks
    assert (STATE_MULTI_AGENT_CODE_REVIEW, STATE_VERIFY_EXIT) in registry.proof_required_edges()
