"""Contract tests for project-setup's reusable capability baseline."""

from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "skills" / "project-setup" / "SKILL.md"


def test_project_setup_establishes_one_reusable_capability_baseline():
    text = SKILL.read_text(encoding="utf-8")

    required_markers = (
        "Capability Baseline (once per project setup)",
        "context/agent-capability-profile.json",
        "context/memory/environment.md",
        "update-cli-models",
        "does not duplicate model catalog policy",
        "Do not repeat deep environment or model analysis",
        "later plan and implementation review gates",
        "ask the user to choose or confirm",
    )
    for marker in required_markers:
        assert marker.lower() in text.lower()


def test_project_setup_preserves_explicit_authorization_boundary_for_reviews():
    text = SKILL.read_text(encoding="utf-8")

    assert "does not authorize reviewer dispatch" in text
    assert "Do not dispatch an internal reviewer" in text


def test_project_setup_asks_one_at_a_time_and_persists_provider_inventory():
    text = SKILL.read_text(encoding="utf-8").lower()

    assert "one question at a time" in text
    assert "codex" in text and "agy" in text and "claude" in text
    assert "copilot" in text and "local llm" in text
    assert "available: yes/no" in text
    assert "active subscription" in text
    assert "project authorization" in text
    assert "work-account" in text
    assert "installed alone never counts" in text
    assert "user-confirmed provider inventory" in text
    assert "context/agent-capability-profile.json" in text
    assert "context/memory/environment.md" in text


def test_project_setup_defines_setup_only_depth_and_pipeline_read_only_handoff():
    text = SKILL.read_text(encoding="utf-8").lower()

    assert "deep analysis belongs in project setup" in text
    assert "pipeline stages must read" in text
    assert "if the profile is missing or stale, route back to project setup" in text
    assert "never store credentials" in text
