#!/usr/bin/env python
"""
test_symlink_manager_policy.py
==============================

Purpose:
    Policy guards for `symlink_manager.py` (plugin-architecture-policy §5: file-level
    symlinks only; installer-owned folders belong to the installer). Found in a
    consumer repo (InvestmentToolkit, 2026-09-29): a manifest entry linked the
    installer-owned `.agents/rules` folder to the repo's `.agent/rules` directory.
    The installer/syncer own and clean `.agents/rules`, so the link never survived
    and `diagnose` reported a permanent "broken link" nobody could fix.

Key Input Dependencies:
    plugins/dev-utils/scripts/symlink_manager.py — `create` and `audit` under test
    git (tmp repo is initialised so find_repo_root() resolves to it)

Layer: Development / Testing

Functions:
    - test_create_refuses_directory_symlink
    - test_create_refuses_link_inside_installer_owned_folder
    - test_create_still_links_a_file_into_a_skill_folder
    - test_audit_reports_existing_policy_violations

Usage:
    python -m pytest plugins/dev-utils/tests/test_symlink_manager_policy.py
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "symlink_manager.py"


def _repo(tmp_path: Path, links: list[dict] | None = None) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "symlinks.json").write_text(json.dumps({"version": 1, "links": links or []}, indent=2), encoding="utf-8")
    return tmp_path


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=repo, capture_output=True, text=True)


def _manifest(repo: Path) -> list[dict]:
    return json.loads((repo / "symlinks.json").read_text(encoding="utf-8"))["links"]


def test_create_refuses_directory_symlink(tmp_path):
    repo = _repo(tmp_path)
    (repo / "shared" / "rules").mkdir(parents=True)
    res = _run(repo, "create", "--src", "shared/rules", "--dst", "plugins/p/skills/s/rules")
    assert res.returncode != 0
    assert "file-level" in (res.stdout + res.stderr)
    assert not (repo / "plugins/p/skills/s/rules").exists()
    assert _manifest(repo) == []


def test_create_refuses_link_inside_installer_owned_folder(tmp_path):
    repo = _repo(tmp_path)
    (repo / ".agent" / "rules").mkdir(parents=True)
    (repo / ".agent" / "rules" / "policy.md").write_text("# rule\n", encoding="utf-8")
    res = _run(repo, "create", "--src", ".agent/rules/policy.md", "--dst", ".agents/rules/policy.md")
    assert res.returncode != 0
    assert "installer-owned" in (res.stdout + res.stderr)
    assert not (repo / ".agents/rules/policy.md").exists()
    assert _manifest(repo) == []


def test_create_still_links_a_file_into_a_skill_folder(tmp_path):
    repo = _repo(tmp_path)
    (repo / "plugins/p/scripts").mkdir(parents=True)
    (repo / "plugins/p/scripts/tool.py").write_text("print('hi')\n", encoding="utf-8")
    res = _run(repo, "create", "--src", "plugins/p/scripts/tool.py", "--dst", "plugins/p/skills/s/scripts/tool.py")
    assert res.returncode == 0, res.stdout + res.stderr
    assert (repo / "plugins/p/skills/s/scripts/tool.py").is_symlink()
    assert [e["dst"] for e in _manifest(repo)] == ["plugins/p/skills/s/scripts/tool.py"]


def test_audit_reports_existing_policy_violations(tmp_path):
    repo = _repo(tmp_path, [{"src": ".agent/rules", "dst": ".agents/rules", "strategy": "symlink",
                             "description": "Rules directory for agent IDE custom rules discovery"}])
    (repo / ".agent" / "rules").mkdir(parents=True)
    out = _run(repo, "audit").stdout
    assert "policy" in out.lower()
    assert "installer-owned" in out
    assert "file-level" in out
