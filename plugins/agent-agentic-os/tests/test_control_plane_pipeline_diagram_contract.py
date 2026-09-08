"""Task 7 contract tests for pipeline diagrams and user-facing skill guidance."""

import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.state_machine import ALLOWED_TRANSITIONS


REPO_ROOT = Path(__file__).resolve().parents[3]
DIAGRAM_DIR = REPO_ROOT / "docs" / "diagrams"


def _edges(path: Path) -> set[tuple[str, str]]:
    return set(re.findall(r"^\s*([A-Z_]+)\s*-->\s*([A-Z_]+)", path.read_text(), re.MULTILINE))


def test_full_pipeline_diagram_matches_canonical_edges():
    expected = {
        (from_state, to_state)
        for from_state, to_states in ALLOWED_TRANSITIONS.items()
        for to_state in to_states
    }
    assert _edges(DIAGRAM_DIR / "control-plane-pipeline.mermaid") == expected


def test_happy_path_diagram_is_a_valid_subset_with_required_closeout_path():
    expected = {
        (from_state, to_state)
        for from_state, to_states in ALLOWED_TRANSITIONS.items()
        for to_state in to_states
    }
    happy_path = DIAGRAM_DIR / "control-plane-pipeline-happy-path.mermaid"
    assert _edges(happy_path) <= expected
    text = happy_path.read_text()
    for marker in ("INTERVIEW", "DRAFT_PLAN", "RETROSPECTIVE", "DONE"):
        assert marker in text


def test_architecture_diagram_names_governed_delegation_and_advisory_guidance():
    text = (DIAGRAM_DIR / "control-plane-architecture.mermaid").read_text()
    for marker in ("DelegationContract", "Transition guidance", "advisory", "verification_receipts"):
        assert marker.lower() in text.lower()


def test_runtime_skills_expose_final_dispatch_contracts():
    interview = (REPO_ROOT / "plugins/agent-agentic-os/skills/interview-spec/SKILL.md").read_text()
    for marker in ("transition-guidance", "advisory", "SQLite"):
        assert marker.lower() in interview.lower()

    for skill_name in ("copilot-cli-agent", "claude-cli-agent"):
        skill = (REPO_ROOT / f"plugins/cli-agents/skills/{skill_name}/SKILL.md").read_text()
        for marker in ("--require-input", "---SOURCE---", "record-critic-review", "REVISE"):
            assert marker in skill
