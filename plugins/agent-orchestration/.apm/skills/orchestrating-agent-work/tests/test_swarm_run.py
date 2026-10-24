"""
Comprehensive Unit & Integration Tests for swarm_run.py (PR D)
================================================================

Validates:
1. File discovery across sources (explicit, dir crawl, checklist, bundle).
2. Path traversal protection: ../paths escaping workdir exit non-zero (code 1).
3. Dry-run safety: --dry-run leaves zero state mutations or disk traces.
4. Checkpoint resume: --resume reprocesses incomplete files.
5. Short-circuit caching via check_cmd.
6. Post-command failure marks the worker result as failed.
7. --require-clean refuses execution if working tree is dirty.
8. Run-id isolation and receipts stored outside working tree (never dirtying workdir).
9. Instruction suppression preserves files in place without renaming.
10. Mock engine dispatch via executable stub on PATH.
"""

import os
import sys
import json
import stat
import types
import subprocess
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.swarm_run import (
    resolve_files,
    parse_yaml_frontmatter_stdlib,
    suppress_monolithic_md,
    _is_safe_path,
)


def test_parse_yaml_frontmatter_stdlib():
    yaml_text = """
model: sonnet
workers: 4
timeout: 120
ext: [".md", ".txt"]
vars:
  env: test
  profile: staging
require_clean: true
"""
    parsed = parse_yaml_frontmatter_stdlib(yaml_text)
    assert parsed["model"] == "sonnet"
    assert parsed["workers"] == 4
    assert parsed["timeout"] == 120
    assert parsed["ext"] == [".md", ".txt"]
    assert parsed["vars"]["env"] == "test"
    assert parsed["vars"]["profile"] == "staging"
    assert parsed["require_clean"] is True


def test_resolve_files_path_traversal_fails_closed(tmp_path):
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")

    # 1. Traversal in explicit files raises SystemExit(1)
    args = types.SimpleNamespace(
        files=[str(outside)],
        bundle=None,
        files_from=None,
        dir=None,
        workdir=workdir,
    )
    with pytest.raises(SystemExit) as exc_info:
        resolve_files(args, {}, root_dir=workdir)
    assert exc_info.value.code == 1

    # 2. Traversal in bundle raises SystemExit(1)
    bundle = workdir / "manifest.json"
    bundle.write_text(json.dumps({"files": [{"path": "../outside.md"}]}), encoding="utf-8")
    args_bundle = types.SimpleNamespace(
        files=None,
        bundle=bundle,
        files_from=None,
        dir=None,
        workdir=workdir,
    )
    with pytest.raises(SystemExit) as exc_info_bundle:
        resolve_files(args_bundle, {}, root_dir=workdir)
    assert exc_info_bundle.value.code == 1


def test_resolve_files_valid_sources(tmp_path):
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    f1 = workdir / "f1.md"
    f2 = workdir / "f2.md"
    f1.write_text("f1", encoding="utf-8")
    f2.write_text("f2", encoding="utf-8")

    # Directory crawl
    args = types.SimpleNamespace(
        files=None,
        dir=workdir,
        bundle=None,
        files_from=None,
        workdir=workdir,
    )
    resolved_dir = resolve_files(args, {"ext": [".md"]}, root_dir=workdir)
    assert "f1.md" in resolved_dir
    assert "f2.md" in resolved_dir

    # Checklist
    checklist = workdir / "checklist.md"
    checklist.write_text("- [ ] `f1.md`\n- [ ] `f2.md`\n", encoding="utf-8")
    args.dir = None
    args.files_from = checklist
    resolved_chk = resolve_files(args, {}, root_dir=workdir)
    assert resolved_chk == ["f1.md", "f2.md"]


