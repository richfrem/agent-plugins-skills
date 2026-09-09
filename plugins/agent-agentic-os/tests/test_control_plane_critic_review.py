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


def test_code_review_exit_requires_passing_review_or_explicit_skip():
    """The selected code-review stage must not be an unenforced state sink."""
    template = TransitionRegistry.load_default().get_template(
        "MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT"
    )
    assert template is not None
    assert "code_review_or_skip" in template.deterministic_checks
