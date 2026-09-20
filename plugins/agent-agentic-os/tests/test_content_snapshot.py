"""
tests/test_content_snapshot.py
==============================

Purpose:
    Failing-first acceptance tests for T2 (auth-ciba-increment-b, issue #639):
    content-bound `revision_hash` for Gate 1 (AWAITING_APPROVAL -> APPROVED),
    design gap (b) in DEBT-20260918-TRANSITION-REQUEST-DESIGN-GAPS. The approval
    must bind the spec and implementation-plan files actually reviewed, so a change
    to them after the request invalidates the approval. Also covers the
    `transition_request` schema migration adding `challenge_version` and
    `content_snapshot`. Spec section 4 cases 4 and 8 (binding half). Real files in
    tmp_path and real disposable SQLite databases; nothing is mocked. The
    signature, commit-hook and occupancy parts of the approval belong to T3/T4/T6.

Key Input Dependencies:
    - control_plane/snapshot.py (SnapshotEntry, build_snapshot, gate1_artifact_paths,
      compute_revision_hash, snapshot_to_json/from_json, snapshot_matches,
      diff_snapshot, CHALLENGE_VERSION, SnapshotError)
    - control_plane/transition_request.py (create_transition_request,
      verify_and_consume, ContentChanged, ContentBindingRequired)
    - control_plane/adapters.py schema (transition_request columns + migration)

Key Functions (test cases):
    - test_snapshot_hashes_file_bytes_in_stable_order
    - test_snapshot_fails_closed_on_missing_artifact
    - test_snapshot_rejects_symlinked_artifact
    - test_gate1_paths_are_under_work_tasks_folder
    - test_revision_hash_is_deterministic_and_content_sensitive
    - test_revision_hash_without_snapshot_matches_legacy_formula
    - test_snapshot_json_round_trip_and_diff
    - test_create_request_stores_snapshot_and_version
    - test_content_change_after_request_blocks_consumption
    - test_unchanged_content_still_consumes
    - test_snapshot_bound_request_requires_live_snapshot
    - test_legacy_request_without_snapshot_is_unaffected
    - test_fresh_schema_has_snapshot_columns
    - test_legacy_database_is_migrated_without_data_loss
"""

import hashlib
import json
import secrets
import sqlite3
import sys
from pathlib import Path

import pytest

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from agent_control import ControlPlane
from control_plane.snapshot import (
    CHALLENGE_VERSION,
    SnapshotEntry,
    SnapshotError,
    build_snapshot,
    compute_revision_hash,
    diff_snapshot,
    gate1_artifact_paths,
    snapshot_from_json,
    snapshot_matches,
    snapshot_to_json,
)
from control_plane.transition_request import (
    ContentBindingRequired,
    ContentChanged,
    create_transition_request,
    issue_stub_token,
    verify_and_consume,
)

TASK = "snapshot-task-001"


@pytest.fixture
def plan_files(tmp_path):
    """Spec and plan files in the work-tasks folder layout, under a fake repo root."""
    folder = tmp_path / "repo" / "docs" / "plans" / "work-tasks" / TASK
    folder.mkdir(parents=True)
    spec = folder / f"{TASK}-spec.md"
    plan = folder / f"{TASK}-implementation-plan.md"
    spec.write_text("# spec v1\n")
    plan.write_text("# plan v1\n")
    return {"root": tmp_path / "repo", "spec": spec, "plan": plan}


@pytest.fixture
def db_and_task(tmp_path):
    db_path = tmp_path / "control_plane.db"
    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    cp.create_task(task_id=TASK, title="Snapshot test", runtime_tool="test")
    return sqlite3.connect(db_path), db_path


def _snapshot(plan_files):
    return build_snapshot(gate1_artifact_paths(plan_files["root"], TASK))


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_snapshot_hashes_file_bytes_in_stable_order(plan_files):
    snap = _snapshot(plan_files)
    assert [e.label for e in snap] == ["spec", "plan"]
    assert snap[0].sha256 == _sha(plan_files["spec"])
    assert snap[1].sha256 == _sha(plan_files["plan"])
    assert all(isinstance(e, SnapshotEntry) for e in snap)


