---
concept: execute
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-docker-skill/execute.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.116815+00:00
cluster: args
content_hash: 78ee7ca225f9e471
---

# Execute

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/create-docker-skill/execute.py -->
#!/usr/bin/env python3
"""Execution wrapper for continuous skill optimization loops.

This script runs the shared benchmarking loop with safe defaults:
- baseline-first iteration governance
- keep/discard/crash ledger output
- optional Copilot improvement backend with token-precedence cleanup
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def _build_command(args: argparse.Namespace, plugin_root: Path) -> list[str]:
    """Build the run_loop invocation command."""
    run_loop_path = plugin_root / "scripts" / "benchmarking" / "run_loop.py"
    cmd = [
        "python3",
        str(run_loop_path),
        "--eval-set",
        args.eval_set,
        "--skill-path",
        args.skill_path,
        "--max-iterations",
        str(args.max_iterations),
        "--runs-per-query",
        str(args.runs_per_query),
        "--num-workers",
        str(args.num_workers),
        "--timeout",
        str(args.timeout),
        "--holdout",
        str(args.holdout),
        "--eval-engine",
        args.eval_engine,
        "--improve-engine",
        args.improve_engine,
        "--results-dir",
        args.results_dir,
        "--report",
        args.report,
    ]
    if args.eval_model:
        cmd.extend(["--eval-model", args.eval_model])
    if args.improve_model:
        cmd.extend(["--improve-model", args.improve_model])
    if args.verbose:
        cmd.append("--verbose")
    return cmd


def main() -> None:
    """Parse args and run the optimization loop."""
    parser = argparse.ArgumentParser(
        description=(
            "Run autoresearch-style continuous optimization on a target skill "
            "using the shared benchmarking loop."
        )
    )
    parser.add_argument("--skill-path", required=True, help="Path to target skill directory")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON")
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--runs-per-query", type=int, default=2)
    parser.add_argument("--num-workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=25)
    parser.add_argument("--holdout", type=float, default=0.34)
    parser.add_argument("--eval-engine", default="claude", choices=["claude"])
    parser.add_argument("--improve-engine", default="copilot", choices=["claude", "copilot"])
    parser.add_argument("--eval-model", default=None)
    parser.add_argument("--improve-model", default="gpt-5-mini")
    parser.add_argument("--report", default="none")
    parser.add_argument("--results-dir", required=True, help="Base results directory")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    plugin_root = Path(__file__).resolve().parents[3]
    command = _build_command(args, plugin_root)

    env = os.environ.copy()
    env.pop("GITHUB_TOKEN", None)
    env.pop("GH_TOKEN", None)
    env.pop("COPILOT_GITHUB_TOKEN", None)

    result = subprocess.run(command, env=env, check=False)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()


<!-- Source: plugin-code/agent-scaffolders/scripts/execute.py -->
#!/usr/bin/env python
"""Execution wrapper for continuous skill optimization loops.

This script runs the shared benchmarking loop with safe defaults:
- baseline-first iteration governance
- keep/discard/crash ledger output
- optional Copilot improvement backend with token-precedence cleanup
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def _build_command(args: argparse.Namespace, plugin_root: Path) -> list[str]:
    """Build the run_loop invocation command."""
    run_loop_path = plugin_root / "scripts" / "benchmarking" / "run_loop.py"
    cmd = [
        "python",
        str(run_loop_path),
        "--eval-set",
        args.eval_set,
        "--skill-path",
        args.skill_path,
        "--max-iterations",
        str(args.max_iterations),
        "--runs-per-query",
        str(args.runs_per_query),
        "--num-workers",
        str(args.num_workers),
        "--timeout",
        str(args.timeout),
        "--holdout",
        str(args.holdout),
        "--eval-engine",
        args.eval_engine,
        "--improve-engine",
        args.improve_engine,
        "--results-dir",
        args.results_dir,
        "--report",
        args.report,
    ]
    if args.eval_model:
        cmd.extend(["--eval-model", args.eval_model])
    if args.improve_model:
        cmd.extend(["--improve-model", args.improve_model])
    if args.verbose:
        cmd.append("--verbose")
    return cmd


def main() -> None:
    """Parse args and run the optimization loop."""
    parser = argparse.ArgumentParser(
        description=(
            "Run autoresearch-style continuous optimization on a target skill "
 

*(combined content truncated)*

## See Also

- [[use-npx-to-lazily-execute-mermaid-cli-so-the-user-doesnt-need-to-globally-install-it]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-docker-skill/execute.py`
- **Indexed:** 2026-04-27T05:21:04.116815+00:00
