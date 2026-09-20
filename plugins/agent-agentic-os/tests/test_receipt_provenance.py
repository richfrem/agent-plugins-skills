"""
tests/test_receipt_provenance.py
================================

Purpose:
    Failing-first contract tests for T15 (auth-ciba-increment-b, issue #639): receipt provenance,
    an append-only `receipt_audit` trail, human-only `invalidate-receipt`, and a human-only
    interactive `record-review-skip`. Regression for the 2026-09-19 incident, where an agent recorded
    a review-skip receipt (`--actor human`, quoting chat as `--human-confirmed`) on the human's behalf.
    Real SQLite and real files; the terminal is injected (tty_fn/input_fn), nothing is mocked.

Key Input Dependencies:
    - control_plane/receipt_provenance.py (record_human_skip, invalidate_receipt, receipt_history)
    - control_plane/adapters.py (receipt_audit table, provenance columns, invalidated receipts ignored)
    - agent_control.py (_build_parser: record-review-skip --interactive, invalidate-receipt)
    - tests/helpers/gate1_fixtures.py

Key Functions (test cases):
    - test_every_receipt_gets_a_created_audit_row_with_provenance
    - test_receipt_audit_is_append_only
    - test_audit_survives_receipt_deletion_on_occupancy_exit
    - test_human_skip_refuses_without_a_terminal_and_records_nothing
    - test_human_skip_records_provenance_human_interactive
    - test_human_skip_requires_typed_confirmation
    - test_invalidate_receipt_is_human_only_and_audited
    - test_invalidated_receipt_no_longer_satisfies_the_gate
    - test_cli_registers_the_verbs_and_skip_requires_interactive
"""

import io
import sqlite3
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

import agent_control
from control_plane.receipt_provenance import ReceiptError, invalidate_receipt, receipt_history, record_human_skip
from helpers.gate1_fixtures import reach_awaiting_approval

TASK = "receipt-task-001"


@pytest.fixture
def cp(tmp_path):
    return reach_awaiting_approval(tmp_path, TASK).control_plane


def _db(cp):
    return sqlite3.connect(cp.db_path)


def _out():
    lines = []
    return lines, (lambda s="": lines.append(str(s)))


def _answers(*values):
    feed = iter(values)
    return lambda _prompt="": next(feed, "")


def test_every_receipt_gets_a_created_audit_row_with_provenance(cp):
    cp.record_review_skip(TASK, "multi_agent_review", "agent", "test")
    rows = _db(cp).execute(
        "SELECT event, provenance, gate_name FROM receipt_audit WHERE task_id = ? AND gate_name = 'multi_agent_review_skipped'", (TASK,)
    ).fetchall()
    assert rows == [("created", "api", "multi_agent_review_skipped")]


def test_receipt_audit_is_append_only(cp):
    cp.record_review_skip(TASK, "multi_agent_review", "agent", "test")
    conn = _db(cp)
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("UPDATE receipt_audit SET event = 'x'")
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DELETE FROM receipt_audit")


def test_audit_survives_receipt_deletion_on_occupancy_exit(cp):
    cp.record_review_skip(TASK, "multi_agent_review", "agent", "test")
    conn = _db(cp)
    conn.execute("DELETE FROM verification_receipts WHERE gate_name = 'multi_agent_review_skipped'")
    conn.commit()
    left = conn.execute("SELECT COUNT(*) FROM receipt_audit WHERE gate_name = 'multi_agent_review_skipped'").fetchone()[0]
    assert left == 1


def test_human_skip_refuses_without_a_terminal_and_records_nothing(cp):
    lines, out = _out()
    with pytest.raises(ReceiptError) as excinfo:
        record_human_skip(cp, TASK, "multi_agent_review", "no review", tty_fn=lambda: False, input_fn=_answers("multi_agent_review"), out=out)
    assert "terminal" in str(excinfo.value).lower()
    assert not cp._persistence.has_receipt(TASK, "multi_agent_review_skipped")


def test_human_skip_requires_typed_confirmation(cp):
    lines, out = _out()
    with pytest.raises(ReceiptError):
        record_human_skip(cp, TASK, "multi_agent_review", "no review", tty_fn=lambda: True, input_fn=_answers("nope"), out=out)
    assert not cp._persistence.has_receipt(TASK, "multi_agent_review_skipped")


def test_human_skip_records_provenance_human_interactive(cp):
    lines, out = _out()
    token = record_human_skip(cp, TASK, "multi_agent_review", "no review", tty_fn=lambda: True, input_fn=_answers("multi_agent_review"), out=out)
    assert token.startswith("EVO-INTEGRITY-")
    row = _db(cp).execute(
        "SELECT provenance, actor FROM receipt_audit WHERE task_id = ? AND event = 'created' AND gate_name = 'multi_agent_review_skipped'", (TASK,)
    ).fetchone()
    assert row == ("human-interactive", "human")


def test_invalidate_receipt_is_human_only_and_audited(cp):
    cp.record_review_skip(TASK, "multi_agent_review", "agent", "test")
    receipt_id = _db(cp).execute("SELECT receipt_id FROM verification_receipts WHERE gate_name = 'multi_agent_review_skipped'").fetchone()[0]
    lines, out = _out()
    with pytest.raises(ReceiptError):
        invalidate_receipt(cp, receipt_id, "agent forged it", tty_fn=lambda: False, input_fn=_answers(str(receipt_id)), out=out)
    invalidate_receipt(cp, receipt_id, "agent forged it", tty_fn=lambda: True, input_fn=_answers(str(receipt_id)), out=out)
    events = [(h["event"], h["actor"]) for h in receipt_history(_db(cp), TASK) if h["gate_name"] == "multi_agent_review_skipped"]
    assert events == [("created", "agent"), ("invalidated", "human")]


def test_invalidated_receipt_no_longer_satisfies_the_gate(cp):
    cp.record_review_skip(TASK, "multi_agent_review", "agent", "test")
    assert cp._persistence.has_receipt(TASK, "multi_agent_review_skipped")
    receipt_id = _db(cp).execute("SELECT receipt_id FROM verification_receipts WHERE gate_name = 'multi_agent_review_skipped'").fetchone()[0]
    lines, out = _out()
    invalidate_receipt(cp, receipt_id, "forged", tty_fn=lambda: True, input_fn=_answers(str(receipt_id)), out=out)
    assert not cp._persistence.has_receipt(TASK, "multi_agent_review_skipped")
    assert cp._persistence.count_receipts(TASK, "multi_agent_review_skipped") == 0


def test_cli_registers_the_verbs_and_skip_requires_interactive():
    parser = agent_control._build_parser()
    args = parser.parse_args(["invalidate-receipt", "--receipt-id", "7", "--reason", "x"])
    assert args.receipt_id == 7
    skip = parser.parse_args(["record-review-skip", "--task-id", "t", "--phase", "multi_agent_review", "--reason", "x", "--interactive"])
    assert skip.interactive is True
    with pytest.raises(SystemExit) as excinfo:
        agent_control._require_human_interactive_skip(parser.parse_args(["record-review-skip", "--task-id", "t", "--phase", "p", "--reason", "x"]))
    assert "interactive" in str(excinfo.value).lower()
