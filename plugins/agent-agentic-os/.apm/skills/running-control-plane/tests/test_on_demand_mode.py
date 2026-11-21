"""S6 tests (DoD rows 5 & 6, G5): on-demand mode toggle, status, active_jobs, and guard matrix."""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from pathlib import Path

from agent_control import ControlPlane
from helpers.control_plane_repo import make_repo, run_mode


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
PRE_COMMIT = SCRIPTS_DIR / "pre-commit-pipeline-guard"
PRE_PUSH = SCRIPTS_DIR / "pre-push-review-guard"


def _init_git_branch(repo: Path, branch: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    if not (repo / ".git").exists():
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True, env=env)
    (repo / "README.md").write_text("hi\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "-b", branch], check=True, env=env)
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def _run_guard(script: Path, repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(script)], cwd=repo, capture_output=True, text=True)


def test_control_plane_mode_on_demand_and_status_json(tmp_path):
    root = make_repo(tmp_path)
    # Replace pretend DB bytes with a real SQLite DB
    db = root / "context" / "control_plane.db"
    db.unlink()
    cp = ControlPlane(db_path=db)
    cp.init_db()
    cp.create_task("t-active-1", "Active job", "claude")

    r = run_mode(root, "on-demand", "--yes")
    assert r.returncode == 0, r.stdout + r.stderr
    assert (root / "context" / "control-plane-mode").read_text(encoding="utf-8").strip() == "on-demand"

    st = run_mode(root, "status", "--json")
    assert st.returncode == 0, st.stdout + st.stderr
    data = json.loads(st.stdout)
    assert data["mode"] == "on-demand"
    assert data["consistent"] is True
    assert len(data["active_jobs"]) == 1
    assert data["active_jobs"][0]["task_id"] == "t-active-1"


def test_on_demand_guard_matrix(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    head_sha = _init_git_branch(repo, "feat/unregistered")
    (repo / "context").mkdir()
    (repo / "context" / "control-plane-mode").write_text("on-demand\n", encoding="utf-8")

    # 1. Missing DB -> fail closed in both guards
    for g in (PRE_COMMIT, PRE_PUSH):
        res = _run_guard(g, repo)
        assert res.returncode == 1
        assert "fail closed" in (res.stdout + res.stderr).lower()

    # 2. Corrupt DB -> fail closed
    db = repo / "context" / "control_plane.db"
    db.write_bytes(b"not a sqlite file")
    for g in (PRE_COMMIT, PRE_PUSH):
        res = _run_guard(g, repo)
        assert res.returncode == 1

    # 3. Symlinked DB -> fail closed
    real_elsewhere = tmp_path / "other.db"
    real_elsewhere.write_bytes(b"x")
    db.unlink()
    db.symlink_to(real_elsewhere)
    for g in (PRE_COMMIT, PRE_PUSH):
        assert _run_guard(g, repo).returncode == 1
    db.unlink()

    # 4. Valid real-stamped DB + unregistered branch -> passes both guards with info line
    cp = ControlPlane(db_path=db)
    cp.init_db()
    for g in (PRE_COMMIT, PRE_PUSH):
        res = _run_guard(g, repo)
        assert res.returncode == 0, res.stdout + res.stderr
        assert "unregistered" in res.stderr.lower()

    # 5. Unknown mode -> fails closed
    (repo / "context" / "control-plane-mode").write_text("bogus-mode\n", encoding="utf-8")
    for g in (PRE_COMMIT, PRE_PUSH):
        assert _run_guard(g, repo).returncode == 1
    (repo / "context" / "control-plane-mode").write_text("on-demand\n", encoding="utf-8")

    # 6. Registered ESCALATED task -> gated (blocked)
    cp.create_task("t-esc", "Escalated", "claude")
    conn = sqlite3.connect(str(db))
    conn.execute("UPDATE tasks SET worktree_branch = 'feat/unregistered' WHERE task_id = 't-esc'")
    conn.commit()
    conn.close()
    assert _run_guard(PRE_PUSH, repo).returncode == 1

    # 7. ROLLED_BACK clean (tip == rollback_base_sha) passes; dirty (NULL or different SHA) blocks
    conn = sqlite3.connect(str(db))
    conn.execute("DROP TRIGGER IF EXISTS enforce_valid_transition")
    conn.execute("UPDATE tasks SET state = 'ROLLED_BACK', rollback_base_sha = ? WHERE task_id = 't-esc'", (head_sha,))
    conn.commit()
    conn.close()
    assert _run_guard(PRE_COMMIT, repo).returncode == 0
    assert _run_guard(PRE_PUSH, repo).returncode == 0

    conn = sqlite3.connect(str(db))
    conn.execute("UPDATE tasks SET rollback_base_sha = NULL WHERE task_id = 't-esc'")
    conn.commit()
    conn.close()
    assert _run_guard(PRE_PUSH, repo).returncode == 1

    # 8. Enabled mode still denies unregistered push
    (repo / "context" / "control-plane-mode").write_text("enabled\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "-b", "feat/other-unreg"], check=True)
    assert _run_guard(PRE_PUSH, repo).returncode == 1
