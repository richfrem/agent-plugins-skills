"""Regression tests for B7, B22, and G14: skill folders never receive transitory output."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent


def _file_set(root: Path) -> set[str]:
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }


def test_agent_control_status_refuses_inside_copied_skill_folder_without_creating_files(tmp_path):
    """B22: running agent_control.py status from inside an installed skill folder (outside a git repo)
    must refuse with exit code 2 and create zero files inside the skill folder."""
    copied_skill = tmp_path / "installed-skills" / "running-control-plane"
    shutil.copytree(
        SKILL_ROOT,
        copied_skill,
        symlinks=False,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tests"),
    )
    before = _file_set(copied_skill)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    res = subprocess.run(
        [sys.executable, str(copied_skill / "scripts" / "agent_control.py"), "status", "--task-id", "t1"],
        cwd=copied_skill,
        capture_output=True,
        text=True,
        env=env,
    )
    after = _file_set(copied_skill)
    assert res.returncode == 2, f"Expected exit 2, got {res.returncode}\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "skill folder" in res.stderr.lower()
    assert after == before, f"Skill folder gained files: {sorted(after - before)}"


def test_interview_outline_writes_to_tmp_repo_never_skill_folder(tmp_path):
    """B7 / G14: running interview outline tests from the skill folder creates no files in the skill folder."""
    before = _file_set(SKILL_ROOT)
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_work_intake_guidance.py",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        cwd=SKILL_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    after = _file_set(SKILL_ROOT)
    assert res.returncode == 0, f"Interview test failed:\n{res.stdout}\n{res.stderr}"
    assert after == before, f"Skill folder gained files: {sorted(after - before)}"
