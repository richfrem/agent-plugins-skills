#!/usr/bin/env python3
"""
init_autoresearch.py -- Scaffold the Karpathy autoresearch loop for any target
================================================================================

Purpose:
    Idempotent scaffold for the autoresearch structure inside an experiment directory.
    The mutation target is NOT assumed to be a SKILL.md — it can be any file:
    a skill definition, a Python script, a config file, a math model, etc.

    Reads all three templates from the os-eval-runner assets directory and
    renders/copies them into the experiment directory:

        <experiment-dir>/references/program.md   (from program.md.template, vars rendered)
        <experiment-dir>/evals/evals.json        (from evals.json.template, vars rendered)
        <experiment-dir>/evals/results.tsv       (from results.tsv.template — header only)

    Safe to re-run: never overwrites existing files.
    .lock.hashes is NOT created here — evaluate.py writes it at --baseline time.

Templates live at:
    skills/os-eval-runner/assets/templates/autoresearch/
        program.md.template      (uses {{EXPERIMENT_NAME}}, {{EXPERIMENT_PATH}},
                                   {{MUTATION_TARGET}}, {{PLUGIN_ROOT}})
        evals.json.template      (uses {{EXPERIMENT_NAME}})
        results.tsv.template     (schema header — no vars)

Usage:
    python plugins/autoresearch-improvement/scripts/init_autoresearch.py \\
        --experiment-dir <path/to/experiment-or-skill> \\
        [--mutation-target SKILL.md] \\
        [--plugin-root plugins/autoresearch-improvement]

    # For a skill:
    python plugins/autoresearch-improvement/scripts/init_autoresearch.py \\
        --experiment-dir plugins/my-plugin/skills/my-skill

    # For a Python script:
    python plugins/autoresearch-improvement/scripts/init_autoresearch.py \\
        --experiment-dir experiments/my-tuning-run \\
        --mutation-target optimizer.py

Workflow after scaffolding:
    1. Edit references/program.md  -- fill in Notes section
    2. Edit evals/evals.json       -- replace REPLACE placeholders with real inputs/outputs
    3. evaluate.py --baseline      -- establish baseline, write .lock.hashes
    4. Agent loop                  -- reads program.md, mutates target, runs evaluate.py
"""

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
PLUGIN_ROOT = HERE.parent

# Templates live at assets/templates/autoresearch/ relative to the script's
# parent directory (the skill root). Using HERE.parent makes this agnostic
# to whether the skill is installed standalone (.agents/skills/os-eval-runner/)
# or inside the full plugin tree (plugins/agent-agentic-os/skills/os-eval-runner/).
TEMPLATES_DIR = PLUGIN_ROOT / "assets" / "templates" / "autoresearch"


def _load_template(name: str) -> str:
    """Read a template file, abort with a clear message if missing."""
    path = TEMPLATES_DIR / name
    if not path.exists():
        print(f"ERROR: template not found: {path}", file=sys.stderr)
        print(f"       Expected templates dir: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(2)
    return path.read_text(encoding="utf-8")


def _render(template: str, vars: dict[str, str]) -> str:
    """Replace all {{KEY}} placeholders in the template."""
    result = template
    for key, value in vars.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def scaffold(experiment_dir: Path, mutation_target: str, plugin_root: Path) -> None:
    """Deploy all three autoresearch templates into the experiment directory."""
    experiment_name = experiment_dir.name

    try:
        experiment_path_display = str(experiment_dir.relative_to(Path.cwd()))
    except ValueError:
        experiment_path_display = str(experiment_dir)

    try:
        plugin_root_display = str(plugin_root.relative_to(Path.cwd()))
    except ValueError:
        plugin_root_display = str(plugin_root)

    references_dir = experiment_dir / "references"
    evals_dir = experiment_dir / "evals"
    program_md = references_dir / "program.md"
    copilot_prompt_md = references_dir / "copilot_proposer_prompt.md"
    evals_json = evals_dir / "evals.json"
    results_tsv = evals_dir / "results.tsv"

    references_dir.mkdir(parents=True, exist_ok=True)
    evals_dir.mkdir(parents=True, exist_ok=True)

    template_vars = {
        "EXPERIMENT_NAME": experiment_name,
        "EXPERIMENT_PATH": experiment_path_display,
        "MUTATION_TARGET": mutation_target,
        "PLUGIN_ROOT": plugin_root_display,
    }

    created: list[str] = []
    skipped: list[str] = []

    def _write_or_skip(dest: Path, content: str) -> None:
        if dest.exists():
            skipped.append(str(dest.relative_to(experiment_dir)))
        else:
            dest.write_text(content, encoding="utf-8")
            created.append(str(dest.relative_to(experiment_dir)))

    _write_or_skip(program_md, _render(_load_template("program.md.template"), template_vars))
    _write_or_skip(copilot_prompt_md, _render(_load_template("copilot_proposer_prompt.md.template"), template_vars))
    _write_or_skip(evals_json, _render(_load_template("evals.json.template"), template_vars))
    _write_or_skip(results_tsv, _load_template("results.tsv.template"))  # no vars in header

    for f in created:
        print(f"[init-autoresearch] CREATED:  {f}")
    for f in skipped:
        print(f"[init-autoresearch] EXISTS (skipped): {f}")

    if created:
        try:
            evaluate_py = (plugin_root / "scripts" / "evaluate.py").relative_to(Path.cwd())
        except ValueError:
            evaluate_py = plugin_root / "scripts" / "evaluate.py"

        print()
        print("Next steps:")
        print(f"  1. Edit references/program.md  -- fill in Notes section (goal, target score)")
        print(f"  2. Edit evals/evals.json        -- replace REPLACE placeholders with real test cases")
        print(f"  3. Establish baseline:")
        print(f"       python {evaluate_py} \\")
        print(f"           --skill {experiment_path_display}/{mutation_target} \\")
        print(f"           --baseline --desc 'initial baseline'")
    else:
        print("[init-autoresearch] All files already exist. Nothing to do.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold the Karpathy autoresearch loop for any mutation target."
    )
    parser.add_argument(
        "--experiment-dir", required=True,
        help="Root directory for this experiment (e.g. a skill dir, or any project folder)"
    )
    parser.add_argument(
        "--mutation-target", default="SKILL.md",
        help="Filename of the file the loop will mutate (default: SKILL.md). "
             "Can be any file: a .py script, a config, a .md definition, etc."
    )
    parser.add_argument(
        "--plugin-root", default=None,
        help="Path to the plugin owning evaluate.py / eval_runner.py. "
             "Defaults to plugins/autoresearch-improvement."
    )
    args = parser.parse_args()

    experiment_dir = Path(args.experiment_dir).resolve()
    if not experiment_dir.exists():
        print(f"ERROR: experiment directory not found: {experiment_dir}", file=sys.stderr)
        sys.exit(2)

    mutation_target_path = experiment_dir / args.mutation_target
    if not mutation_target_path.exists():
        print(f"WARNING: mutation target not found: {mutation_target_path}", file=sys.stderr)
        print(f"         Scaffolding anyway — create {args.mutation_target} before running the loop.")

    plugin_root = Path(args.plugin_root).resolve() if args.plugin_root else PLUGIN_ROOT
    scaffold(experiment_dir, args.mutation_target, plugin_root)


if __name__ == "__main__":
    main()
