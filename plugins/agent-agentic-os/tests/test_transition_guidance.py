"""Task 5 contract tests for advisory, registry-derived transition guidance."""

import io
import pytest
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.coordinator import TransitionCoordinator
from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS
from agent_control import ControlPlane


@pytest.fixture
def control_plane(tmp_path):
    control_plane = ControlPlane(db_path=tmp_path / "control_plane.db")
    control_plane.init_db()
    return control_plane


def test_guidance_derives_legal_next_states_and_exposes_versioned_snapshot(control_plane):
    task_id = "guidance-derived-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")

    guidance = control_plane.get_transition_guidance(task_id)

    assert guidance["advisory"] is True
    assert guidance["registry_version"]
    assert guidance["current_state"] == "INTAKE"
    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS["INTAKE"]
    assert {edge["to_state"] for edge in guidance["transitions"]} == set(ALLOWED_TRANSITIONS["INTAKE"])
    assert all(edge["command"].startswith("python3 ") for edge in guidance["transitions"])
    interview = next(edge for edge in guidance["transitions"] if edge["to_state"] == "INTERVIEW")
    assert any("log-prior-art" in helper for helper in interview["helper_commands"])


def test_guidance_cannot_authorize_illegal_requested_edge(control_plane):
    task_id = "guidance-denial-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")

    guidance = control_plane.get_transition_guidance(task_id, requested_to_state="DONE")

    assert guidance["advisory"] is True
    assert guidance["legal"] is False
    assert guidance["command"] is None
    assert guidance["denial_guidance"]
    assert guidance["recovery_states"] == ALLOWED_TRANSITIONS["INTAKE"]


def test_stale_yaml_next_state_claim_is_ignored_for_guidance_legality(control_plane):
    task_id = "guidance-stale-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")
    registry = TransitionRegistry.load_default()
    control_plane._transition_registry = registry
    registry.get_template("INTAKE", "INTERVIEW").guidance["legal_next_states"] = ["DONE"]

    guidance = control_plane.get_transition_guidance(task_id)

    assert guidance["legal_next_states"] == ALLOWED_TRANSITIONS["INTAKE"]
    assert "DONE" not in guidance["legal_next_states"]


def test_coordinator_surfaces_advisory_guidance_before_and_after_transition(control_plane):
    task_id = "guidance-output-001"
    control_plane.create_task(task_id=task_id, title="Guidance", runtime_tool="codex")
    output = io.StringIO()
    coordinator = TransitionCoordinator(control_plane, output_stream=output)

    coordinator._write_transition_guidance("INTAKE", "INTERVIEW", phase="before")
    coordinator._write_next_steps_hint("INTAKE")

    rendered = output.getvalue()
    assert "Advisory transition guidance" in rendered
    assert "registry version" in rendered
    assert "INTAKE -> INTERVIEW" in rendered
    assert "advisory only" in rendered.lower()
    assert "Next possible transitions from INTAKE" in rendered
