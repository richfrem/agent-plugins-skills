"""T5: pure-formatting unit tests for run_transition_simulation.py's
actor-classification/denial-reason display. The rest of that script drives
real `claude` CLI subprocess calls and is intentionally excluded from the
normal pytest suite (LLM calls cost real time/money) -- see the module's own
docstring. Only the new pure formatter is unit-tested here."""

import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent.parent / "scripts")
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.run_transition_simulation import format_actor_classification_line
from control_plane.transition_simulation_cases import SimulationCase
from control_plane.registry import TransitionRegistry


def test_routine_edge_shows_agent_or_human_without_denial_reason():
    registry = TransitionRegistry.load_default()
    template = registry.get_template("INTAKE", "INTERVIEW")
    case = SimulationCase(
        from_state="INTAKE", to_state="INTERVIEW", transition_id=template.transition_id,
        condition="HUMAN_APPROVES",
    )
    line = format_actor_classification_line(case, template)
    assert "agent_or_human" in line
    assert "DENIED" not in line


def test_adversarial_case_on_human_only_edge_shows_denial_reason():
    registry = TransitionRegistry.load_default()
    template = registry.get_template("AWAITING_APPROVAL", "APPROVED")
    case = SimulationCase(
        from_state="AWAITING_APPROVAL", to_state="APPROVED", transition_id=template.transition_id,
        condition="AGENT_SPOOF_DENIED",
    )
    line = format_actor_classification_line(case, template)
    assert "human_only" in line
    assert "DENIED" in line
