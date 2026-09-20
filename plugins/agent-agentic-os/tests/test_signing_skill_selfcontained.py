"""
tests/test_signing_skill_selfcontained.py
=========================================

Purpose:
    Failing-first tests for the os-signing-setup skill packaging (auth-ciba-increment-b, #639):
    the skill must be self-contained, so the self-test has a standalone hub CLI
    (`scripts/test_signing_mechanics.py`) whose spokes (and `signing_selftest.py`) are symlinked into
    the skill, the SKILL.md steps point only at skill-relative scripts, and a README for humans exists.
    Real files and a real subprocess; no mocks.

Key Input Dependencies:
    - scripts/test_signing_mechanics.py, scripts/control_plane/signing_selftest.py
    - skills/os-signing-setup/{SKILL.md,README.md,scripts/}

Key Functions (test cases):
    - test_standalone_selftest_cli_refuses_without_a_terminal
    - test_skill_scripts_are_symlinks_to_the_hub
    - test_every_skill_script_import_resolves_inside_the_skill
    - test_skill_md_uses_only_skill_relative_scripts
    - test_readme_exists_with_the_high_level_steps
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "os-signing-setup"


def test_standalone_selftest_cli_refuses_without_a_terminal(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "test_signing_mechanics.py"), "--key", str(tmp_path / "k"), "--repo-root", str(tmp_path)],
        capture_output=True, text=True, stdin=subprocess.DEVNULL,
    )
    assert result.returncode != 0
    assert "terminal" in (result.stdout + result.stderr).lower()


def test_skill_scripts_are_symlinks_to_the_hub():
    for rel in ("scripts/test_signing_mechanics.py", "scripts/setup_ciba_identity.py", "scripts/control_plane/signing_selftest.py"):
        link = SKILL / rel
        assert link.is_symlink(), rel
        assert link.resolve().is_file(), rel


def test_every_skill_script_import_resolves_inside_the_skill(tmp_path):
    """Run the skill copies from a directory that is NOT the plugin, so only skill-local files can import."""
    for script in ("setup_ciba_identity.py", "test_signing_mechanics.py"):
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / script), "--help"],
            capture_output=True, text=True, cwd=tmp_path,
        )
        assert result.returncode == 0, result.stderr
        # deref check: the imported control_plane package must come from the skill folder
        probe = subprocess.run(
            [sys.executable, "-c",
             "import sys, runpy; sys.argv=['x','--help']; sys.path.insert(0, %r); import control_plane, control_plane.signing_selftest as m; print(control_plane.__file__)" % str(SKILL / "scripts")],
            capture_output=True, text=True, cwd=tmp_path,
        )
        assert probe.returncode == 0, probe.stderr


def test_skill_md_uses_only_skill_relative_scripts():
    text = (SKILL / "SKILL.md").read_text()
    assert "agent_control.py test-signing-mechanics" not in text
    assert "scripts/test_signing_mechanics.py" in text
    assert "plugins/agent-agentic-os/scripts" not in text


def test_readme_exists_with_the_high_level_steps():
    readme = (SKILL / "README.md").read_text().lower()
    for needle in ("passphrase", "fingerprint", "setup_ciba_identity.py", "test_signing_mechanics.py", "show-challenge", "approve-transition", "agentic-os-local-agent", "never"):
        assert needle in readme, needle
