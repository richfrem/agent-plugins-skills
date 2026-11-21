"""S7 tests (DoD row 8 & 15, sec-2-1, sec-2-2): verify_task_approved and verify_gate_evidence.py --gate APPROVED."""

from __future__ import annotations

import hashlib
import io
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

from agent_control import ControlPlane
from control_plane.coordinator import TransitionCoordinator
from control_plane.gate_evidence import verify_task_approved
from control_plane.identity_layout import default_layout
from control_plane.registry import TransitionRegistry
from helpers.human_signer import get_test_human


VERIFIER = Path(__file__).resolve().parents[1] / "scripts" / "verify_gate_evidence.py"


def _setup_approved_real_repo(tmp_path: Path, task_id: str, manifest_sha: str, *, mode: str = "plan-pin") -> Path:
    repo = tmp_path / "repo"
    (repo / "context" / "identity").mkdir(parents=True)
    db = repo / "context" / "control_plane.db"
    cp = ControlPlane(db_path=db)
    cp.init_db()
    cp.repo_root = repo
    cp.create_task(task_id, "S7 verify test", "claude")

    # Enroll real human test key into repo's allowed_signers
    human = get_test_human()
    human.ensure_identity(repo)

    reg = TransitionRegistry.load_default()

    # INTAKE -> DRAFT_PLAN
    TransitionCoordinator(
        cp, registry=reg, input_fn=lambda _p: "1", output_stream=io.StringIO(),
    ).coordinate_transition(task_id=task_id, to_state="DRAFT_PLAN", actor="human", reason="outline", interactive=True)

    # Write spec + plan (with Manifest SHA-256 pin if plan-pin, or graph manifest if manifest)
    task_dir = repo / "docs" / "plans" / "work-tasks" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / f"{task_id}-spec.md").write_text("# Spec\n", encoding="utf-8")
    if mode == "plan-pin":
        (task_dir / f"{task_id}-implementation-plan.md").write_text(
            f"# Plan\n\n- Strategy: direct\n\nManifest SHA-256: {manifest_sha}\n",
            encoding="utf-8",
        )
    else:
        (task_dir / f"{task_id}-implementation-plan.md").write_text("# Plan\n\n- Strategy: direct\n", encoding="utf-8")

    # DRAFT_PLAN -> PLAN_REVIEW
    TransitionCoordinator(
        cp, registry=reg, output_stream=io.StringIO(),
    ).coordinate_transition(task_id=task_id, to_state="PLAN_REVIEW", actor="agent", reason="submit", interactive=False)

    # PLAN_REVIEW -> APPROVED (signed by real human test key)
    TransitionCoordinator(
        cp, registry=reg, output_stream=io.StringIO(), human_signer=human.sign_request,
    ).coordinate_transition(task_id=task_id, to_state="APPROVED", actor="human", reason="approve", interactive=True)

    return repo


def test_verify_task_approved_plan_pin_pass_wrong_sha_and_missing_binding(tmp_path):
    good_sha = hashlib.sha256(b'{"graph_id":"demo"}').hexdigest()
    wrong_sha = hashlib.sha256(b'{"graph_id":"other"}').hexdigest()
    repo = _setup_approved_real_repo(tmp_path, "t-s7-1", good_sha, mode="plan-pin")

    # 1. Valid plan-pin passes (API and CLI)
    problems, binding = verify_task_approved(repo, "t-s7-1", manifest_sha256=good_sha)
    assert problems == [], problems
    assert binding == "plan-pin"

    cli_ok = subprocess.run(
        [sys.executable, str(VERIFIER), "--repo-root", str(repo), "--task-id", "t-s7-1", "--gate", "APPROVED", "--manifest-sha256", good_sha, "--json"],
        capture_output=True, text=True,
    )
    assert cli_ok.returncode == 0, cli_ok.stdout + cli_ok.stderr
    assert json.loads(cli_ok.stdout)["verified"] is True

    # 2. Wrong manifest SHA fails (exit 1)
    cli_bad = subprocess.run(
        [sys.executable, str(VERIFIER), "--repo-root", str(repo), "--task-id", "t-s7-1", "--gate", "APPROVED", "--manifest-sha256", wrong_sha, "--json"],
        capture_output=True, text=True,
    )
    assert cli_bad.returncode == 1
    assert json.loads(cli_bad.stdout)["verified"] is False

    # 3. Missing approver binding is a refusal (sec-2-2)
    conn = sqlite3.connect(str(repo / "context" / "control_plane.db"))
    conn.execute("DELETE FROM task_approver_binding WHERE task_id = 't-s7-1'")
    conn.commit()
    conn.close()
    problems_nb, _ = verify_task_approved(repo, "t-s7-1", manifest_sha256=good_sha)
    assert any("approver binding" in p.lower() for p in problems_nb)

    # 4. Missing DB -> CLI exit 3
    cli_missing = subprocess.run(
        [sys.executable, str(VERIFIER), "--repo-root", str(tmp_path / "nope"), "--task-id", "t-s7-1", "--gate", "APPROVED", "--json"],
        capture_output=True, text=True,
    )
    assert cli_missing.returncode == 3
