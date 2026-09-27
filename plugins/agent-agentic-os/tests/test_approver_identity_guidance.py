#!/usr/bin/env python
"""
test_approver_identity_guidance.py
==================================

Purpose:
    Contract tests for the approver-identity rule: each pipeline has exactly one
    approver; the default is the human operator's signing identity for all main
    work, and only simulation work (signed off by the human) may use the agent's
    test identity. The rule must reach agents through the INTERVIEW stage
    contract (surfaced by transition-guidance) and as the first work-intake rule.

Key Input Dependencies:
    plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml — stages.INTERVIEW.approver_identity
    plugins/agent-agentic-os/skills/work-intake/SKILL.md — Critical Operational Rule 1
    plugins/agent-agentic-os/skills/transition-simulator/SKILL.md — simulation approver section

Layer: Development / Testing

Functions:
    - test_interview_contract_declares_single_human_default_approver
    - test_work_intake_confirms_approver_identity_first
    - test_transition_simulator_documents_simulation_approver
    - test_guidance_describes_the_two_database_split

Usage:
    python -m pytest plugins/agent-agentic-os/tests/test_approver_identity_guidance.py
"""

from pathlib import Path

from control_plane.registry import TransitionRegistry

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def test_interview_contract_declares_single_human_default_approver():
    contract = TransitionRegistry.load_default().get_stage_contract("INTERVIEW")
    approver = contract["approver_identity"]
    assert approver["one_approver_per_pipeline"] is True
    assert approver["default"] == "human_operator"
    assert "simulation" in approver["agent_simulation"].lower()
    assert "test-human@local" in approver["agent_simulation"]


def test_work_intake_confirms_approver_identity_first():
    text = (PLUGIN_ROOT / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8")
    rules = text.split("## Critical Operational Rules", 1)[1]
    first_rule = next(line for line in rules.splitlines() if line.startswith("1. "))
    assert "Approver Identity" in first_rule
    assert "simulation" in first_rule.lower()


def test_transition_simulator_documents_simulation_approver():
    text = (PLUGIN_ROOT / "skills" / "transition-simulator" / "SKILL.md").read_text(encoding="utf-8")
    assert "## Approver Identity in Simulations" in text
    assert "test-human@local" in text


def test_guidance_describes_the_two_database_split():
    """The rule is enforced by database (approver_policy.py): every guidance surface must say that
    simulations run in the separate simulation_control_plane.db and must not point agents at the
    removed in-database designation command."""
    contract = TransitionRegistry.load_default().get_stage_contract("INTERVIEW")["approver_identity"]
    surfaces = {
        "yaml": " ".join(str(v) for v in contract.values()),
        "work-intake": (PLUGIN_ROOT / "skills" / "work-intake" / "SKILL.md").read_text(encoding="utf-8"),
        "transition-simulator": (PLUGIN_ROOT / "skills" / "transition-simulator" / "SKILL.md").read_text(encoding="utf-8"),
    }
    for name, text in surfaces.items():
        assert "simulation_control_plane.db" in text, name
        assert "designate-simulation" not in text, name
