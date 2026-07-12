#!/usr/bin/env python
"""
eval_runner.py -- Pure skill scorer for the autoresearch loop
=============================================================

Purpose:
    Evaluates a skill FOLDER against its evals/evals.json, computing
    quality_score / accuracy / heuristic / f1. Writes nothing to disk.
    This is the metric producer in the Karpathy autoresearch pattern.

    Single responsibility: answer "What is the quality of this skill folder?"
    All KEEP/DISCARD decisions and TSV writes belong in evaluate.py.

    A skill is a folder, not a file. The mutation target may be SKILL.md,
    a script, a reference doc, or any file within the skill folder. The
    evaluator scores the folder holistically each iteration.

Usage:
    pythonal_runner.py --skill PATH_TO_SKILL_DIR
    pythonal_runner.py --skill PATH_TO_SKILL_DIR --json
    pythonal_runner.py --skill PATH_TO_SKILL_DIR --snapshot
    pythonal_runner.py --skill PATH_TO_SKILL.md         # backward compat

CLI Arguments:
    --skill <path>   Skill folder path (or SKILL.md path for backward compat)
    --json           Output machine-readable JSON with all metric fields
    --snapshot       Print a compact skill state snapshot (score trend, fp/fn rates)

Output (--json):
    {
      "quality_score": N, "accuracy": N, "f1": N, "heuristic": N,
      "routing_detail": [{input, should_trigger, matched_keywords, triggered, correct, failure_reason?}],
      "heuristic_detail": [{check, penalty, passed}]
    }

Output (--snapshot):
    Markdown block: score trend, KEEP/DISCARD history, fp/fn rates, dominant problem,
    recommended focus. Reads evals/results.tsv and evals/traces/ for history.

Output (default):
    Human-readable score report printed to stdout

Input Files:
    - <skill_dir>/SKILL.md        frontmatter keywords for routing accuracy
    - <skill_dir>/evals/evals.json test prompts with expected trigger outcomes
    - <skill_dir>/scripts/*.py    syntax-checked via py_compile
    - <skill_dir>/references/*.md checked for non-empty content

Key Input Dependencies:
    - <skill_dir>/SKILL.md, evals/evals.json, evals/results.tsv, evals/traces/*.json

Key Functions:
    calculate_heuristic_score()  Folder-aware structural health (agentskills.io spec)
    run_routing_eval()           Keyword routing accuracy + F1 score
    build_snapshot()             Skill state snapshot for proposer warm-up

Scoring formula:
    quality_score = (routing_accuracy * 0.7) + (heuristic_score * 0.3)

Consumed by:
    - evaluate.py (autoresearch loop gate, via --json)
    - CI/CD validation, standalone manual scoring
    - os-skill-improvement proposer (via --snapshot before mutation proposals)
"""

import json
import re
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------

