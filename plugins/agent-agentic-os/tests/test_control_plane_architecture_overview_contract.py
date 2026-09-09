"""Contract tests for the durable control-plane architecture overview."""

import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.registry import TransitionRegistry
from control_plane.state_machine import ALLOWED_TRANSITIONS, CANONICAL_STATES


REPO_ROOT = Path(__file__).resolve().parents[3]
OVERVIEW = REPO_ROOT / "plugins/agent-agentic-os/references/control-plane-architecture.md"
TEMPLATES = REPO_ROOT / "plugins/agent-agentic-os/scripts/control_plane/transition_templates.yaml"


def _overview_edges(text: str) -> set[tuple[str, str]]:
    return set(
        re.findall(r"^\|\s*([A-Z_]+)\s*\|\s*([A-Z_]+)\s*\|", text, re.MULTILINE)
    )


def test_overview_exists_and_describes_the_runtime_contract():
    text = OVERVIEW.read_text()
    for marker in (
        "TransitionRegistry",
        "TransitionCoordinator",
        "SQLite",
        "verification_receipts",
        "human provenance",
        "work package",
        "execution step",
        "control-plane-pipeline.mermaid",
        "control-plane-architecture.mermaid",
    ):
        assert marker.lower() in text.lower()


def test_overview_states_match_canonical_state_machine():
    text = OVERVIEW.read_text()
    documented_states = set(re.findall(r"^\|\s*([A-Z_]+)\s*\|", text, re.MULTILINE))
    assert documented_states == set(CANONICAL_STATES)


def test_overview_edges_match_registry_and_templates():
    registry = TransitionRegistry.load_from_file(TEMPLATES)
    text = OVERVIEW.read_text()
    expected_edges = {
        (from_state, to_state)
        for from_state, to_states in ALLOWED_TRANSITIONS.items()
        for to_state in to_states
    }
    assert registry.get_all_edges() == expected_edges
    assert _overview_edges(text) == expected_edges


def test_overview_preserves_advisory_execution_guidance_boundary():
    text = OVERVIEW.read_text().lower()
    assert "advisory" in text
    assert "must not change legal transitions" in text
    assert "objective" in text
    assert "failure/recovery" in text
