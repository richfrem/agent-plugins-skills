"""Installed skill contracts using real materialized files and subprocesses.

Purpose: Ensure source-tree paths cannot hide missing templates or dependencies.
Key Input Dependencies: create-skill/audit-skill spokes and managed-link utility.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
MANAGER = REPO / "plugins/dev-utils/scripts/symlink_manager.py"


def run(*args, cwd=None):
    """Execute fixture commands with the actual Python interpreter."""
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True)


def test_materialized_authoring_workflow(tmp_path):
    """Copied authoring skills generate and audit without consulting their source hub."""
    creator = tmp_path / "installed/create-skill"
    auditor = tmp_path / "installed/audit-skill"
    shutil.copytree(PLUGIN / "skills/create-skill", creator, symlinks=False)
    shutil.copytree(PLUGIN / "skills/audit-skill", auditor, symlinks=False)
    plugin = tmp_path / "output/sample-plugin"
    for variant in ("instructional", "executable"):
        name = f"{variant}-sample"
        result = run(creator / "scripts/scaffold.py", "--type", "skill", "--name", name,
                     "--path", plugin / "skills", "--desc", "Processes samples. Use for sample processing.",
                     "--variant", variant, "--plugin-root", plugin, "--json", cwd=creator)
        assert result.returncode == 0, result.stderr
        receipt = json.loads(result.stdout)
        for link in receipt["links"]:
            result = run(MANAGER, "create", "--src", link["src"], "--dst", link["dst"],
                         "--manifest", tmp_path / "manifest.json")
            assert result.returncode == 0, result.stderr + result.stdout
        source = plugin / "skills" / name
        result = run(auditor / "scripts/audit_skill.py", source, "--mode", "source", "--json", cwd=auditor)
        assert result.returncode == 0, result.stdout + result.stderr
        installed = tmp_path / "deployed" / name
        shutil.copytree(source, installed, symlinks=False)
        result = run(auditor / "scripts/audit_skill.py", installed, "--mode", "installed", "--json", cwd=auditor)
        assert result.returncode == 0, result.stdout + result.stderr
        if variant == "executable":
            result = run(installed / "scripts/executable_sample.py", "--help", cwd=installed)
            assert result.returncode == 0, result.stderr


def test_contract_rule_registry_matches_emitted_rule_ids():
    """Every emitted ID has one normative severity definition, with no orphan rules."""
    import re
    contract = json.loads((PLUGIN / "references/skill-authoring-contract.json").read_text())
    code = (PLUGIN / "scripts/audit_skill.py").read_text()
    referenced = set(re.findall(r'"((?:input|metadata|size|navigation|links|evals|packaging|repair)\.[a-z-]+)"', code))
    assert {rule for rule in referenced if not rule.endswith(".json")} == set(contract["rules"])
