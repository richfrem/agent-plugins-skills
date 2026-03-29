#!/usr/bin/env python3
"""
eval_runner.py — Pure skill scorer for the autoresearch loop
============================================================

Purpose:
    Reads SKILL.md frontmatter keywords and evals/evals.json, computes
    quality_score / accuracy / heuristic / f1. Writes nothing to disk.
    This is the metric producer in the Karpathy autoresearch pattern.

    Single responsibility: answer "What is the score of this SKILL.md?"
    All KEEP/DISCARD decisions and TSV writes belong in evaluate.py.

Usage:
    python3 eval_runner.py --skill PATH_TO_SKILL.md
    python3 eval_runner.py --skill PATH_TO_SKILL.md --json

CLI Arguments:
    --skill <path>   Target SKILL.md file to evaluate
    --json           Output machine-readable JSON with all metric fields

Output (--json):
    {"quality_score": N, "accuracy": N, "f1": N, "heuristic": N}

Output (default):
    Human-readable score report printed to stdout

Input Files:
    - Specified SKILL.md (frontmatter keywords extracted for routing)
    - <skill_dir>/evals/evals.json (test prompts with expected trigger outcomes)

Key Functions:
    calculate_heuristic_score()  Structural health check (examples, length)
    run_routing_eval()           Keyword routing accuracy + F1 score

Consumed by:
    - evaluate.py (autoresearch loop gate, via --json)
    - CI/CD validation, standalone manual scoring
"""

import json
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any

def calculate_heuristic_score(skill_content: str) -> Dict[str, Any]:
    """
    Checks for structural quality using regex.
    """
    score = 1.0
    feedback = []
    
    # Check for <example> XML tags specifically
    example_tags = re.findall(r'<example>.*?</example>', skill_content, re.DOTALL)
    if not example_tags:
        score -= 0.3
        feedback.append("Missing <example> XML blocks.")
    elif len(example_tags) < 2:
        score -= 0.1
        feedback.append("Only one <example> block found. Recommend at least two.")

    if len(skill_content) < 200:
        score -= 0.2
        feedback.append("Description is very short (under 200 chars).")

    return {"score": max(0.0, score), "feedback": feedback}

def run_routing_eval(skill_content: str, skill_name: str, evals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simulates routing based on keyword/description match.
    Scopes keyword extraction to the frontmatter for Phase A accuracy.
    Returns accuracy, precision, recall, and F1 score to close the keyword-stuffing exploit:
    a change that pads triggers (raises recall) but breaks precision scores lower on F1.
    """
    total = len(evals)
    if total == 0:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "details": []}

    # Scoped Keyword Extraction: frontmatter only — fail hard if malformed.
    # If the agent breaks the YAML delimiters, scoring returns 0.0 rather than
    # silently falling back to the full file body (which would reward the exploit).
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', skill_content, re.DOTALL | re.MULTILINE)
    if not frontmatter_match:
        return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0,
                "details": [{"error": "FRONTMATTER_MISSING_OR_MALFORMED"}]}
    routing_content = frontmatter_match.group(1)

    skill_keywords = set(re.findall(r'\w{4,}', routing_content.lower()))
    skill_keywords.add(skill_name.lower())

    passed = 0
    true_pos = 0   # should_trigger=True  and triggered
    false_pos = 0  # should_trigger=False and triggered
    false_neg = 0  # should_trigger=True  and NOT triggered
    details = []

    for item in evals:
        # Support both 'prompt'/'query' and 'expected'/'should_trigger'
        prompt = (item.get("prompt") or item.get("query", "")).lower()
        expected_raw = item.get("expected") or item.get("should_trigger")

        if expected_raw is True:
            expected = "pass"
        elif expected_raw is False:
            expected = "fail"
        else:
            expected = str(expected_raw).lower()

        # Does the prompt overlap with skill keywords?
        prompt_words = set(re.findall(r'\w{4,}', prompt))
        overlap = prompt_words.intersection(skill_keywords)
        triggers = len(overlap) > 0

        is_correct = False
        if expected == "pass" and triggers:
            is_correct = True
            true_pos += 1
        elif expected == "fail" and not triggers:
            is_correct = True
        elif expected == "pass" and not triggers:
            false_neg += 1
        elif expected == "fail" and triggers:
            false_pos += 1

        if is_correct:
            passed += 1
            details.append({"prompt": prompt, "result": "CORRECT"})
        else:
            details.append({"prompt": prompt, "result": "INCORRECT",
                            "expected": expected, "triggered": triggers})

    accuracy = passed / total
    precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0.0
    recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {"accuracy": accuracy, "precision": precision, "recall": recall, "f1": f1, "details": details}

def main() -> None:
    parser = argparse.ArgumentParser(description="Pure skill scorer — writes nothing to disk")
    parser.add_argument("--skill", "--target", dest="skill", required=True,
                        help="Path to the SKILL.md to evaluate")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output machine-readable JSON with all metric fields")

    args = parser.parse_args()
    skill_path = Path(args.skill).resolve()
    skill_dir = skill_path.parent

    if not skill_path.exists():
        print(f"Error: Skill not found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    content = skill_path.read_text()
    skill_name = skill_dir.name

    # Load evals
    evals_path = skill_dir / "evals" / "evals.json"
    if not evals_path.exists():
        print(f"Warning: No evals.json found at {evals_path}. Using heuristics only.", file=sys.stderr)
        eval_data = []
    else:
        with open(evals_path, "r") as f:
            eval_data = json.load(f)

    # Score
    heuristic = calculate_heuristic_score(content)
    routing = run_routing_eval(content, skill_name, eval_data)
    quality_score = (routing["accuracy"] * 0.7) + (heuristic["score"] * 0.3)
    f1 = routing["f1"]

    if args.json_output:
        print(json.dumps({
            "quality_score": quality_score,
            "accuracy": routing["accuracy"],
            "f1": f1,
            "heuristic": heuristic["score"],
        }))
        return

    print(f"--- Skill Evaluation: {skill_path.name} ---")
    print(f"Routing Accuracy : {routing['accuracy']:.4f}")
    print(f"F1 Score         : {f1:.4f}  (precision={routing['precision']:.4f}, recall={routing['recall']:.4f})")
    print(f"Heuristic Health : {heuristic['score']:.4f}")
    print(f"FINAL SCORE      : {quality_score:.4f}")

    if routing["accuracy"] < 1.0:
        print("\nRouting Failures:")
        for d in routing["details"]:
            if d["result"] == "INCORRECT":
                trigger_msg = "triggered when it shouldn't" if d["triggered"] else "failed to trigger"
                print(f"  - {d['prompt']}: {trigger_msg}")

    if heuristic["score"] < 1.0:
        print("\nStructural Recommendations:")
        for fb in heuristic["feedback"]:
            print(f"  - {fb}")

if __name__ == "__main__":
    main()
