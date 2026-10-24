"""Fast, deterministic tests for the cheap-agent simulation case generator itself
(transition_simulation_cases.py). No model calls here -- this only verifies the
generated data is well-formed and matches the live registry contract. Runs as
part of the normal pytest suite. The actual Haiku-in-the-loop execution driven
by this data is a separate, manually-invoked, opt-in step -- see
plugins/agent-agentic-os/references/cheap-agent-transition-simulation.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from control_plane.registry import TransitionRegistry
from control_plane.transition_simulation_cases import build_simulation_cases, proof_gate_exempt


def test_expected_case_count_per_edge():
    """Non-exempt edges -> 2 cases each (approve/reject). Exempt force_retrospective_*
    edges -> 1 case per declared force_retrospective_reason_category option (2, since
    that question currently declares 2 options). Other exempt edges -> 1 case each."""
    registry = TransitionRegistry.load_default()
    cases = build_simulation_cases(registry)
    expected = 0
    for template in registry.get_all_templates():
        if not proof_gate_exempt(template):
            expected += 2
        elif template.transition_id.startswith("force_retrospective_from_"):
            reason_q = next(
                (q for q in template.human_questions if q["question_id"] == "force_retrospective_reason_category"),
                None,
            )
            expected += len(reason_q["options"]) if reason_q else 1
        else:
            expected += 1
    assert len(cases) == expected


def test_every_case_id_is_unique():
    cases = build_simulation_cases()
    ids = [c.case_id for c in cases]
    assert len(ids) == len(set(ids))


def test_non_exempt_cases_expect_guidance_confirmation_question():
    cases = build_simulation_cases()
    for case in cases:
        if not case.is_guidance_gate_exempt:
            assert "guidance_compliance_confirmation" in case.expected_question_ids
            assert case.expected_guidance_confirmation_answer in ("YES", "NO")


def test_exempt_cases_are_cryptographic_proof_edges_only():
    registry = TransitionRegistry.load_default()
    cases = build_simulation_cases(registry)
    for case in cases:
        if case.is_guidance_gate_exempt:
            assert (case.from_state, case.to_state) in registry.proof_required_edges()
            assert proof_gate_exempt(registry.get_template(case.from_state, case.to_state))


def test_approve_and_reject_conditions_both_present_for_every_non_exempt_edge():
    """force_retrospective_from_* edges are non-exempt but use VALID_REASON:: conditions
    instead of HUMAN_APPROVES/HUMAN_REJECTS (their own reason-category branch point,
    not a rejection scenario) -- excluded here, not a gap in this check."""
    cases = build_simulation_cases()
    non_exempt_edges = {
        (c.from_state, c.to_state) for c in cases
        if not c.is_guidance_gate_exempt and not c.condition.startswith("VALID_REASON::")
    }
    for from_state, to_state in non_exempt_edges:
        conditions = {
            c.condition for c in cases
            if c.from_state == from_state and c.to_state == to_state
        }
        assert conditions == {"HUMAN_APPROVES", "HUMAN_REJECTS"}


def test_human_only_edges_returns_only_human_only_classified_edges():
    """T5: human_only_edges() must return exactly the edges the registry itself
    classifies human_only (mirrors control_plane.constants.AUTHORIZED_ACTOR_HUMAN_ONLY),
    never a hand-maintained parallel list that could drift from the real derivation."""
    from control_plane.transition_simulation_cases import human_only_edges
    from control_plane.constants import AUTHORIZED_ACTOR_HUMAN_ONLY

    registry = TransitionRegistry.load_default()
    edges = human_only_edges(registry)
    assert len(edges) > 0
    assert ("AWAITING_APPROVAL", "APPROVED") in edges
    assert ("INTAKE", "INTERVIEW") not in edges
    for from_state, to_state in edges:
        template = registry.get_template(from_state, to_state)
        assert template.authorized_actor == AUTHORIZED_ACTOR_HUMAN_ONLY


def test_agent_spoof_adversarial_cases_cover_every_human_only_edge():
    """T5: the adversarial matrix must have exactly one case per human_only edge,
    so every consequential edge gets a spoofed-actor regression case."""
    from control_plane.transition_simulation_cases import (
        build_agent_spoof_adversarial_cases, human_only_edges,
    )

    registry = TransitionRegistry.load_default()
    cases = build_agent_spoof_adversarial_cases(registry)
    edges = human_only_edges(registry)
    assert len(cases) == len(edges)
    case_edges = {(c.from_state, c.to_state) for c in cases}
    assert case_edges == set(edges)
    assert all(c.condition == "AGENT_SPOOF_DENIED" for c in cases)
