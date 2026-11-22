"""Selector rule and planning hints: a serial chain is not a graph (graph-planning principles)."""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.select_strategy import OVERRIDE_TO_GRAPH_HINT, SERIAL_CHAIN_HINT, decide_strategy

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "select_strategy.py"


def _answers(unit, order, assurance="normal"):
    return {"unit_structure": unit, "ordering_convergence": order, "assurance_need": assurance}


def test_join_barrier_selects_graph():
    dec = decide_strategy(_answers("distinct_steps", "barrier"))
    assert dec["pattern"] == "graph"
    assert dec["planning_hints"] == []


def test_serial_chain_of_distinct_steps_selects_dual_loop_with_hint():
    dec = decide_strategy(_answers("distinct_steps", "ordered_mutations"))
    assert dec["pattern"] == "dual-loop"
    assert SERIAL_CHAIN_HINT in dec["planning_hints"]
    assert "graph" in [r["pattern"] for r in dec["rejected"]]


def test_distinct_steps_without_ordering_or_barrier_is_not_a_graph():
    dec = decide_strategy(_answers("distinct_steps", "none"))
    assert dec["pattern"] == "dual-loop"


def test_ordered_mutations_on_bounded_change_stay_dual_loop():
    dec = decide_strategy(_answers("one_bounded", "ordered_mutations"))
    assert dec["pattern"] == "dual-loop"
    assert SERIAL_CHAIN_HINT in dec["planning_hints"]


def test_minimal_direct_edit_stays_direct_even_with_ordering():
    assert decide_strategy(_answers("minimal_direct", "ordered_mutations"))["pattern"] == "direct"


def test_many_identical_units_still_select_swarm():
    assert decide_strategy(_answers("many_identical", "none"))["pattern"] == "agent-swarm"


def test_adversarial_assurance_does_not_change_topology():
    dec = decide_strategy(_answers("distinct_steps", "ordered_mutations", "adversarial"))
    assert dec["pattern"] == "dual-loop"
    assert "red-team-review" in dec["advisory_wrappers"]


def test_planning_hints_key_is_always_present():
    for unit in ("minimal_direct", "one_bounded", "distinct_steps", "many_identical"):
        for order in ("none", "barrier", "ordered_mutations"):
            assert isinstance(decide_strategy(_answers(unit, order))["planning_hints"], list)


def _run(*extra):
    answers = json.dumps(_answers("distinct_steps", "ordered_mutations"))
    out = subprocess.run([sys.executable, str(SCRIPT), "--answers", answers, "--non-interactive", *extra],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_override_to_graph_on_a_serial_chain_adds_hint_and_rewrites_rationale():
    dec = _run("--override", "graph", "--override-reason", "human wants a graph")
    assert dec["pattern"] == "graph"
    assert OVERRIDE_TO_GRAPH_HINT in dec["planning_hints"]
    assert dec["rationale"].startswith("Caller override from dual-loop to graph")
    assert dec["next_step"] == "graph-planning"


def test_override_keeps_next_step_of_the_chosen_pattern():
    dec = _run("--override", "direct", "--override-reason", "tiny")
    assert dec["pattern"] == "direct"
    assert dec["next_step"] is None
    assert OVERRIDE_TO_GRAPH_HINT not in dec["planning_hints"]
