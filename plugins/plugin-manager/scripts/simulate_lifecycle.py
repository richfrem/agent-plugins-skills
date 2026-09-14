#!/usr/bin/env python3
"""
simulate_lifecycle.py
=====================

Purpose:
    Unified lifecycle simulator that tests and validates the complete agent
    plugin toolchain (Installer -> Pruner -> Syncer -> Remover) in a
    sandboxed directory to ensure all registries, locks, manifests, and
    central stores remain synchronized across operations.

Layer: Plugin Manager / Testing & Simulation

Usage Examples:
    python3 simulate_lifecycle.py
    python3 simulate_lifecycle.py --scenario full
    python3 simulate_lifecycle.py --scenario install
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]


def create_mock_plugin(root: Path, plugin_name: str = "mock-plugin", skills: list[str] = None) -> Path:
    """Scaffolds a compliant synthetic plugin inside root/plugins/<plugin_name>."""
    if skills is None:
        skills = ["alpha-skill", "beta-skill", "gamma-skill"]

    plugin_dir = root / "plugins" / plugin_name
    skills_dir = plugin_dir / "skills"
    scripts_dir = plugin_dir / "scripts"
    refs_dir = plugin_dir / "references"

    for d in (skills_dir, scripts_dir, refs_dir):
        d.mkdir(parents=True, exist_ok=True)

    manifest_file = plugin_dir / ".claude-plugin" / "plugin.json"
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps({
        "name": plugin_name,
        "description": f"Synthetic test plugin {plugin_name}",
        "version": "1.0.0"
    }, indent=2), encoding="utf-8")

    (refs_dir / "acceptance-criteria.md").write_text("# Acceptance Criteria\n", encoding="utf-8")
    (scripts_dir / "helper.py").write_text("print('helper')\n", encoding="utf-8")

    for s_name in skills:
        s_dir = skills_dir / s_name
        s_dir.mkdir(parents=True, exist_ok=True)
        (s_dir / "SKILL.md").write_text(
            f"---\nname: {s_name}\nplugin: {plugin_name}\ndescription: Implements {s_name}.\n---\n# {s_name}\n",
            encoding="utf-8"
        )
        s_evals = s_dir / "evals"
        s_evals.mkdir(parents=True, exist_ok=True)
        (s_evals / "evals.json").write_text(json.dumps([
            {"prompt": f"Run {s_name}", "should_trigger": True},
            {"prompt": "Unrelated prompt", "should_trigger": False}
        ], indent=2), encoding="utf-8")

    return plugin_dir


def run_lifecycle_simulation(target_root: Path, scenario: str = "full") -> dict:
    """Runs end-to-end lifecycle stages against target_root."""
    stages_completed = []
    details = {}

    installer_py = SCRIPT_DIR / "plugin_installer.py"
    pruner_py = SCRIPT_DIR / "prune_installed_skills.py"
    syncer_py = SCRIPT_DIR / "sync_with_inventory.py"
    remover_py = SCRIPT_DIR / "plugin_remove.py"

    target_root.mkdir(parents=True, exist_ok=True)
    plugin_name = "test-plugin"
    skills = ["skill-one", "skill-two", "skill-three"]
    plugin_dir = create_mock_plugin(target_root, plugin_name, skills)

    # 1. Stage: INSTALL
    if scenario in ("full", "install"):
        # Install the plugin
        cmd_install = [
            sys.executable, str(installer_py),
            "--plugin", str(plugin_dir),
        ]
        res = subprocess.run(cmd_install, cwd=target_root, capture_output=True, text=True)
        assert res.returncode == 0, f"Install failed: {res.stderr}"

        # Populate plugin-sources.json
        sources_file = target_root / "plugin-sources.json"
        sources_file.write_text(json.dumps({
            "sources": [{"source": str(target_root / "plugins"), "plugins": [plugin_name]}]
        }, indent=2), encoding="utf-8")

        # Verify all skills are present
        for s in skills:
            assert (target_root / ".agents" / "skills" / s).exists(), f"Skill {s} missing after install"

        assert (target_root / "plugin-retention.json").exists(), "plugin-retention.json missing after install"
        stages_completed.append("install")
        details["install"] = "All 3 skills installed, retention and sources registered"

    # 2. Stage: PRUNE
    if scenario in ("full", "prune"):
        ret_file = target_root / "plugin-retention.json"
        with open(ret_file, "r", encoding="utf-8") as f:
            ret_data = json.load(f)

        # Untoggle skill-two
        ret_data["plugins"][plugin_name]["skills"]["skill-two"] = False
        with open(ret_file, "w", encoding="utf-8") as f:
            json.dump(ret_data, f, indent=2)

        # Run pruner with confirmation token
        cmd_prune = [
            sys.executable, str(pruner_py),
            "--execute",
            "--confirm-token", "PRUNE-INSTALLED-SKILLS"
        ]
        res = subprocess.run(cmd_prune, cwd=target_root, capture_output=True, text=True)
        assert res.returncode == 0, f"Pruner failed: {res.stderr}"

        # Verify skill-two was deleted and others remained
        assert (target_root / ".agents" / "skills" / "skill-one").exists()
        assert not (target_root / ".agents" / "skills" / "skill-two").exists(), "skill-two should have been pruned"
        assert (target_root / ".agents" / "skills" / "skill-three").exists()

        stages_completed.append("prune")
        details["prune"] = "skill-two successfully pruned from .agents/skills/ and registries"

    # 3. Stage: SYNC
    if scenario in ("full", "sync"):
        # Run sync_with_inventory.py
        cmd_sync = [sys.executable, str(syncer_py)]
        res = subprocess.run(cmd_sync, cwd=target_root, capture_output=True, text=True)
        assert res.returncode == 0, f"Syncer failed: {res.stderr}"

        # Verify post-sync retention enforcement kept skill-two pruned
        assert (target_root / ".agents" / "skills" / "skill-one").exists()
        assert not (target_root / ".agents" / "skills" / "skill-two").exists(), "skill-two re-appeared after sync!"
        assert (target_root / ".agents" / "skills" / "skill-three").exists()

        stages_completed.append("sync")
        details["sync"] = "Sync completed and retention policy enforced"

    # 4. Stage: REMOVE
    if scenario in ("full", "remove"):
        cmd_remove = [sys.executable, str(remover_py), "--all", "--yes"]
        res = subprocess.run(cmd_remove, cwd=target_root, capture_output=True, text=True)
        assert res.returncode == 0, f"Remover failed: {res.stderr}"

        # Verify .agents/skills/ is completely empty
        skills_dir = target_root / ".agents" / "skills"
        if skills_dir.exists():
            remaining = [i.name for i in skills_dir.iterdir() if not i.name.startswith(".")]
            assert len(remaining) == 0, f"Orphans remain in .agents/skills: {remaining}"

        stages_completed.append("remove")
        details["remove"] = "All plugins removed and .agents/skills completely clean"

    return {
        "success": True,
        "stages_completed": stages_completed,
        "details": details
    }


def main():
    parser = argparse.ArgumentParser(description="Run plugin lifecycle simulator across install, prune, sync, and remove.")
    parser.add_argument("--scenario", choices=["full", "install", "prune", "sync", "remove"], default="full",
                        help="Simulation scenario to execute (default: full)")
    parser.add_argument("--temp-dir", default=None, help="Custom target workspace directory")
    args = parser.parse_args()

    temp_dir = None
    if args.temp_dir:
        target_root = Path(args.temp_dir).resolve()
    else:
        temp_dir = tempfile.mkdtemp(prefix="plugin_sim_")
        target_root = Path(temp_dir)

    try:
        print(f"Running lifecycle simulation [{args.scenario}] in {target_root}...")
        res = run_lifecycle_simulation(target_root, scenario=args.scenario)
        print("✓ Simulation SUCCESS!")
        print(f"  Stages completed: {' -> '.join(res['stages_completed'])}")
        for stage, desc in res["details"].items():
            print(f"    - {stage.upper()}: {desc}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
