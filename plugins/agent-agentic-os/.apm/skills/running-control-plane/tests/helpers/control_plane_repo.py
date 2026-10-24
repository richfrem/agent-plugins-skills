"""
helpers/control_plane_repo.py - a realistic throwaway repo for control-plane-mode tests.

Builds a git repo that looks like a consumer install:
  * the skill's scripts deployed the way APM deploys them, under
    `.claude/skills/running-control-plane/scripts` (so the tests run the script from there)
  * .git/hooks/pre-commit and pre-push dispatchers wired exactly as init_agentic_os.py wires them
    (plus a custom line and the independent evolution guard, which must survive any toggle)
  * the guard scripts installed into .git/hooks, stamped with the deployed script paths
  * a context/control_plane.db whose bytes must never change
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPTS = SKILL / "scripts"
DEPLOYED = Path(".claude") / "skills" / "running-control-plane"

DB_BYTES = b"SQLite-format-3-pretend-task-history\x00\x01\x02" * 8


def deploy_skill(root: Path) -> Path:
    """Copy the skill's scripts into the repo like an APM project install; returns the scripts dir."""
    dest = root / DEPLOYED / "scripts"
    shutil.copytree(SCRIPTS, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dest


def make_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@example.com"],
                ["git", "config", "user.name", "Tester"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)

    deployed = deploy_skill(root)
    hooks = root / ".git" / "hooks"
    hooks.mkdir(exist_ok=True)
    (hooks / "pre-commit").write_text(
        "#!/usr/bin/env bash\n"
        'HOOKS_DIR="$(dirname "$0")"\n'
        "echo custom-pre-commit-step\n"
        "\n# Run evolution guard if it exists\n"
        'if [ -x "$HOOKS_DIR/pre-commit-evolution-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-commit-evolution-guard" || exit 1\n'
        "fi\n"
        "\n# Run pipeline execution guard if it exists\n"
        'if [ -x "$HOOKS_DIR/pre-commit-pipeline-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-commit-pipeline-guard" || exit 1\n'
        "fi\n"
        "\nexit 0\n",
        encoding="utf-8",
    )
    # the older minimal style the installer wrote when no pre-push hook existed
    (hooks / "pre-push").write_text(
        "#!/usr/bin/env bash\n"
        "# pre-push hook - installed by init_agentic_os.py\n"
        'HOOKS_DIR="$(dirname "$0")"\n'
        "\n# Run review guard\n"
        'if [ -x "$HOOKS_DIR/pre-push-review-guard" ]; then\n'
        '    "$HOOKS_DIR/pre-push-review-guard" || exit 1\n'
        "fi\n"
        "\nexit 0\n",
        encoding="utf-8",
    )
    sys.path.insert(0, str(deployed))
    try:
        import control_plane_hooks as cph
        for guard in cph.CONTROL_PLANE_GUARDS:
            cph.install_guard_script(deployed / guard.name, hooks, guard)
    finally:
        sys.path.remove(str(deployed))
    shutil.copy2(SCRIPTS / "pre-commit-evolution-guard", hooks / "pre-commit-evolution-guard")
    for name in ("pre-commit", "pre-push", "pre-commit-evolution-guard"):
        (hooks / name).chmod(0o755)

    (root / "context").mkdir()
    (root / "context" / "control_plane.db").write_bytes(DB_BYTES)
    return root


def mode_script(root: Path) -> Path:
    return root / DEPLOYED / "scripts" / "control_plane_mode.py"


def run_mode(root: Path, *args: str) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(mode_script(root)), *args, "--target", str(root)]
    return subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})


def snapshot(root: Path) -> dict:
    """Every file under the repo (excluding .git objects) -> bytes, to prove 'nothing changed'."""
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and ".git/objects" not in p.as_posix() and ".git/index" not in p.as_posix():
            out[p.relative_to(root).as_posix()] = p.read_bytes()
    return out
