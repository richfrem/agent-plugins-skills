#!/usr/bin/env python3
"""
evaluate.py -- Locked loop gate for the autoresearch loop
==========================================================

Purpose:
    Single responsibility: "Should the loop keep or discard this change?"

    Calls eval_runner.py once (--json), reads the last BASELINE row from
    <target-skill>/evals/results.tsv, compares score and f1, appends one row
    to that same TSV, then exits 0 (KEEP) or 1 (DISCARD).

    DO NOT MODIFY THIS FILE. It is the locked evaluator. Only the target
    SKILL.md is the mutation target.

Usage (run from the plugin root or any directory):
    python scripts/evaluate.py --skill <path/to/mutation-target>
    python scripts/evaluate.py --target <path/to/mutation-target> --desc "what changed"
    python scripts/evaluate.py --skill <path/to/mutation-target> --baseline

    --skill and --target are aliases. evaluate.py accepts any file as input,
    but eval_runner.py scoring is optimized for SKILL.md targets (YAML frontmatter
    + <example> tags). Non-SKILL.md targets score accuracy=0.0 and receive heuristic
    penalties for missing SKILL.md structure — see eval_runner.py Known Limitations.

Karpathy mapping:
    This file = prepare.py (gate logic half)
    eval_runner.py = prepare.py (metric producer half)
    <mutation-target> = train.py (SKILL.md, .py, config, or any file type)

KEEP condition: score >= baseline_score AND f1 >= baseline_f1
    Dual guard prevents keyword-stuffing exploit (padding triggers raises
    recall but drops precision, so F1 falls even as accuracy rises).
"""

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# evaluate.py lives at plugins/agent-agentic-os/scripts/evaluate.py
HERE = Path(__file__).parent.resolve()
EVAL_RUNNER = HERE / "eval_runner.py"

HEADERS = ["timestamp", "commit", "score", "baseline", "accuracy", "heuristic", "f1", "status", "description"]

# Files the loop must never modify — checked at startup
LOCKED_FILES = [HERE / "evaluate.py", HERE / "eval_runner.py"]

# Name of the SHA256 snapshot file saved alongside results.tsv at baseline time
LOCK_HASHES_FILENAME = ".lock.hashes"


def check_locked_files(skill_root: Path, evals_json: Path) -> None:
    """Abort if any locked files have uncommitted modifications.

    Relying on the agent to obey 'Locked:' in program.md is not enough.
    An agent in a deep loop will eventually rewrite evaluate.py to always
    return exit 0. This check turns convention into a runtime guarantee.
    """
    to_check = LOCKED_FILES + [evals_json]
    try:
        repo_root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True, cwd=skill_root
        )
        repo_root = Path(repo_root_result.stdout.strip())
    except subprocess.CalledProcessError:
        return  # Not a git repo — skip check

    modified = []
    for f in to_check:
        if not f.exists():
            continue
        try:
            rel = f.relative_to(repo_root)
        except ValueError:
            continue
        result = subprocess.run(
            ["git", "status", "--porcelain", str(rel)],
            capture_output=True, text=True, cwd=repo_root
        )
        if result.stdout.strip():
            modified.append(str(rel))

    if modified:
        print("ERROR: Locked files have been modified — aborting.", file=sys.stderr)
        for m in modified:
            print(f"  modified: {m}", file=sys.stderr)
        print("Restore them with: git checkout -- <file>", file=sys.stderr)
        sys.exit(3)


def _sha256(path: Path) -> str:
    """Return hex SHA256 of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def save_lock_hashes(results_tsv: Path, files_to_hash: list[Path]) -> None:
    """Snapshot SHA256 hashes of locked files next to results.tsv.

    Called once when --baseline is recorded.  The snapshot is later compared
    on every loop iteration by check_sha256_hashes(), closing the gap where
    a committed (not just dirty) modification to evaluate.py or eval_runner.py
    would silently pass the git-status check.
    """
    hashes: dict[str, str] = {}
    for f in files_to_hash:
        if f.exists():
            hashes[str(f)] = _sha256(f)
    lock_hashes_path = results_tsv.parent / LOCK_HASHES_FILENAME
    with open(lock_hashes_path, "w") as fh:
        json.dump(hashes, fh, indent=2)
    print(f"-> lock hashes written to {lock_hashes_path.name} ({len(hashes)} files)")


def check_sha256_hashes(results_tsv: Path, files_to_hash: list[Path]) -> None:
    """Abort if any locked file has changed since the baseline snapshot.

    Complements check_locked_files(): that function catches uncommitted edits
    (git status); this function catches modifications that were *committed*
    between loop iterations — the gap left open by the git-status approach.

    Silently skips if .lock.hashes does not yet exist (pre-baseline run).
    """
    lock_hashes_path = results_tsv.parent / LOCK_HASHES_FILENAME
    if not lock_hashes_path.exists():
        return  # No snapshot yet — baseline not yet established

    with open(lock_hashes_path) as fh:
        saved: dict[str, str] = json.load(fh)

    tampered: list[str] = []
    for f in files_to_hash:
        key = str(f)
        if key in saved and f.exists():
            if _sha256(f) != saved[key]:
                tampered.append(key)

    if tampered:
        print("ERROR: Locked files have changed since baseline snapshot (SHA256 mismatch) — aborting.", file=sys.stderr)
        for t in tampered:
            print(f"  tampered: {t}", file=sys.stderr)
        print(f"Restore with: git checkout <baseline-commit> -- <file>", file=sys.stderr)
        sys.exit(3)


def get_commit(cwd: Path) -> str:
    """Return short git commit hash, or 'uncommitted' if not in a repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "uncommitted"