def test_snapshot_fails_closed_on_missing_artifact(plan_files):
    plan_files["plan"].unlink()
    with pytest.raises(SnapshotError):
        _snapshot(plan_files)


def test_snapshot_rejects_symlinked_artifact(plan_files, tmp_path):
    """A symlinked artifact could be redirected after review; fail closed."""
    other = tmp_path / "other.md"
    other.write_text("# elsewhere\n")
    plan_files["spec"].unlink()
    plan_files["spec"].symlink_to(other)
    with pytest.raises(SnapshotError):
        _snapshot(plan_files)


def test_gate1_paths_are_under_work_tasks_folder(plan_files):
    paths = dict(gate1_artifact_paths(plan_files["root"], TASK))
    assert paths["spec"] == plan_files["spec"]
    assert paths["plan"] == plan_files["plan"]
    assert "work-tasks" in str(paths["spec"])


def test_revision_hash_is_deterministic_and_content_sensitive(plan_files):
    snap = _snapshot(plan_files)
    base = compute_revision_hash(TASK, "AWAITING_APPROVAL", "APPROVED", 7, "nonce-a", snap)
    assert base == compute_revision_hash(TASK, "AWAITING_APPROVAL", "APPROVED", 7, "nonce-a", snap)
    assert len(base) == 64

    for change in (
        dict(nonce="nonce-b"),
        dict(occupancy=8),
        dict(to_state="DONE"),
    ):
        args = dict(task=TASK, frm="AWAITING_APPROVAL", to_state="APPROVED", occupancy=7, nonce="nonce-a")
        args.update(change)
        other = compute_revision_hash(
            args["task"], args["frm"], args["to_state"], args["occupancy"], args["nonce"], snap
        )
        assert other != base

    plan_files["spec"].write_text("# spec v2\n")
    assert compute_revision_hash(TASK, "AWAITING_APPROVAL", "APPROVED", 7, "nonce-a", _snapshot(plan_files)) != base
    plan_files["spec"].write_text("# spec v1\n")
    plan_files["plan"].write_text("# plan v2\n")
    assert compute_revision_hash(TASK, "AWAITING_APPROVAL", "APPROVED", 7, "nonce-a", _snapshot(plan_files)) != base


def test_revision_hash_without_snapshot_matches_legacy_formula():
    """Increment A callers pass no snapshot; their hash must not change."""
    legacy = hashlib.sha256(f"{TASK}:AWAITING_APPROVAL:APPROVED:7:nonce-a".encode("utf-8")).hexdigest()
    assert compute_revision_hash(TASK, "AWAITING_APPROVAL", "APPROVED", 7, "nonce-a", None) == legacy


def test_snapshot_json_round_trip_and_diff(plan_files):
    snap = _snapshot(plan_files)
    text = snapshot_to_json(snap)
    assert json.loads(text)[0]["label"] == "spec"
    assert snapshot_from_json(text) == snap
    assert snapshot_matches(text, snap)

    plan_files["plan"].write_text("# plan changed\n")
    changed = _snapshot(plan_files)
    assert not snapshot_matches(text, changed)
    assert diff_snapshot(text, changed) == ["plan"]


def test_create_request_stores_snapshot_and_version(db_and_task, plan_files):
    conn, _ = db_and_task
    snap = _snapshot(plan_files)
    record = create_transition_request(
        conn, task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, content_snapshot=snap,
    )
    row = conn.execute(
        "SELECT revision_hash, challenge_version, content_snapshot FROM transition_request WHERE request_id = ?",
        (record.request_id,),
    ).fetchone()
    assert row[1] == CHALLENGE_VERSION == "control-plane-challenge/1"
    assert snapshot_from_json(row[2]) == snap
    assert row[0] == compute_revision_hash(TASK, "AWAITING_APPROVAL", "APPROVED", 1, record.nonce, snap)
    assert record.revision_hash == row[0]


