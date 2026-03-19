#!/usr/bin/env python3
"""
Purpose: Automated Trainer for Skill Improvement.
Simulates Karpathy's train.py loop for Agentic OS Skills.
Calculates objective routing accuracy from evals/evals.json.
"""

import json
import os
import sys
import argparse
import re
import csv
from datetime import datetime
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
    """
    passed = 0
    total = len(evals)
    if total == 0:
        return {"accuracy": 0.0, "details": []}

    details = []
    
    # Scoped Keyword Extraction: Extract the first frontmatter block
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', skill_content, re.DOTALL | re.MULTILINE)
    routing_content = skill_content # Fallback
    if frontmatter_match:
        routing_content = frontmatter_match.group(1)
        
    skill_keywords = set(re.findall(r'\w{4,}', routing_content.lower()))
    skill_keywords.add(skill_name.lower())
    
    for item in evals:
        # Support both 'prompt'/'query' and 'expected'/'should_trigger'
        prompt = (item.get("prompt") or item.get("query", "")).lower()
        expected_raw = item.get("expected") or item.get("should_trigger")
        
        if expected_raw is True: expected = "pass"
        elif expected_raw is False: expected = "fail"
        else: expected = str(expected_raw).lower()
        
        # Does the prompt overlap with skill keywords?
        prompt_words = set(re.findall(r'\w{4,}', prompt))
        overlap = prompt_words.intersection(skill_keywords)
        triggers = len(overlap) > 0
        
        is_correct = False
        if expected == "pass" and triggers:
            is_correct = True
        elif expected == "fail" and not triggers:
            is_correct = True
            
        if is_correct:
            passed += 1
            details.append({"prompt": prompt, "result": "CORRECT"})
        else:
            details.append({"prompt": prompt, "result": "INCORRECT", "expected": expected, "triggered": triggers})
            
    return {"accuracy": passed / total, "details": details}

def main():
    parser = argparse.ArgumentParser(description="Skill Improvement Evaluator (Trainer)")
    parser.add_argument("--skill", "--target", dest="skill", required=True,
                        help="Path to the SKILL.md to evaluate (--target is an alias for programmatic callers)")
    parser.add_argument("--baseline", action="store_true", help="Record result as baseline")
    parser.add_argument("--desc", default="Manual iteration", help="Description for results.tsv")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output machine-readable JSON: {\"quality_score\": N} for optimizer callers")

    args = parser.parse_args()
    skill_path = Path(args.skill).resolve()
    skill_dir = skill_path.parent
    
    if not skill_path.exists():
        print(f"Error: Skill not found at {skill_path}")
        sys.exit(1)
        
    content = skill_path.read_text()
    skill_name = skill_path.parent.name # Assumes standard skill folder structure
    
    # 1. Load Evals
    evals_path = skill_dir / "evals" / "evals.json"
    if not evals_path.exists():
        print(f"Warning: No evals.json found at {evals_path}. Using fallback heuristics only.")
        eval_data = []
    else:
        with open(evals_path, 'r') as f:
            eval_data = json.load(f)
            
    # 2. Run Evaluations
    heuristic = calculate_heuristic_score(content)
    routing = run_routing_eval(content, skill_name, eval_data)
    
    # Final numeric score (weighted average of accuracy and structural health)
    final_score = (routing["accuracy"] * 0.7) + (heuristic["score"] * 0.3)
    
    # 3. Handle Persistence (results.tsv)
    results_path = skill_dir / "evals" / "results.tsv"
    os.makedirs(results_path.parent, exist_ok=True)
    
    # Load last baseline
    last_score = 0.0
    if results_path.exists():
        with open(results_path, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                try:
                    last_score = float(row.get('score', 0))
                except (ValueError, TypeError):
                    pass

    # Write new entry
    headers = ["timestamp", "score", "accuracy", "heuristic", "status", "description"]
    write_header = not results_path.exists()
    
    status = "KEEP" if final_score >= last_score else "DISCARD"
    if last_score == 0: status = "BASELINE"
    
    with open(results_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, delimiter='\t')
        if write_header:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "score": f"{final_score:.4f}",
            "accuracy": f"{routing['accuracy']:.4f}",
            "heuristic": f"{heuristic['score']:.4f}",
            "status": status,
            "description": args.desc
        })

    # Machine-readable output for programmatic callers (execute.py --json)
    if args.json_output:
        print(json.dumps({"quality_score": final_score}))
        return

    print(f"--- Skill Evaluation: {skill_path.name} ---")
    print(f"Routing Accuracy: {routing['accuracy']:.4f}")
    print(f"Heuristic Health: {heuristic['score']:.4f}")
    print(f"FINAL SCORE: {final_score:.4f} (Baseline: {last_score:.4f})")
    print(f"STATUS: {status}")
    
    if routing["accuracy"] < 1.0:
        print("\nRouting Failures:")
        for d in routing["details"]:
            if d["result"] == "INCORRECT":
                trigger_msg = "triggered when it shouldn't" if d["triggered"] else "failed to trigger"
                print(f"- {d['prompt']}: {trigger_msg}")

    if heuristic["score"] < 1.0:
        print("\nStructural Recommendations:")
        for f in heuristic["feedback"]:
            print(f"- {f}")
    
    if status in ["KEEP", "BASELINE"] and final_score > 0.7:
        print("\n<EVAL_PASSED>")

if __name__ == "__main__":
    main()