def run_eval_runner(skill_root: Path) -> dict:
    """Call eval_runner.py --json once with the skill folder and return all metric fields."""
    result = subprocess.run(
        [sys.executable, str(EVAL_RUNNER), "--skill", str(skill_root), "--json"],
        capture_output=True, text=True,
        cwd=skill_root,
    )
    if result.returncode != 0:
        print(f"ERROR: eval_runner.py failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        print(f"ERROR: could not parse eval_runner output: {result.stdout!r}", file=sys.stderr)
        sys.exit(2)


def load_baseline(results_tsv: Path) -> tuple[float, float]:
    """Return (baseline_score, baseline_f1) from the LAST BASELINE row, or (0.0, 0.0)."""
    if not results_tsv.exists():
        return 0.0, 0.0
    last_baseline: dict | None = None
    with open(results_tsv, newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("status") == "BASELINE":
                last_baseline = row
    if last_baseline is None:
        return 0.0, 0.0
    try:
        score = float(last_baseline.get("score", 0))
        # Support both "f1" (new schema) and "llm_routing_score" (legacy)
        f1_raw = last_baseline.get("f1") or last_baseline.get("llm_routing_score") or "0"
        try:
            f1 = float(f1_raw)
        except (ValueError, TypeError):
            f1 = 0.0
        return score, f1
    except (ValueError, KeyError):
        return 0.0, 0.0


def write_row(results_tsv: Path, commit: str, score: float, baseline: float,
              accuracy: float, heuristic: float, f1: float,
              status: str, desc: str) -> None:
    """Append one row to <target-skill>/evals/results.tsv."""
    results_tsv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not results_tsv.exists()
    with open(results_tsv, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, delimiter="\t")
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "commit": commit,
            "score": f"{score:.4f}",
            "baseline": f"{baseline:.4f}",
            "accuracy": f"{accuracy:.4f}",
            "heuristic": f"{heuristic:.4f}",
            "f1": f"{f1:.4f}",
            "status": status,
            "description": desc,
        })


def main() -> None:
    parser = argparse.ArgumentParser(description="Locked autoresearch loop gate")
    parser.add_argument(
        "--skill", "--target", dest="skill", required=True,
        help="Path to the skill folder (or any file within it for backward compat)"
    )
    parser.add_argument("--desc", default="iteration", help="Description for results.tsv")
    parser.add_argument("--baseline", action="store_true", help="Record this run as the new baseline")
    args = parser.parse_args()

    target = Path(args.skill).resolve()

    # Accept skill folder path OR a file path within the skill (backward compat)
    if target.is_dir():
        skill_root = target
    else:
        skill_root = target.parent

    if not skill_root.exists():
        print(f"ERROR: Skill folder not found at {skill_root}", file=sys.stderr)
        sys.exit(2)

    results_tsv = skill_root / "evals" / "results.tsv"
    evals_json = skill_root / "evals" / "evals.json"

    locked_files_to_hash = LOCKED_FILES + [evals_json]

    check_locked_files(skill_root, evals_json)
    check_sha256_hashes(results_tsv, locked_files_to_hash)

    commit = get_commit(skill_root)
    data = run_eval_runner(skill_root)

    score = float(data["quality_score"])
    accuracy = float(data.get("accuracy", 0.0))
    heuristic = float(data.get("heuristic", 0.0))
    f1 = float(data.get("f1", 0.0))

    baseline_score, baseline_f1 = load_baseline(results_tsv)

    if args.baseline or baseline_score == 0.0:
        status = "BASELINE"
    elif round(score, 4) >= round(baseline_score, 4) and round(f1, 4) >= round(baseline_f1, 4):
        status = "KEEP"
    else:
        status = "DISCARD"

    write_row(results_tsv, commit, score, baseline_score, accuracy, heuristic, f1, status, args.desc)

    if status == "BASELINE":
        # Snapshot locked file hashes alongside results.tsv so subsequent runs can
        # detect committed modifications (not just dirty-working-tree changes).
        save_lock_hashes(results_tsv, locked_files_to_hash)

    print(f"score={score:.4f}  baseline={baseline_score:.4f}  f1={f1:.4f}  baseline_f1={baseline_f1:.4f}  STATUS: {status}")
    print(f"commit={commit}  skill={skill_root.name}  desc={args.desc!r}")

    if status == "DISCARD":
        # Revert the entire skill folder — the mutation target may be any file within it
        # (SKILL.md, a script, a reference doc). Reverting '.' from skill_root restores
        # all tracked files in the folder and subdirectories to HEAD.
        revert = subprocess.run(
            ["git", "checkout", "--", "."],
            capture_output=True, text=True, cwd=skill_root,
        )
        if revert.returncode == 0:
            print(f"-> reverted: {skill_root.name}/")
        else:
            print(f"WARNING: git checkout failed: {revert.stderr.strip()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