def _create_mock_engine(bin_dir: Path, engine_name: str = "claude"):
    """Create a mock executable script that writes dummy response."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    exe_path = bin_dir / engine_name
    script_content = (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        "print('mocked output for ' + sys.argv[-1])\n"
    )
    exe_path.write_text(script_content, encoding="utf-8")
    exe_path.chmod(exe_path.stat().st_mode | stat.S_IEXEC)


def test_dry_run_leaves_zero_state_and_resume_processes_all(tmp_path):
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    f1 = workdir / "doc1.md"
    f2 = workdir / "doc2.md"
    f1.write_text("doc 1 content", encoding="utf-8")
    f2.write_text("doc 2 content", encoding="utf-8")

    job_file = workdir / "test.job.md"
    job_file.write_text(
        "---\nmodel: haiku\nworkers: 2\n---\nSummarize this file.\n",
        encoding="utf-8",
    )

    script = Path(__file__).resolve().parents[1] / "scripts" / "swarm_run.py"

    # Step 1: Run --dry-run
    cmd_dry = [
        sys.executable, str(script),
        "--job", str(job_file),
        "--workdir", str(workdir),
        "--files", "doc1.md", "doc2.md",
        "--dry-run",
    ]
    res_dry = subprocess.run(cmd_dry, capture_output=True, text=True)
    assert res_dry.returncode == 0
    assert "[DRY]" in res_dry.stdout or "[DRY]" in res_dry.stderr

    # Assert no .swarm-run directory was created in workdir
    assert not (workdir / ".swarm-run").exists()

    # Step 2: Now run live with mock engine
    bin_dir = tmp_path / "bin"
    _create_mock_engine(bin_dir, "claude")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"

    cmd_live = [
        sys.executable, str(script),
        "--job", str(job_file),
        "--workdir", str(workdir),
        "--files", "doc1.md", "doc2.md",
        "--resume",
    ]
    res_live = subprocess.run(cmd_live, capture_output=True, text=True, env=env)
    assert res_live.returncode == 0
    assert "DONE. Success: 2 | Failed: 0" in res_live.stdout or "DONE. Success: 2 | Failed: 0" in res_live.stderr

    # State is stored outside the working tree
    assert not (workdir / ".swarm-run").exists()
    runs_dir = workdir.parent / ".swarm-run" / "test"
    assert runs_dir.exists()
    runs = list(runs_dir.iterdir())
    assert len(runs) > 0
    state = json.loads((runs[0] / "state.json").read_text(encoding="utf-8"))
    assert len(state["completed"]) == 2


def test_post_cmd_failure_marks_failed(tmp_path):
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    f1 = workdir / "doc1.md"
    f1.write_text("doc 1", encoding="utf-8")

    job_file = workdir / "failing_post.job.md"
    job_file.write_text(
        "---\nmodel: haiku\npost_cmd: sh -c 'exit 1'\n---\nPrompt\n",
        encoding="utf-8",
    )

    bin_dir = tmp_path / "bin"
    _create_mock_engine(bin_dir, "claude")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"

    script = Path(__file__).resolve().parents[1] / "scripts" / "swarm_run.py"
    cmd = [
        sys.executable, str(script),
        "--job", str(job_file),
        "--workdir", str(workdir),
        "--files", "doc1.md",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert res.returncode == 1
    assert "Failed: 1" in res.stdout or "Failed: 1" in res.stderr


def test_check_cmd_skip(tmp_path):
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    f1 = workdir / "cached.md"
    f2 = workdir / "uncached.md"
    f1.write_text("cached", encoding="utf-8")
    f2.write_text("uncached", encoding="utf-8")

    # Create indicator file for cached.md
    (workdir / "cached.md.done").write_text("done", encoding="utf-8")

    job_file = workdir / "check.job.md"
    job_file.write_text(
        "---\nmodel: haiku\ncheck_cmd: test -f {file}.done\n---\nPrompt\n",
        encoding="utf-8",
    )

    bin_dir = tmp_path / "bin"
    _create_mock_engine(bin_dir, "claude")
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"

    script = Path(__file__).resolve().parents[1] / "scripts" / "swarm_run.py"
    cmd = [
        sys.executable, str(script),
        "--job", str(job_file),
        "--workdir", str(workdir),
        "--files", "cached.md", "uncached.md",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert res.returncode == 0
    assert "already cached" in res.stdout or "already cached" in res.stderr


def test_require_clean_refuses_dirty_workdir(tmp_path):
    workdir = tmp_path / "gitrepo"
    workdir.mkdir()
    subprocess.run(["git", "init"], cwd=str(workdir), capture_output=True)
    (workdir / "tracked.txt").write_text("clean", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=str(workdir), capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(workdir), capture_output=True)

    # Now make it dirty
    (workdir / "dirty.txt").write_text("dirty content", encoding="utf-8")

    job_file = workdir / "clean.job.md"
    job_file.write_text("---\nmodel: haiku\n---\nPrompt\n", encoding="utf-8")

    script = Path(__file__).resolve().parents[1] / "scripts" / "swarm_run.py"
    cmd = [
        sys.executable, str(script),
        "--job", str(job_file),
        "--workdir", str(workdir),
        "--files", "tracked.txt",
        "--require-clean",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "working directory is dirty" in (res.stderr + res.stdout)


def test_hide_instructions_does_not_rename_files(tmp_path):
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    claude_md = workdir / "CLAUDE.md"
    claude_md.write_text("# Project instructions", encoding="utf-8")

    with suppress_monolithic_md("claude", workdir, enabled=True):
        assert claude_md.is_file()
        assert not (workdir / ".CLAUDE.md.swarm_bak").exists()

    assert claude_md.is_file()
    assert claude_md.read_text(encoding="utf-8") == "# Project instructions"