def _extract_frontmatter(skill_content: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (frontmatter_text, body_text) or (None, None) if not found."""
    m = re.search(r'^---[ \t]*\n(.*?)\n---[ \t]*\n', skill_content, re.DOTALL | re.MULTILINE)
    if not m:
        return None, None
    return m.group(1), skill_content[m.end():]


def _extract_field(frontmatter_text: str, key: str) -> str:
    """Extract a scalar YAML field. Handles inline and > / | block scalar styles."""
    # Inline: key: some value (not a block indicator)
    inline = re.search(
        r'^' + re.escape(key) + r':\s+(?![>|])(.+)$',
        frontmatter_text, re.MULTILINE
    )
    if inline:
        return inline.group(1).strip().strip('"').strip("'")
    # Block scalar: key: > or key: |  (collect indented continuation lines)
    block = re.search(
        r'^' + re.escape(key) + r':\s*[>|][>|-]*[ \t]*\n((?:[ \t]+[^\n]*\n?)*)',
        frontmatter_text, re.MULTILINE
    )
    if block:
        lines = [line.strip() for line in block.group(1).splitlines() if line.strip()]
        return ' '.join(lines)
    return ''


# ---------------------------------------------------------------------------
# Heuristic scorer (folder-aware, agentskills.io spec)
# ---------------------------------------------------------------------------

def _check_name_field(frontmatter_text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Validate the 'name' field per agentskills.io spec. Returns (name, hard_fail_dict_or_None)."""
    name = _extract_field(frontmatter_text, "name")
    if not name:
        return None, {"score": 0.0, "feedback": ["HARD FAIL: 'name' field missing from frontmatter."],
                "heuristic_detail": [{"check": "name_present", "penalty": -1.0, "passed": False}]}
    if not (1 <= len(name) <= 64):
        return None, {"score": 0.0, "feedback": [
            f"HARD FAIL: 'name' must be 1-64 characters (got {len(name)}): {name!r}"
        ], "heuristic_detail": [{"check": "name_length", "penalty": -1.0, "passed": False}]}
    # Only lowercase letters and hyphens; must start and end with a letter
    if not re.fullmatch(r'[a-z]([a-z-]*[a-z])?', name):
        return None, {"score": 0.0, "feedback": [
            f"HARD FAIL: 'name' must only contain [a-z-] and start/end with a letter: {name!r}"
        ], "heuristic_detail": [{"check": "name_format", "penalty": -1.0, "passed": False}]}
    if '--' in name:
        return None, {"score": 0.0, "feedback": [
            f"HARD FAIL: 'name' may not contain double hyphens: {name!r}"
        ], "heuristic_detail": [{"check": "name_no_double_hyphen", "penalty": -1.0, "passed": False}]}
    return name, None


def _penalize_folder_and_description(skill_dir: Path, name: str, description: str) -> Tuple[float, List[str], List[Dict[str, Any]]]:
    """Check folder-name match and description length. Returns (score_delta, feedback, heuristic_detail)."""
    score_delta = 0.0
    feedback: List[str] = []
    detail: List[Dict[str, Any]] = []

    # Folder name must match SKILL.md name
    if skill_dir.name != name:
        score_delta -= 0.20
        feedback.append(
            f"Folder name '{skill_dir.name}' does not match SKILL.md 'name: {name}'. "
            f"Rename the folder to match."
        )
        detail.append({"check": "folder_name_matches", "penalty": -0.20, "passed": False})
    else:
        detail.append({"check": "folder_name_matches", "penalty": 0.0, "passed": True})

    # Description length cap
    if len(description) > 1024:
        score_delta -= 0.05
        feedback.append(
            f"'description' is {len(description)} chars; spec maximum is 1024."
        )
        detail.append({"check": "description_length", "penalty": -0.05, "passed": False})
    else:
        detail.append({"check": "description_length", "penalty": 0.0, "passed": True})

    return score_delta, feedback, detail


def _penalize_examples_and_body(skill_content: str, body_text: Optional[str]) -> Tuple[float, List[str], List[Dict[str, Any]]]:
    """Check <example> block count and body length. Returns (score_delta, feedback, heuristic_detail)."""
    score_delta = 0.0
    feedback: List[str] = []
    detail: List[Dict[str, Any]] = []

    # <example> XML blocks
    examples = re.findall(r'<example>.*?</example>', skill_content, re.DOTALL)
    if not examples:
        score_delta -= 0.30
        feedback.append("Missing <example> XML blocks.")
        detail.append({"check": "example_blocks", "penalty": -0.30, "passed": False})
    elif len(examples) < 2:
        score_delta -= 0.10
        feedback.append("Only one <example> block found. Recommend at least two.")
        detail.append({"check": "example_blocks", "penalty": -0.10, "passed": False,
                                  "note": f"only {len(examples)} block(s) found"})
    else:
        detail.append({"check": "example_blocks", "penalty": 0.0, "passed": True,
                                  "note": f"{len(examples)} blocks found"})

    # Body length
    if body_text is not None:
        body_lines = len(body_text.splitlines())
        if body_lines > 500:
            score_delta -= 0.10
            feedback.append(
                f"Body is {body_lines} lines. Spec recommends under 500 — "
                f"move detailed reference material to separate files."
            )
            detail.append({"check": "body_length", "penalty": -0.10, "passed": False,
                                      "note": f"{body_lines} lines"})
        else:
            detail.append({"check": "body_length", "penalty": 0.0, "passed": True})

    return score_delta, feedback, detail


def _penalize_broken_scripts(skill_dir: Path) -> Tuple[float, List[str], List[Dict[str, Any]]]:
    """Check scripts/*.py for py_compile failures. Returns (score_delta, feedback, heuristic_detail)."""
    score_delta = 0.0
    feedback: List[str] = []
    detail: List[Dict[str, Any]] = []

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists() and scripts_dir.is_dir():
        broken: List[str] = []
        for py_file in sorted(scripts_dir.glob("*.py")):
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                broken.append(py_file.name)
        if broken:
            penalty = min(0.40, 0.20 * len(broken))
            score_delta -= penalty
            for bf in broken:
                detail.append({"check": f"py_compile:{bf}", "penalty": -0.20, "passed": False})
            feedback.append(
                f"scripts/ has {len(broken)} file(s) failing py_compile: "
                f"{', '.join(broken)}"
            )

    return score_delta, feedback, detail


def _penalize_empty_references(skill_dir: Path) -> Tuple[float, List[str], List[Dict[str, Any]]]:
    """Check references/*.md for empty files. Returns (score_delta, feedback, heuristic_detail)."""
    score_delta = 0.0
    feedback: List[str] = []
    detail: List[Dict[str, Any]] = []

    references_dir = skill_dir / "references"
    if references_dir.exists() and references_dir.is_dir():
        empty_refs: List[str] = []
        for md_file in sorted(references_dir.glob("*.md")):
            if md_file.stat().st_size == 0:
                empty_refs.append(md_file.name)
        if empty_refs:
            penalty = min(0.20, 0.10 * len(empty_refs))
            score_delta -= penalty
            feedback.append(
                f"references/ has {len(empty_refs)} empty .md file(s): "
                f"{', '.join(empty_refs)}"
            )
            for ef in empty_refs:
                detail.append({"check": f"references_empty:{ef}", "penalty": -0.10, "passed": False})
        else:
            if references_dir.exists():
                detail.append({"check": "references_non_empty", "penalty": 0.0, "passed": True})

    return score_delta, feedback, detail


def _apply_soft_penalties(skill_dir: Path, skill_content: str, body_text: Optional[str],
                           name: str, description: str) -> Dict[str, Any]:
    """Apply all soft-penalty checks (folder/description, examples/body, scripts, references)."""
    score = 1.0
    feedback: List[str] = []
    heuristic_detail: List[Dict[str, Any]] = []

    for delta, fb, detail in (
        _penalize_folder_and_description(skill_dir, name, description),
        _penalize_examples_and_body(skill_content, body_text),
        _penalize_broken_scripts(skill_dir),
        _penalize_empty_references(skill_dir),
    ):
        score += delta
        feedback.extend(fb)
        heuristic_detail.extend(detail)

    return {"score": max(0.0, score), "feedback": feedback, "heuristic_detail": heuristic_detail}


def calculate_heuristic_score(skill_dir: Path, skill_content: str) -> Dict[str, Any]:
    """
    Folder-aware structural health check following the agentskills.io spec.

    Hard fails (score=0.0 returned immediately):
      - Frontmatter missing or unparseable (no --- boundaries)
      - 'name' field: missing, not 1-64 chars, chars outside [a-z-],
        starts/ends with hyphen, or contains double hyphens (--)
      - 'description' field: missing or empty

    Soft penalties (deducted from 1.0 base):
      Folder name != SKILL.md 'name' field     : -0.20
      'description' exceeds 1024 chars         : -0.05
      No <example> XML blocks                  : -0.30
      Fewer than 2 <example> blocks            : -0.10
      Body > 500 lines                         : -0.10
      scripts/*.py fails py_compile (-0.2 each, capped at -0.40)
      references/*.md is empty  (-0.1 each, capped at -0.20)
    """
    # ---- Frontmatter (hard fail) ----
    frontmatter_text, body_text = _extract_frontmatter(skill_content)
    if frontmatter_text is None:
        return {
            "score": 0.0,
            "feedback": ["HARD FAIL: SKILL.md frontmatter missing or malformed (no --- boundaries)."],
            "heuristic_detail": [{"check": "frontmatter", "penalty": -1.0, "passed": False}],
        }

    # ---- name field (hard fail) ----
    name, name_fail = _check_name_field(frontmatter_text)
    if name_fail:
        return name_fail

    # ---- description field (hard fail) ----
    description = _extract_field(frontmatter_text, "description")
    if not description:
        return {"score": 0.0, "feedback": ["HARD FAIL: 'description' field missing or empty."],
                "heuristic_detail": [{"check": "description_present", "penalty": -1.0, "passed": False}]}

    return _apply_soft_penalties(skill_dir, skill_content, body_text, name, description)


# ---------------------------------------------------------------------------
# Routing eval — returns per-input detail for trace storage
# ---------------------------------------------------------------------------

def _extract_skill_keywords(frontmatter_text: str, skill_name: str) -> set:
    """Extract routing keywords: prefer an explicit 'keywords:' list, else derive from 'description:'.

    Using the entire frontmatter causes false positives from unrelated fields
    (e.g., argument-hint, allowed-tools, exclusion-keywords) and allows
    exclusion keyword lists to paradoxically become positive triggers.
    """
    explicit_keywords_raw = _extract_field(frontmatter_text, "keywords")
    if explicit_keywords_raw:
        # Parse YAML list items (lines starting with '-')
        kw_lines = [l.strip().lstrip('- ').strip() for l in explicit_keywords_raw.splitlines() if l.strip()]
        skill_keywords = set(w.lower() for kw in kw_lines for w in re.findall(r'\w{4,}', kw))
    else:
        description = _extract_field(frontmatter_text, "description")
        skill_keywords = set(re.findall(r'\w{4,}', description.lower()))
    skill_keywords.add(skill_name.lower())
    return skill_keywords


def _score_eval_item(item: Dict[str, Any], skill_keywords: set) -> Dict[str, Any]:
    """Score a single eval item against skill_keywords. Returns correctness flags plus detail/summary entries."""
    prompt = (item.get("prompt") or item.get("query", "") or item.get("input", "")).lower()
    expected_raw = item.get("expected") or item.get("should_trigger")

    if expected_raw is True:
        expected = "pass"
    elif expected_raw is False:
        expected = "fail"
    else:
        expected = str(expected_raw).lower()

    prompt_words = set(re.findall(r'\w{4,}', prompt))
    matched = sorted(prompt_words.intersection(skill_keywords))
    triggers = len(matched) > 0
    should_trigger = (expected == "pass")

    is_correct = False
    is_true_pos = is_false_pos = is_false_neg = False
    if expected == "pass" and triggers:
        is_correct = True
        is_true_pos = True
    elif expected == "fail" and not triggers:
        is_correct = True
    elif expected == "pass" and not triggers:
        is_false_neg = True
    elif expected == "fail" and triggers:
        is_false_pos = True

    detail_entry: Dict[str, Any] = {
        "input": prompt,
        "should_trigger": should_trigger,
        "matched_keywords": matched,
        "triggered": triggers,
        "correct": is_correct,
    }
    if not is_correct:
        if expected == "fail" and triggers:
            detail_entry["failure_reason"] = f"false positive — keywords {matched} matched a should_trigger=false input"
        else:
            detail_entry["failure_reason"] = "false negative — no keywords matched a should_trigger=true input"

    if is_correct:
        summary_entry = {"prompt": prompt, "result": "CORRECT"}
    else:
        summary_entry = {"prompt": prompt, "result": "INCORRECT", "expected": expected, "triggered": triggers}

    return {
        "is_correct": is_correct, "is_true_pos": is_true_pos, "is_false_pos": is_false_pos,
        "is_false_neg": is_false_neg, "detail_entry": detail_entry, "summary_entry": summary_entry,
    }


def _score_all_evals(evals: List[Dict[str, Any]], skill_keywords: set) -> Dict[str, Any]:
    """Score every eval item, returning aggregate TP/FP/FN counters plus detail/summary lists."""
    passed = true_pos = false_pos = false_neg = 0
    details = []
    routing_detail = []

    for item in evals:
        result = _score_eval_item(item, skill_keywords)
        if result["is_correct"]:
            passed += 1
        if result["is_true_pos"]:
            true_pos += 1
        if result["is_false_pos"]:
            false_pos += 1
        if result["is_false_neg"]:
            false_neg += 1
        details.append(result["summary_entry"])
        routing_detail.append(result["detail_entry"])

    return {
        "passed": passed, "true_pos": true_pos, "false_pos": false_pos, "false_neg": false_neg,
        "details": details, "routing_detail": routing_detail,
    }


def run_routing_eval(skill_content: str, skill_name: str, evals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simulates routing based on keyword/description match.
    Scopes keyword extraction to the frontmatter for Phase A accuracy.
    Returns accuracy, precision, recall, and F1 score to close the keyword-stuffing
    exploit: padding triggers raises recall but drops precision, so F1 falls even
    as accuracy rises.

    Non-SKILL.md targets (no frontmatter) return accuracy=0.0 — only heuristic
    contributes to quality_score for those targets.
    """
    total = len(evals)
    if total == 0:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "details": [], "routing_detail": []}

    # Scoped keyword extraction: frontmatter only.
    # Hard fail if malformed — prevents the exploit where breaking the YAML
    # delimiter causes full-body fallback that artificially inflates accuracy.
    frontmatter_text, _ = _extract_frontmatter(skill_content)
    if frontmatter_text is None:
        return {
            "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0,
            "details": [{"error": "FRONTMATTER_MISSING_OR_MALFORMED"}],
            "routing_detail": [{"error": "FRONTMATTER_MISSING_OR_MALFORMED"}],
        }

    skill_keywords = _extract_skill_keywords(frontmatter_text, skill_name)
    agg = _score_all_evals(evals, skill_keywords)

    accuracy = agg["passed"] / total
    precision = agg["true_pos"] / (agg["true_pos"] + agg["false_pos"]) if (agg["true_pos"] + agg["false_pos"]) > 0 else 0.0
    recall = agg["true_pos"] / (agg["true_pos"] + agg["false_neg"]) if (agg["true_pos"] + agg["false_neg"]) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "accuracy": accuracy, "precision": precision,
        "recall": recall, "f1": f1, "details": agg["details"],
        "routing_detail": agg["routing_detail"],
    }


# ---------------------------------------------------------------------------
# Snapshot builder — reads history from results.tsv + traces/ for proposer warm-up
# ---------------------------------------------------------------------------

def _snapshot_trajectory_lines(rows: List[Dict[str, Any]]) -> List[str]:
    """Compute the score-trajectory and KEEP/DISCARD summary lines for the snapshot header."""
    baseline_rows = [r for r in rows if r.get("status") == "BASELINE"]
    iter_rows = [r for r in rows if r.get("status") in ("KEEP", "DISCARD")]
    keep_rows = [r for r in iter_rows if r.get("status") == "KEEP"]
    discard_rows = [r for r in iter_rows if r.get("status") == "DISCARD"]

    baseline_score = float(baseline_rows[-1]["score"]) if baseline_rows else 0.0
    current_score = float(rows[-1]["score"]) if rows else 0.0
    delta = round(current_score - baseline_score, 4)

    best_row = max(iter_rows, key=lambda r: float(r["score"])) if iter_rows else None
    best_score = float(best_row["score"]) if best_row else baseline_score
    best_desc = best_row.get("description", "") if best_row else "baseline"

    last_3 = [r.get("status", "?") for r in rows[-3:]]

    return [
        f"- Current score:    {current_score:.4f}  (baseline: {baseline_score:.4f}, delta: {delta:+.4f})\n",
        f"- Iterations run:   {len(iter_rows)}  ({len(keep_rows)} KEEP, {len(discard_rows)} DISCARD)\n",
        f"- Last 3 verdicts:  {', '.join(last_3)}\n",
        f"- Best ever score:  {best_score:.4f}  (\"{best_desc}\")\n",
    ]


def _compute_fp_fn_snapshot(traces_dir: Path) -> Tuple[Optional[float], Optional[float], List[str]]:
    """Read the most recent trace file's routing_detail and compute fp/fn rates plus summary lines.

    Returns (fp_rate, fn_rate, lines) — lines is empty if no trace data was available or parsing failed.
    """
    fp_rate = fn_rate = None
    lines: List[str] = []
    if traces_dir.exists():
        trace_files = sorted(traces_dir.glob("iter_*.json"))
        if trace_files:
            try:
                trace_data = json.loads(trace_files[-1].read_text())
                detail = trace_data.get("routing_detail", [])
                if detail:
                    fp = sum(1 for d in detail if not d.get("correct") and d.get("should_trigger") is False)
                    fn = sum(1 for d in detail if not d.get("correct") and d.get("should_trigger") is True)
                    total_false = sum(1 for d in detail if d.get("should_trigger") is False)
                    total_true = sum(1 for d in detail if d.get("should_trigger") is True)
                    fp_rate = fp / total_false if total_false else 0.0
                    fn_rate = fn / total_true if total_true else 0.0
                    lines.append(f"- False-positive rate: {fp_rate:.2f}  ({fp}/{total_false} should_trigger=false inputs misfire)\n")
                    lines.append(f"- False-negative rate: {fn_rate:.2f}  ({fn}/{total_true} should_trigger=true inputs missed)\n")
            except Exception:
                pass
    return fp_rate, fn_rate, lines


def _dominant_problem_lines(fp_rate: Optional[float], fn_rate: Optional[float]) -> List[str]:
    """Return markdown lines describing whether precision or recall is the dominant routing problem."""
    if fp_rate is None or fn_rate is None:
        return []
    if fp_rate > fn_rate:
        return ["- Dominant problem: PRECISION — too many false positives\n",
                "  → Do NOT add more keywords. Remove broad keywords or add adversarial <example> blocks.\n"]
    elif fn_rate > fp_rate:
        return ["- Dominant problem: RECALL — missing true triggers\n",
                "  → Add specific trigger phrases. Check 4-char word floor (no 'fix', 'run', 'doc').\n"]
    elif fp_rate == 0.0 and fn_rate == 0.0:
        return ["- Routing: clean — focus on heuristic structural improvements.\n"]
    else:
        return ["- Dominant problem: BOTH precision and recall need work.\n"]


def build_snapshot(skill_dir: Path) -> str:
    """
    Return a compact markdown skill state snapshot for the proposer.
    Reads evals/results.tsv for score history, evals/traces/ for latest per-input detail.
    Writes nothing to disk.
    """
    import csv as _csv
    results_tsv = skill_dir / "evals" / "results.tsv"
    traces_dir = skill_dir / "evals" / "traces"

    lines = ["## Skill State Snapshot\n"]

    if not results_tsv.exists():
        lines.append("- No results.tsv found — no improvement history yet.\n")
        return "".join(lines)

    rows = []
    with open(results_tsv, newline="") as f:
        reader = _csv.DictReader(f, delimiter="\t")
        for row in reader:
            rows.append(row)

    if not rows:
        lines.append("- results.tsv is empty.\n")
        return "".join(lines)

    lines.extend(_snapshot_trajectory_lines(rows))

    fp_rate, fn_rate, fp_fn_lines = _compute_fp_fn_snapshot(traces_dir)
    lines.extend(fp_fn_lines)
    lines.extend(_dominant_problem_lines(fp_rate, fn_rate))

    return "".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for eval_runner.py."""
    parser = argparse.ArgumentParser(
        description="Pure skill folder scorer — writes nothing to disk"
    )
    parser.add_argument(
        "--skill", "--target", dest="skill", required=True,
        help="Path to the skill directory (or SKILL.md file for backward compat)"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output",
        help="Output machine-readable JSON with all metric fields"
    )
    parser.add_argument(
        "--snapshot", action="store_true", dest="snapshot",
        help="Print compact skill state snapshot (score trend, fp/fn rates) for proposer warm-up"
    )
    return parser


def _resolve_skill_paths(skill_arg: str) -> Tuple[Path, Path]:
    """Resolve --skill/--target to (skill_dir, skill_md_path), accepting a dir or a file path."""
    skill_path = Path(skill_arg).resolve()
    if skill_path.is_dir():
        return skill_path, skill_path / "SKILL.md"
    return skill_path.parent, skill_path


def _load_eval_data(skill_dir: Path) -> List[Dict[str, Any]]:
    """Load evals/evals.json, supporting flat-list and dict-wrapped ({evaluations:}/{scenarios:}) schemas."""
    evals_path = skill_dir / "evals" / "evals.json"
    if not evals_path.exists():
        print(
            f"Warning: No evals.json found at {evals_path}. Using heuristics only.",
            file=sys.stderr
        )
        return []
    with open(evals_path, "r") as f:
        raw = json.load(f)
    if isinstance(raw, dict):
        return raw.get("evaluations") or raw.get("scenarios") or []
    return raw


def _print_json_report(quality_score: float, routing: Dict[str, Any], heuristic: Dict[str, Any]) -> None:
    """Print the --json machine-readable metrics report."""
    print(json.dumps({
        "quality_score": quality_score,
        "accuracy": routing["accuracy"],
        "precision": routing["precision"],
        "recall": routing["recall"],
        "f1": routing["f1"],
        "heuristic": heuristic["score"],
        "routing_detail": routing.get("routing_detail", []),
        "heuristic_detail": heuristic.get("heuristic_detail", []),
    }))


def _print_human_report(skill_dir: Path, routing: Dict[str, Any], heuristic: Dict[str, Any], quality_score: float) -> None:
    """Print the human-readable score report with routing failures and structural issues."""
    print(f"--- Skill Evaluation: {skill_dir.name}/ ---")
    print(f"Routing Accuracy : {routing['accuracy']:.4f}")
    print(f"F1 Score         : {routing['f1']:.4f}  (precision={routing['precision']:.4f}, recall={routing['recall']:.4f})")
    print(f"Heuristic Health : {heuristic['score']:.4f}")
    print(f"FINAL SCORE      : {quality_score:.4f}")

    if routing["accuracy"] < 1.0:
        print("\nRouting Failures:")
        for d in routing["details"]:
            if d["result"] == "INCORRECT":
                trigger_msg = "triggered when it should not" if d["triggered"] else "failed to trigger"
                print(f"  - {d['prompt']}: {trigger_msg}")

    if heuristic["score"] < 1.0:
        print("\nStructural Issues:")
        for fb in heuristic["feedback"]:
            print(f"  - {fb}")


def main() -> None:
    """CLI entrypoint: score a skill folder and print JSON, snapshot, or human-readable output."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    skill_dir, skill_md_path = _resolve_skill_paths(args.skill)

    # --snapshot: print history summary and exit (no scoring needed)
    if args.snapshot:
        print(build_snapshot(skill_dir))
        return

    if not skill_md_path.exists():
        print(f"Error: SKILL.md not found at {skill_md_path}", file=sys.stderr)
        sys.exit(1)

    content = skill_md_path.read_text()
    skill_name = skill_dir.name
    eval_data = _load_eval_data(skill_dir)

    heuristic = calculate_heuristic_score(skill_dir, content)
    routing = run_routing_eval(content, skill_name, eval_data)
    quality_score = (routing["accuracy"] * 0.7) + (heuristic["score"] * 0.3)

    if args.json_output:
        _print_json_report(quality_score, routing, heuristic)
        return

    _print_human_report(skill_dir, routing, heuristic, quality_score)


if __name__ == "__main__":
    main()
