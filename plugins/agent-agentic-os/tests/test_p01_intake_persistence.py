"""P01 persistence contracts for scoped premium consent and source-assisted answers."""

import sqlite3
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane
from control_plane.adapters import CURRENT_SCHEMA_VERSION
from control_plane.ports import PersistenceInvariantViolation


def _control_plane_with_task(tmp_path):
    control_plane = ControlPlane(db_path=tmp_path / "control_plane.db")
    control_plane.create_task("p01-task", "P01 persistence", "codex")
    return control_plane


def test_v9_migration_persists_scoped_consent_and_candidate_provenance(tmp_path):
    control_plane = _control_plane_with_task(tmp_path)
    db_path = control_plane.db_path

    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("UPDATE schema_version SET version = 8")
        conn.commit()
    finally:
        conn.close()

    control_plane.init_db()
    control_plane.record_premium_consent(
        task_id="p01-task",
        stage="interview",
        round_id="round-1",
        model_id="premium-model",
        actor="human",
    )
    candidate_id = control_plane.record_source_assisted_answer_candidate(
        task_id="p01-task",
        stage="interview",
        round_id="round-1",
        question_id="scope",
        answer="P01 only",
        source_path="docs/brief.md",
    )

    conn = sqlite3.connect(str(db_path))
    try:
        assert conn.execute("SELECT version FROM schema_version").fetchone()[0] == 9
        assert CURRENT_SCHEMA_VERSION == 9
        assert conn.execute(
            "SELECT stage, round_id, model_id, actor FROM premium_consents"
        ).fetchone() == ("interview", "round-1", "premium-model", "human")
        assert conn.execute(
            "SELECT question_id, answer, source_path, confirmation_status "
            "FROM source_assisted_answer_candidates WHERE candidate_id = ?",
            (candidate_id,),
        ).fetchone() == ("scope", "P01 only", "docs/brief.md", "pending")
    finally:
        conn.close()


def test_premium_consent_is_denied_outside_its_exact_stage_and_round(tmp_path):
    control_plane = _control_plane_with_task(tmp_path)
    control_plane.record_premium_consent(
        task_id="p01-task",
        stage="interview",
        round_id="round-1",
        model_id="premium-model",
        actor="human",
    )

    control_plane.require_premium_consent("p01-task", "interview", "round-1", "premium-model")

    with pytest.raises(PersistenceInvariantViolation, match="stage='plan', round_id='round-1'"):
        control_plane.require_premium_consent("p01-task", "plan", "round-1", "premium-model")

    with pytest.raises(PersistenceInvariantViolation, match="stage='interview', round_id='round-2'"):
        control_plane.require_premium_consent("p01-task", "interview", "round-2", "premium-model")


def test_unconfirmed_source_candidate_blocks_interview_exit_until_human_confirmed(tmp_path):
    control_plane = _control_plane_with_task(tmp_path)
    candidate_id = control_plane.record_source_assisted_answer_candidate(
        task_id="p01-task",
        stage="interview",
        round_id="round-1",
        question_id="scope",
        answer="P01 only",
        source_path="docs/brief.md",
    )

    with pytest.raises(PersistenceInvariantViolation, match="unconfirmed source-assisted answer candidate"):
        control_plane.assert_interview_exit_ready("p01-task", "interview", "round-1")

    control_plane.confirm_source_assisted_answer_candidate(candidate_id, actor="human")

    control_plane.assert_interview_exit_ready("p01-task", "interview", "round-1")