def test_content_change_after_request_blocks_consumption(db_and_task, plan_files):
    conn, _ = db_and_task
    secret = secrets.token_bytes(32)
    record = create_transition_request(
        conn, task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, content_snapshot=_snapshot(plan_files),
    )
    token = issue_stub_token(record, secret)

    plan_files["spec"].write_text("# spec edited after the request\n")
    with pytest.raises(ContentChanged) as excinfo:
        verify_and_consume(
            conn, task_id=TASK, token=token, secret=secret, live_snapshot=_snapshot(plan_files)
        )
    assert "spec" in str(excinfo.value)
    status = conn.execute(
        "SELECT status FROM transition_request WHERE request_id = ?", (record.request_id,)
    ).fetchone()[0]
    assert status == "PENDING"


def test_unchanged_content_still_consumes(db_and_task, plan_files):
    conn, _ = db_and_task
    secret = secrets.token_bytes(32)
    record = create_transition_request(
        conn, task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, content_snapshot=_snapshot(plan_files),
    )
    token = issue_stub_token(record, secret)
    result = verify_and_consume(
        conn, task_id=TASK, token=token, secret=secret, live_snapshot=_snapshot(plan_files)
    )
    assert result.status == "CONSUMED"


def test_snapshot_bound_request_requires_live_snapshot(db_and_task, plan_files):
    """Fail closed: a request bound to content cannot be consumed without re-checking it."""
    conn, _ = db_and_task
    secret = secrets.token_bytes(32)
    record = create_transition_request(
        conn, task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED",
        occupancy_id=1, content_snapshot=_snapshot(plan_files),
    )
    token = issue_stub_token(record, secret)
    with pytest.raises(ContentBindingRequired):
        verify_and_consume(conn, task_id=TASK, token=token, secret=secret)
    status = conn.execute(
        "SELECT status FROM transition_request WHERE request_id = ?", (record.request_id,)
    ).fetchone()[0]
    assert status == "PENDING"


def test_legacy_request_without_snapshot_is_unaffected(db_and_task):
    conn, _ = db_and_task
    secret = secrets.token_bytes(32)
    record = create_transition_request(
        conn, task_id=TASK, from_state="AWAITING_APPROVAL", to_state="APPROVED", occupancy_id=1,
    )
    row = conn.execute(
        "SELECT challenge_version, content_snapshot FROM transition_request WHERE request_id = ?",
        (record.request_id,),
    ).fetchone()
    assert row == (None, None)
    token = issue_stub_token(record, secret)
    assert verify_and_consume(conn, task_id=TASK, token=token, secret=secret).status == "CONSUMED"


def test_fresh_schema_has_snapshot_columns(db_and_task):
    conn, _ = db_and_task
    cols = {r[1] for r in conn.execute("PRAGMA table_info(transition_request)").fetchall()}
    assert {"challenge_version", "content_snapshot"} <= cols


def test_legacy_database_is_migrated_without_data_loss(tmp_path):
    """A pre-T2 database (transition_request without the new columns) gains them, keeps
    its rows, and a second init_db() is a no-op."""
    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE transition_request (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            from_state TEXT NOT NULL,
            to_state TEXT NOT NULL,
            occupancy_id INTEGER NOT NULL,
            nonce TEXT NOT NULL UNIQUE,
            expiration REAL NOT NULL,
            revision_hash TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            jti TEXT,
            consumed_at REAL,
            created_at REAL NOT NULL
        );
        INSERT INTO transition_request
            (task_id, from_state, to_state, occupancy_id, nonce, expiration, revision_hash, created_at)
        VALUES ('legacy-task', 'AWAITING_APPROVAL', 'APPROVED', 1, 'legacy-nonce', 9e9, 'abc', 1.0);
        """
    )
    conn.commit()
    conn.close()

    cp = ControlPlane(db_path=db_path)
    cp.init_db()
    cp.init_db()  # idempotent

    conn = sqlite3.connect(db_path)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(transition_request)").fetchall()}
    assert {"challenge_version", "content_snapshot"} <= cols
    row = conn.execute(
        "SELECT nonce, revision_hash, challenge_version, content_snapshot FROM transition_request"
    ).fetchone()
    assert row == ("legacy-nonce", "abc", None, None)
