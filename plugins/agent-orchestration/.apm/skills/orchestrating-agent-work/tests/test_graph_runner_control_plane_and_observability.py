"""S7 tests (DoD rows 8 & 20, L1, L2, A4, delta 9): graph_runner.py control-plane hook,
3-node parallel observability (`active_nodes`, `--status`, `--progress-file`), and pre-rollback diff save."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path


RUNNER = Path(__file__).resolve().parents[1] / "scripts" / "graph_runner.py"


def _make_git_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True, env=env)
    (repo / "a.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True, env=env)


def _write_fake_verifier(skills_root: Path, exit_code: int) -> Path:
    v = skills_root / "running-control-plane" / "scripts" / "verify_gate_evidence.py"
    v.parent.mkdir(parents=True, exist_ok=True)
    v.write_text(
        f"import json, sys\nprint(json.dumps({{'verified': {exit_code == 0}, 'problems': [] if {exit_code == 0} else ['denied']}}))\nsys.exit({exit_code})\n",
        encoding="utf-8",
    )
    return v


def test_control_plane_gate_hook_passes_fails_and_handles_missing_sibling(tmp_path):
    repo = tmp_path / "repo"
    _make_git_repo(repo)
    manifest = {
        "schema_version": "1.0.0",
        "graph_id": "cp-hook-test",
        "version": "1.0.0",
        "control_plane": {"task_id": "t-demo", "require_approved_signature": True},
        "budget": {"token_ceiling_total": 10000, "max_parallel_concurrency": 2, "max_retries_per_node": 0},
        "nodes": [{
            "id": "r1", "type": "parallel_read", "tier": "deterministic_script",
            "command_or_eval": "echo ok", "input_bindings": [], "output_contract": {},
            "depends_on": [], "failure_escalation": "rollback_and_halt",
        }],
    }
    mpath = tmp_path / "manifest.json"
    mpath.write_text(json.dumps(manifest), encoding="utf-8")

    # 1. Missing sibling verifier -> halts with control_plane_gate_failed
    empty_skills = tmp_path / "empty-skills"
    empty_skills.mkdir()
    run_dir_1 = tmp_path / "runs-1"
    r1 = subprocess.run(
        [sys.executable, str(RUNNER), str(mpath), "--no-workspace", "--run-dir", str(run_dir_1), "--skills-root", str(empty_skills)],
        cwd=repo, capture_output=True, text=True,
    )
    assert r1.returncode == 1
    state1 = json.loads(next(run_dir_1.rglob("state.json")).read_text(encoding="utf-8"))
    assert state1["status"] == "control_plane_gate_failed"

    # 2. Fake verifier exits 1 -> halts with control_plane_gate_failed
    bad_skills = tmp_path / "bad-skills"
    _write_fake_verifier(bad_skills, 1)
    run_dir_2 = tmp_path / "runs-2"
    r2 = subprocess.run(
        [sys.executable, str(RUNNER), str(mpath), "--no-workspace", "--run-dir", str(run_dir_2), "--skills-root", str(bad_skills)],
        cwd=repo, capture_output=True, text=True,
    )
    assert r2.returncode == 1
    state2 = json.loads(next(run_dir_2.rglob("state.json")).read_text(encoding="utf-8"))
    assert state2["status"] == "control_plane_gate_failed"

    # 3. Fake verifier exits 0 -> passes!
    ok_skills = tmp_path / "ok-skills"
    _write_fake_verifier(ok_skills, 0)
    run_dir_3 = tmp_path / "runs-3"
    r3 = subprocess.run(
        [sys.executable, str(RUNNER), str(mpath), "--no-workspace", "--run-dir", str(run_dir_3), "--skills-root", str(ok_skills)],
        cwd=repo, capture_output=True, text=True,
    )
    assert r3.returncode == 0, r3.stdout + r3.stderr


def test_three_parallel_nodes_appear_active_at_once_and_status_and_progress_file_work(tmp_path):
    """DoD row 20 / L1 / L2 / A4: 3 parallel nodes appear in state.json active_nodes simultaneously."""
    repo = tmp_path / "repo"
    _make_git_repo(repo)
    manifest = {
        "schema_version": "1.0.0",
        "graph_id": "obs-parallel-3",
        "version": "1.0.0",
        "budget": {"token_ceiling_total": 10000, "max_parallel_concurrency": 3, "max_retries_per_node": 0},
        "nodes": [
            {
                "id": f"p{i}", "label": f"scout-{i}", "type": "parallel_read", "tier": "deterministic_script",
                "command_or_eval": "sleep 0.6 && echo done", "input_bindings": [], "output_contract": {},
                "depends_on": [], "failure_escalation": "rollback_and_halt",
            }
            for i in (1, 2, 3)
        ],
    }
    mpath = tmp_path / "m3.json"
    mpath.write_text(json.dumps(manifest), encoding="utf-8")
    run_dir = tmp_path / "runs"
    prog = tmp_path / "progress.jsonl"

    proc = subprocess.Popen(
        [sys.executable, str(RUNNER), str(mpath), "--no-workspace", "--run-dir", str(run_dir), "--progress-file", str(prog)],
        cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    saw_three = False
    deadline = time.time() + 10.0
    while proc.poll() is None and time.time() < deadline:
        states = list(run_dir.rglob("state.json"))
        if states:
            try:
                st = json.loads(states[0].read_text(encoding="utf-8"))
                if len(st.get("active_nodes") or []) == 3:
                    saw_three = True
                    break
            except Exception:
                pass
        time.sleep(0.05)

    out, err = proc.communicate(timeout=15)
    assert proc.returncode == 0, out + err
    assert saw_three, "Expected all 3 parallel nodes to appear in active_nodes simultaneously!"

    # Verify --status works on the finished run directory
    actual_run_dir = next(run_dir.rglob("state.json")).parent
    st_cmd = subprocess.run([sys.executable, str(RUNNER), "--status", str(actual_run_dir), "--json"], capture_output=True, text=True)
    assert st_cmd.returncode == 0
    st_json = json.loads(st_cmd.stdout)
    assert st_json["status"] == "success"
    assert st_json["active_nodes"] == []

    # Verify --progress-file recorded node_started and node_finished for all 3 nodes
    events = [json.loads(line) for line in prog.read_text(encoding="utf-8").splitlines() if line.strip()]
    started = {e["node_id"] for e in events if e["event"] == "node_started"}
    finished = {e["node_id"] for e in events if e["event"] == "node_finished"}
    assert started == {"p1", "p2", "p3"}
    assert finished == {"p1", "p2", "p3"}


def test_failed_mutation_saves_diff_before_rollback(tmp_path):
    """Delta 9: save the failed node's git diff into the run directory before rolling back."""
    repo = tmp_path / "repo"
    _make_git_repo(repo)
    manifest = {
        "schema_version": "1.0.0",
        "graph_id": "save-diff-test",
        "version": "1.0.0",
        "budget": {"token_ceiling_total": 10000, "max_parallel_concurrency": 1, "max_retries_per_node": 0},
        "nodes": [
            {
                "id": "approve", "role": "approval", "type": "verifier_gate", "tier": "deterministic_script",
                "command_or_eval": "true", "input_bindings": [], "output_contract": {},
                "depends_on": [], "failure_escalation": "rollback_and_halt",
            },
            {
                "id": "m1", "type": "sequential_mutation", "tier": "deterministic_script",
                "mutation_targets": ["a.txt"],
                "command_or_eval": "echo changed >> a.txt && exit 1",
                "input_bindings": [], "output_contract": {},
                "depends_on": ["approve"], "failure_escalation": "rollback_and_halt",
            },
        ],
    }
    mpath = tmp_path / "m_fail.json"
    mbytes = json.dumps(manifest).encode("utf-8")
    mpath.write_bytes(mbytes)
    import hashlib
    msha = hashlib.sha256(mbytes).hexdigest()
    run_dir = tmp_path / "runs"

    res = subprocess.run(
        [sys.executable, str(RUNNER), str(mpath), "--worktree", str(repo), "--approval", "none", "--expect-manifest-sha256", msha, "--run-dir", str(run_dir)],
        cwd=repo, capture_output=True, text=True,
    )
    assert res.returncode == 1
    # Worktree was rolled back to base
    assert (repo / "a.txt").read_text(encoding="utf-8") == "base\n"
    # Pre-rollback diff was saved!
    patches = list(run_dir.rglob("failed-diff.patch"))
    assert patches, "Expected failed-diff.patch to be saved before rollback!"
    assert "+changed" in patches[0].read_text(encoding="utf-8")
