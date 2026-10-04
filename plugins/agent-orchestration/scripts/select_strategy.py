#!/usr/bin/env python3
"""
Deterministic Strategy Selector for Agent Orchestration
=======================================================

Single front door for choosing an orchestration pattern based on a 4-dimension diagnostic model.
Zero external dependencies (stdlib only).

Dimensions:
1. unit_structure: minimal_direct | one_bounded | distinct_steps | many_identical
2. ordering_convergence: none | barrier | ordered_mutations
3. assurance_need: normal | adversarial
4. task_nature: build_fix | exploratory_research | system_optimization
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

SCRIPT_DIR = Path(__file__).resolve().parent
PATTERNS_FILE = SCRIPT_DIR.parent / "references" / "patterns.json"

DIMENSION_OPTIONS: Dict[str, Set[str]] = {
    "unit_structure": {"minimal_direct", "one_bounded", "distinct_steps", "many_identical"},
    "ordering_convergence": {"none", "barrier", "ordered_mutations"},
    "assurance_need": {"normal", "adversarial"},
    "task_nature": {"build_fix", "exploratory_research", "system_optimization"},
}

VALID_PATTERNS: Set[str] = {
    "direct",
    "dual-loop",
    "graph",
    "agent-swarm",
    "red-team-review",
    "learning-loop",
    "triple-loop-learning",
}

QUESTIONS: Dict[str, Dict[str, Any]] = {
    "unit_structure": {
        "prompt": "What is the structural unit breakdown of the task?",
        "options": [
            {"label": "Option A [Recommended]: One bounded change (single localized feature or bugfix)", "value": "one_bounded"},
            {"label": "Option B: Minimal direct change (single-line fix, typo, or trivial doc edit)", "value": "minimal_direct"},
            {"label": "Option C: Distinct steps with dependencies (stages, parallel fan-out, or sequential checkpoints)", "value": "distinct_steps"},
            {"label": "Option D: Many identical independent units (bulk operations across 10+ files or items)", "value": "many_identical"},
        ],
        "default": "one_bounded",
    },
    "ordering_convergence": {
        "prompt": "What ordering or convergence constraints apply to the results?",
        "options": [
            {"label": "Option A [Recommended]: None (steps do not need to merge at a synchronization barrier)", "value": "none"},
            {"label": "Option B: Results must merge at a barrier (e.g. parallel analysis joined before decisions)", "value": "barrier"},
            {"label": "Option C: Ordered mutations with gates between them (strict step-by-step state changes)", "value": "ordered_mutations"},
        ],
        "default": "none",
    },
    "assurance_need": {
        "prompt": "What level of assurance or review is required?",
        "options": [
            {"label": "Option A [Recommended]: Normal (standard test verification and code review)", "value": "normal"},
            {"label": "Option B: Adversarial review required (security boundary, architecture stress test)", "value": "adversarial"},
        ],
        "default": "normal",
    },
    "task_nature": {
        "prompt": "What is the primary nature of the task?",
        "options": [
            {"label": "Option A [Recommended]: Build/fix (concrete implementation or bug fix)", "value": "build_fix"},
            {"label": "Option B: Exploratory research (spikes, surveys, open-ended evaluations)", "value": "exploratory_research"},
            {"label": "Option C: System/friction optimization (meta-evolution, tool friction resolution)", "value": "system_optimization"},
        ],
        "default": "build_fix",
    },
}


def load_patterns_catalog() -> Dict[str, Dict[str, Any]]:
    """Load canonical patterns catalog if present, or return defaults."""
    if PATTERNS_FILE.is_file():
        try:
            data = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {
        "graph": {"pattern": "graph", "next_skill": "graph-planner", "plan_artifact": "docs/plans/work-tasks/<task-id>/<task-id>-graph-manifest.json"},
        "dual-loop": {"pattern": "dual-loop", "next_skill": "dual-loop", "plan_artifact": "handoffs/task_packet_<task-id>.md"},
        "agent-swarm": {"pattern": "agent-swarm", "next_skill": "agent-swarm", "plan_artifact": "docs/plans/work-tasks/<task-id>/<task-id>.job.md"},
        "direct": {"pattern": "direct", "next_skill": None, "plan_artifact": "docs/plans/work-tasks/<task-id>/<task-id>-implementation-plan.md"},
        "red-team-review": {"pattern": "red-team-review", "next_skill": "red-team-review", "plan_artifact": "docs/plans/work-tasks/<task-id>/<task-id>-threat-model.md"},
        "learning-loop": {"pattern": "learning-loop", "next_skill": "learning-loop", "plan_artifact": "docs/plans/work-tasks/<task-id>/<task-id>-eval-brief.md"},
        "triple-loop-learning": {"pattern": "triple-loop-learning", "next_skill": "triple-loop-learning", "plan_artifact": "docs/plans/work-tasks/<task-id>/<task-id>-learning-contract.md"},
    }


def validate_answers(answers: Dict[str, Any]) -> List[str]:
    """Validate that answered dimensions have recognized, legal values."""
    errors = []
    for dim, val in answers.items():
        if dim not in DIMENSION_OPTIONS:
            errors.append(f"Unknown dimension '{dim}'")
            continue
        allowed = DIMENSION_OPTIONS[dim]
        if val not in allowed:
            errors.append(f"Invalid value '{val}' for dimension '{dim}'. Allowed values: {sorted(allowed)}")
    return errors


def decide_strategy(answers: Dict[str, str]) -> Dict[str, Any]:
    """Pure decision table mapping explicit validated answers to an orchestration pattern."""
    missing = [dim for dim in ["unit_structure", "ordering_convergence", "assurance_need", "task_nature"] if dim not in answers]
    if missing:
        next_dim = missing[0]
        q = QUESTIONS[next_dim]
        return {
            "status": "needs_clarification",
            "missing_dimension": next_dim,
            "question": {
                "dimension": next_dim,
                "prompt": q["prompt"],
                "options": q["options"],
                "default": q["default"],
            },
        }

    catalog = load_patterns_catalog()
    unit = answers["unit_structure"]
    order = answers["ordering_convergence"]
    assurance = answers["assurance_need"]
    nature = answers["task_nature"]

    rejected = []
    pattern = "direct"
    rationale = ""

    # Rule 1: Meta-friction / system optimization -> triple-loop-learning
    if nature == "system_optimization":
        pattern = "triple-loop-learning"
        rationale = "Task involves meta-systemic friction analysis and evolutionary optimization."
        rejected.append({"pattern": "graph", "reason": "System optimization operates on friction logs rather than structural node DAGs"})
        rejected.append({"pattern": "dual-loop", "reason": "Requires meta-evolutionary trace feedback, not single-unit dispatch"})

    # Rule 2: Exploratory research / open-ended spikes -> learning-loop
    elif nature == "exploratory_research":
        pattern = "learning-loop"
        rationale = "Task is an open-ended exploratory spike or evaluation survey."
        rejected.append({"pattern": "graph", "reason": "Exploratory research lacks pre-computable deterministic DAG topologies"})
        rejected.append({"pattern": "agent-swarm", "reason": "Research spike is not a collection of identical independent units"})

    # Rule 3: Many identical independent units, no ordering -> agent-swarm
    elif unit == "many_identical" and order == "none":
        pattern = "agent-swarm"
        rationale = "Task comprises many identical, independent units without inter-step dependencies."
        rejected.append({"pattern": "graph", "reason": "Identical independent units execute more efficiently under swarm workers without DAG barrier overhead"})
        rejected.append({"pattern": "dual-loop", "reason": "Dual-loop does not provide concurrent batch worker dispatch across bulk files"})

    # Rule 4: Distinct steps with dependencies or ordering barriers -> graph
    elif unit == "distinct_steps" or order in ("barrier", "ordered_mutations"):
        pattern = "graph"
        rationale = "Task exhibits distinct dependent phases, parallel fan-out join barriers, or ordered mutations."
        rejected.append({"pattern": "agent-swarm", "reason": "Swarm cannot manage join barriers, topological ordering, or dependency graphs"})
        rejected.append({"pattern": "dual-loop", "reason": "Dual-loop cannot orchestrate parallel fan-out reads or multi-step mutation sequences"})

    # Rule 5: One bounded change -> dual-loop
    elif unit == "one_bounded":
        pattern = "dual-loop"
        rationale = "Task is a single bounded feature or bugfix suitable for supervisor-worker execution."
        rejected.append({"pattern": "graph", "reason": "Single bounded change does not justify the ceremony or token overhead of a DAG runner"})
        rejected.append({"pattern": "agent-swarm", "reason": "Single bounded change is not a bulk batch operation"})

    # Rule 6: Minimal direct edit -> direct
    else:
        pattern = "direct"
        rationale = "Task is a minimal localized change executable directly without subagent overhead."
        rejected.append({"pattern": "graph", "reason": "Trivial edit does not require DAG orchestration"})
        rejected.append({"pattern": "dual-loop", "reason": "Trivial edit does not require supervisor-worker separation"})

    pat_info = catalog.get(pattern, {})
    result: Dict[str, Any] = {
        "status": "success",
        "pattern": pattern,
        "rationale": rationale,
        "rejected": rejected,
        "next_skill": pat_info.get("next_skill"),
        "plan_artifact": pat_info.get("plan_artifact"),
        "override_requested": None,
    }

    # Adversarial assurance is a modifier wrapper on the build/fix pattern
    if assurance == "adversarial":
        result["assurance"] = "adversarial"
        result["advisory_wrappers"] = ["red-team-review"]
        result["rationale"] += " Wrapped with adversarial red-team review."

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Strategy Selector for Agent Orchestration")
    parser.add_argument("--answers", help="JSON string or path to JSON file containing dimension answers")
    parser.add_argument("--out", help="Optional output directory for decision record (default: stdout only, no tree pollution)")
    parser.add_argument("--override", help="Caller override pattern (e.g. graph, dual-loop, agent-swarm, direct)")
    parser.add_argument("--override-reason", help="Reason for requested override")
    parser.add_argument("--non-interactive", action="store_true", help="Fail closed if any dimension is missing")

    args = parser.parse_args()

    answers: Dict[str, str] = {}

    # 1. Parse explicit answers
    if args.answers:
        raw_ans = args.answers.strip()
        if raw_ans.startswith("{"):
            try:
                answers.update(json.loads(raw_ans))
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON for --answers: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            ans_path = Path(raw_ans)
            if not ans_path.is_file():
                print(f"Error: Answers file not found: {ans_path}", file=sys.stderr)
                sys.exit(1)
            try:
                answers.update(json.loads(ans_path.read_text(encoding="utf-8")))
            except Exception as e:
                print(f"Error: Failed to read answers file {ans_path}: {e}", file=sys.stderr)
                sys.exit(1)

    # 2. Validate answer values
    val_errors = validate_answers(answers)
    if val_errors:
        for err in val_errors:
            print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    is_non_interactive = args.non_interactive or not sys.stdin.isatty() or bool(args.answers)

    # 3. Evaluate decision
    decision = decide_strategy(answers)

    if decision.get("status") == "needs_clarification":
        if is_non_interactive:
            print(json.dumps(decision, indent=2))
            print(f"Non-interactive mode: missing required answer for '{decision.get('missing_dimension')}'.", file=sys.stderr)
            sys.exit(2)
        else:
            # Interactive question flow
            q = decision["question"]
            dim = q["dimension"]
            print(f"\n{q['prompt']}")
            for opt in q["options"]:
                print(f"  - {opt['label']}")
            print(f"Default: [{q['default']}]")
            val = input(f"Select value ({', '.join([o['value'] for o in q['options']])}) [{q['default']}]: ").strip()
            if not val:
                val = q["default"]
            answers[dim] = val

            # Validate input
            val_errs = validate_answers({dim: val})
            if val_errs:
                for err in val_errs:
                    print(f"Error: {err}", file=sys.stderr)
                sys.exit(1)

            decision = decide_strategy(answers)

    # 4. Handle override if requested
    if args.override:
        if args.override not in VALID_PATTERNS:
            print(f"Error: Invalid override pattern '{args.override}'. Valid patterns: {sorted(VALID_PATTERNS)}", file=sys.stderr)
            sys.exit(1)

        catalog = load_patterns_catalog()
        target_info = catalog.get(args.override, {})
        decision["override_requested"] = {
            "from": decision.get("pattern"),
            "to": args.override,
            "reason": args.override_reason or "Caller requested override",
        }
        decision["pattern"] = args.override
        decision["next_skill"] = target_info.get("next_skill")
        decision["plan_artifact"] = target_info.get("plan_artifact")

    # 5. Output handling: Only write to disk if --out is explicitly provided
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "select-loop-strategy-decision.json"
        out_file.write_text(json.dumps(decision, indent=2), encoding="utf-8")

        md_file = out_dir / "select-loop-strategy-decision.md"
        md_content = (
            f"# Orchestration Strategy Decision\n\n"
            f"- **Pattern**: `{decision.get('pattern')}`\n"
            f"- **Rationale**: {decision.get('rationale')}\n"
            f"- **Next Skill**: `{decision.get('next_skill')}`\n"
            f"- **Plan Artifact**: `{decision.get('plan_artifact')}`\n"
        )
        if decision.get("override_requested"):
            ov = decision["override_requested"]
            md_content += f"- **Requested Override**: From `{ov.get('from')}` to `{ov.get('to')}` ({ov.get('reason')})\n"
        md_file.write_text(md_content, encoding="utf-8")

    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
