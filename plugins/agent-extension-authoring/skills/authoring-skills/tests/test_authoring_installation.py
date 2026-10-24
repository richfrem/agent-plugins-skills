"""Installed authoring-skills contract using a real copy of the skill and subprocesses.

Purpose: Ensure source-tree paths cannot hide missing templates or dependencies. The skill is copied
to a temporary location (as APM would deploy it), then used to scaffold and audit new skills.
Key Input Dependencies: this skill folder (scripts/scaffold.py, scripts/audit_skill.py).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]


def run(*args, cwd=None):
    """Execute fixture commands with the actual Python interpreter."""
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True)


def test_installed_copy_generates_and_audits_skills(tmp_path):
    """A copied skill scaffolds instructional and executable skills that audit clean in both modes."""
    installed = tmp_path / "installed" / "authoring-skills"
    shutil.copytree(SKILL, installed, symlinks=False, ignore=shutil.ignore_patterns("__pycache__", "tests"))
    plugin = tmp_path / "output" / "sample-plugin"
    for variant in ("instructional", "executable"):
        name = f"{variant}-sample"
        result = run(installed / "scripts/scaffold.py", "--type", "skill", "--name", name, "--path", plugin / "skills",
                     "--desc", "Processes samples. Use for sample processing.", "--variant", variant, "--json", cwd=installed)
        assert result.returncode == 0, result.stderr
        receipt = json.loads(result.stdout)
        assert receipt["links"] == [], "skills are self-contained; no managed links"
        source = plugin / "skills" / name
        assert not (plugin / "scripts").exists(), "no plugin-root hub scripts"
        result = run(installed / "scripts/audit_skill.py", source, "--mode", "source", "--json", cwd=installed)
        assert result.returncode == 0, result.stdout + result.stderr
        deployed = tmp_path / "deployed" / name
        shutil.copytree(source, deployed, symlinks=False)
        result = run(installed / "scripts/audit_skill.py", deployed, "--mode", "installed", "--json", cwd=installed)
        assert result.returncode == 0, result.stdout + result.stderr
        if variant == "executable":
            script = deployed / "scripts/executable_sample.py"
            assert script.is_file()
            result = run(script, "--help", cwd=deployed)
            assert result.returncode == 0, result.stderr
