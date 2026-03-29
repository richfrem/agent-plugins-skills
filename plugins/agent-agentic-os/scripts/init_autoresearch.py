#!/usr/bin/env python3
"""
init_autoresearch.py -- Scaffold the Karpathy autoresearch loop for a target skill
====================================================================================

Purpose:
    Idempotent scaffold for the 3-file autoresearch structure inside a target skill
    directory. Generates:
        <target-skill>/references/program.md    (from templates/autoresearch/program.md.template)
        <target-skill>/evals/evals.json         (empty fixture scaffold)
        <target-skill>/evals/                   (directory, safe for results.tsv creation later)

    Does NOT create results.tsv or .lock.hashes — those are created by evaluate.py
    when the first --baseline run is recorded.

    Safe to re-run: never overwrites existing files.

Usage:
    python scripts/init_autoresearch.py --skill <path/to/target-skill>
    python scripts/init_autoresearch.py --skill <path/to/target-skill> --plugin-root <path/to/plugin>

    # Example:
    python plugins/agent-agentic-os/scripts/init_autoresearch.py \\
        --skill plugins/my-plugin/skills/my-skill

Relationship to evaluate.py:
    Run init_autoresearch.py FIRST to scaffold the target skill.
    Then run evaluate.py --baseline to establish the baseline.
    The autoresearch loop (agent + evaluate.py) runs after that.

This script reads from:
    plugins/agent-agentic-os/templates/autoresearch/program.md.template
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
PLUGIN_ROOT = HERE.parent
# Template lives inside skill-improvement-eval's own assets — not at plugin root —
# so it's clearly scoped as a resource of this evaluation skill, not a plugin-level artifact.
TEMPLATE_PATH = (
    PLUGIN_ROOT
    / "skills"
    / "skill-improvement-eval"
    / "assets"
    / "templates"
    / "autoresearch"
    / "program.md.template"
)

EVALS_JSON_SCAFFOLD = [
    {
        "prompt": "REPLACE_ME: a prompt that SHOULD trigger this skill",
        "should_trigger": True
    },
    {
        "prompt": "REPLACE_ME: another prompt that SHOULD trigger this skill",
        "should_trigger": True
    },
    {
        "prompt": "REPLACE_ME: a prompt that should NOT trigger this skill",
        "should_trigger": False
    }
]


def scaffold_target(skill_root: Path, plugin_root: Path) -> None:
    """Create the autoresearch scaffold files inside the target skill directory."""
    skill_name = skill_root.name
    # Compute skill path relative to cwd for readability in program.md
    try:
        skill_path_display = str(skill_root.relative_to(Path.cwd()))
    except ValueError:
        skill_path_display = str(skill_root)

    references_dir = skill_root / "references"
    evals_dir = skill_root / "evals"
    program_md = references_dir / "program.md"
    evals_json = evals_dir / "evals.json"

    # Ensure directories exist
    references_dir.mkdir(parents=True, exist_ok=True)
    evals_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    skipped: list[str] = []

    # 1. program.md from template
    if program_md.exists():
        skipped.append(str(program_md.relative_to(skill_root)))
    else:
        if not TEMPLATE_PATH.exists():
            print(f"ERROR: template not found at {TEMPLATE_PATH}", file=sys.stderr)
            sys.exit(2)
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
        rendered = (
            template
            .replace("{{SKILL_NAME}}", skill_name)
            .replace("{{SKILL_PATH}}", skill_path_display)
            .replace("{{PLUGIN_ROOT}}", str(plugin_root.relative_to(Path.cwd()) if Path.cwd() in plugin_root.parents else plugin_root))
        )
        program_md.write_text(rendered, encoding="utf-8")
        created.append(str(program_md.relative_to(skill_root)))

    # 2. evals.json scaffold (empty fixture list with placeholder entries)
    if evals_json.exists():
        skipped.append(str(evals_json.relative_to(skill_root)))
    else:
        evals_json.write_text(
            json.dumps(EVALS_JSON_SCAFFOLD, indent=2) + "\n",
            encoding="utf-8"
        )
        created.append(str(evals_json.relative_to(skill_root)))

    # Report
    for f in created:
        print(f"[init-autoresearch] CREATED:  {f}")
    for f in skipped:
        print(f"[init-autoresearch] EXISTS (skipped): {f}")

    if created:
        print()
        print("Next steps:")
        print(f"  1. Edit {program_md} — fill in target score, notes")
        print(f"  2. Edit {evals_json} — replace placeholder prompts with real test cases")
        print(f"  3. Run baseline:")
        print(f"       python {Path(__file__).relative_to(Path.cwd())} is done")
        print(f"       python {plugin_root}/scripts/evaluate.py \\")
        print(f"           --skill {skill_path_display}/SKILL.md \\")
        print(f"           --baseline --desc 'initial baseline'")
    else:
        print("[init-autoresearch] All files already exist. Nothing to do.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold the Karpathy autoresearch loop for a target skill."
    )
    parser.add_argument(
        "--skill", required=True,
        help="Path to the target skill directory (contains SKILL.md)"
    )
    parser.add_argument(
        "--plugin-root", default=None,
        help="Path to the plugin that owns evaluate.py / eval_runner.py. "
             "Defaults to plugins/agent-agentic-os relative to the skill."
    )
    args = parser.parse_args()

    skill_root = Path(args.skill).resolve()
    if not skill_root.exists():
        print(f"ERROR: skill directory not found: {skill_root}", file=sys.stderr)
        sys.exit(2)
    if not (skill_root / "SKILL.md").exists():
        print(f"ERROR: no SKILL.md found in {skill_root}", file=sys.stderr)
        sys.exit(2)

    plugin_root = Path(args.plugin_root).resolve() if args.plugin_root else PLUGIN_ROOT
    scaffold_target(skill_root, plugin_root)


if __name__ == "__main__":
    main()
