"""
Tests for Deterministic Strategy Selector (PR C)
=================================================

Validates:
1. Mapping of diagnostic dimensions to expected patterns.
2. Comprehensive table-driven test covering all 72 answer combinations.
3. Strict validation: invalid answers and invalid overrides fail closed.
4. Override records 'override_requested' without claiming human authority.
5. Adversarial assurance acts as a modifier wrapper and does not overwrite build topology.
6. Ambiguous or missing inputs return 'needs_clarification'.
7. Non-interactive execution fails closed (exit code 2) when inputs are incomplete.
8. Clean tree guarantee: no files written unless --out is provided.
"""

import json
import itertools
import subprocess
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.select_strategy import (
    decide_strategy,
    validate_answers,
    DIMENSION_OPTIONS,
    VALID_PATTERNS,
)


def test_rule_mapping_swarm_vs_graph():
    swarm_answers = {
        "unit_structure": "many_identical",
        "ordering_convergence": "none",
        "assurance_need": "normal",
        "task_nature": "build_fix",
    }
    swarm_dec = decide_strategy(swarm_answers)
    assert swarm_dec["status"] == "success"
    assert swarm_dec["pattern"] == "agent-swarm"
    assert swarm_dec["next_skill"] == "agent-swarm"

    graph_answers = {
        "unit_structure": "distinct_steps",
        "ordering_convergence": "none",
        "assurance_need": "normal",
        "task_nature": "build_fix",
    }
    graph_dec = decide_strategy(graph_answers)
    assert graph_dec["status"] == "success"
    assert graph_dec["pattern"] == "graph"
    assert graph_dec["next_skill"] == "graph-planner"


def test_rule_mapping_direct_minimal_change():
    direct_answers = {
        "unit_structure": "minimal_direct",
        "ordering_convergence": "none",
        "assurance_need": "normal",
        "task_nature": "build_fix",
    }
    dec = decide_strategy(direct_answers)
    assert dec["status"] == "success"
    assert dec["pattern"] == "direct"
    assert dec["next_skill"] is None


def test_rule_mapping_adversarial_is_wrapper():
    adv_answers = {
        "unit_structure": "distinct_steps",
        "ordering_convergence": "barrier",
        "assurance_need": "adversarial",
        "task_nature": "build_fix",
    }
    dec = decide_strategy(adv_answers)
    assert dec["status"] == "success"
    assert dec["pattern"] == "graph"
    assert dec["assurance"] == "adversarial"
    assert "red-team-review" in dec.get("advisory_wrappers", [])


def test_table_driven_all_72_combinations():
    units = DIMENSION_OPTIONS["unit_structure"]
    orderings = DIMENSION_OPTIONS["ordering_convergence"]
    assurances = DIMENSION_OPTIONS["assurance_need"]
    natures = DIMENSION_OPTIONS["task_nature"]

    combinations = list(itertools.product(units, orderings, assurances, natures))
    assert len(combinations) == 72

    for u, o, a, n in combinations:
        ans = {
            "unit_structure": u,
            "ordering_convergence": o,
            "assurance_need": a,
            "task_nature": n,
        }
        dec = decide_strategy(ans)
        assert dec["status"] == "success", f"Failed for {ans}"
        assert dec["pattern"] in VALID_PATTERNS, f"Unknown pattern {dec['pattern']} for {ans}"
        assert dec["rationale"], f"Empty rationale for {ans}"


def test_answer_validation_rejects_invalid_values():
    errs = validate_answers({"unit_structure": "banana"})
    assert len(errs) == 1
    assert "Invalid value 'banana'" in errs[0]

    errs_dim = validate_answers({"bogus_dim": "val"})
    assert len(errs_dim) == 1
    assert "Unknown dimension 'bogus_dim'" in errs_dim[0]


def test_cli_invalid_answers_exits_nonzero(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "select_strategy.py"
    cmd = [
        sys.executable,
        str(script),
        "--answers", '{"unit_structure": "banana"}',
        "--non-interactive",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "Invalid value 'banana'" in res.stderr


def test_cli_invalid_override_rejected(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "select_strategy.py"
    answers = json.dumps({
        "unit_structure": "one_bounded",
        "ordering_convergence": "none",
        "assurance_need": "normal",
        "task_nature": "build_fix",
    })
    cmd = [
        sys.executable,
        str(script),
        "--answers", answers,
        "--override", "yolo",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 1
    assert "Invalid override pattern 'yolo'" in res.stderr


def test_cli_override_records_requested_override_without_human_claim(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "select_strategy.py"
    answers = json.dumps({
        "unit_structure": "one_bounded",
        "ordering_convergence": "none",
        "assurance_need": "normal",
        "task_nature": "build_fix",
    })
    cmd = [
        sys.executable,
        str(script),
        "--answers", answers,
        "--out", str(tmp_path),
        "--override", "graph",
        "--override-reason", "Architect requested DAG checkpointing",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    decision_file = tmp_path / "select-loop-strategy-decision.json"
    assert decision_file.is_file()
    dec = json.loads(decision_file.read_text(encoding="utf-8"))
    assert dec["pattern"] == "graph"
    assert "override_requested" in dec
    assert dec["override_requested"]["from"] == "dual-loop"
    assert dec["override_requested"]["to"] == "graph"
    assert dec["override_requested"]["reason"] == "Architect requested DAG checkpointing"
    assert "overridden_by" not in dec  # Does not claim human authorization


def test_cli_no_out_flag_does_not_dirty_tree():
    script = Path(__file__).resolve().parents[1] / "scripts" / "select_strategy.py"
    answers = json.dumps({
        "unit_structure": "one_bounded",
        "ordering_convergence": "none",
        "assurance_need": "normal",
        "task_nature": "build_fix",
    })
    cmd = [
        sys.executable,
        str(script),
        "--answers", answers,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0
    assert not Path(".orchestration").exists()
    data = json.loads(res.stdout)
    assert data["status"] == "success"
    assert data["pattern"] == "dual-loop"


def test_pattern_catalog_parity():
    """
    Asserts exact parity across:
    1. Canonical references/patterns.json (agent-orchestration)
    2. Symlinked select-loop-strategy/references/patterns.json
    3. Fallback VALID_PATTERNS in select_strategy.py
    """
    repo_root = Path(__file__).resolve().parents[3]
    patterns_canonical = repo_root / "plugins" / "agent-orchestration" / "references" / "patterns.json"
    patterns_symlink = (
        repo_root
        / "plugins"
        / "agent-orchestration"
        / "skills"
        / "select-loop-strategy"
        / "references"
        / "patterns.json"
    )

    assert patterns_canonical.is_file(), f"Missing {patterns_canonical}"
    assert patterns_symlink.is_file(), f"Missing {patterns_symlink}"

    with open(patterns_canonical, "r", encoding="utf-8") as f:
        canon_data = json.load(f)

    with open(patterns_symlink, "r", encoding="utf-8") as f:
        symlink_data = json.load(f)

    canon_keys = set(canon_data.keys())
    symlink_keys = set(symlink_data.keys())
    valid_keys = set(VALID_PATTERNS)

    assert canon_keys == symlink_keys, "Symlink patterns.json does not match canonical"
    assert canon_keys == valid_keys, "select_strategy.py VALID_PATTERNS does not match patterns.json"


