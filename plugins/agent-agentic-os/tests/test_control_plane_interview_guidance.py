"""P01 behavioral contracts for bounded intake, consent, and user-facing guidance."""

import sys
from pathlib import Path

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from interview_spec_engine import (
    prepare_source_assisted_answers,
    review_round_budget,
    summarize_precompletion_gate,
)


TEMPLATES = SCRIPTS_DIR / "control_plane" / "transition_templates.yaml"


def test_authorized_source_answers_are_candidates_not_approval_or_confirmation():
    result = prepare_source_assisted_answers(
        ["scope", "approval"],
        [{
            "path": "docs/brief.md",
            "authorized": True,
            "complete": True,
            "stale": False,
            "answers": {"scope": "P0 only", "approval": "approved"},
        }],
        approval_question_ids={"approval"},
    )

    assert result["candidates"]["scope"]["answer"] == "P0 only"
    assert result["candidates"]["scope"]["requires_human_confirmation"] is True
    assert "approval" not in result["candidates"]
    assert result["unresolved"] == ["approval"]
    assert result["rejected_authority"]["approval"] == "document_cannot_grant_approval"


def test_conflicting_or_unauthorized_sources_do_not_answer_for_user_and_confirmed_answers_resume():
    result = prepare_source_assisted_answers(
        ["scope", "verification", "decision"],
        [
            {"path": "docs/a.md", "authorized": True, "complete": True, "stale": False,
             "answers": {"scope": "one", "verification": "tests"}},
            {"path": "docs/b.md", "authorized": True, "complete": True, "stale": True,
             "answers": {"scope": "two"}},
            {"path": "docs/untrusted.md", "authorized": False, "complete": True, "stale": False,
             "answers": {"decision": "yes"}},
        ],
        confirmed_answers={"verification": "tests"},
    )

    assert "scope" in result["conflicts"]
    assert "scope" in result["unresolved"]
    assert "verification" not in result["unresolved"]
    assert result["confirmed_answers"] == {"verification": "tests"}
    assert result["ignored_sources"] == ["docs/untrusted.md"]
    assert "decision" in result["unresolved"]


def test_review_budget_is_shared_per_round_and_timeout_is_partial():
    budget = review_round_budget("STANDARD", elapsed_minutes=15.1, reviewer_count=3)

    assert budget["ceiling_minutes"] == 15
    assert budget["scope"] == "whole_round"
    assert budget["reviewer_count"] == 3
    assert budget["status"] == "partial_timeout"


def test_precompletion_summary_translates_machine_gate_for_user():
    summary = summarize_precompletion_gate({
        "capability_check": True,
        "existing_capability_failed_or_bypassed": True,
        "repeatable_process_assumption": False,
        "next_agent_friction_found": True,
    })

    assert summary["machine_gate"]["MAP_DEBT"] is True
    assert "user_summary" in summary
    assert "not a request for you to do anything now" in summary["user_summary"].lower()
    assert "map debt" in summary["user_summary"].lower()


def test_yaml_declares_source_confirmation_model_guidance_and_review_ceilings():
    config = yaml.safe_load(TEMPLATES.read_text(encoding="utf-8"))
    intake = config["intake_guidance"]

    assert intake["source_documents"]["authorization_required"] is True
    assert intake["source_documents"]["inferred_answers_require_confirmation"] is True
    assert intake["source_documents"]["documents_cannot_grant_approval"] is True
    assert intake["review_rounds"]["ceilings_minutes"] == {"QUICK": 5, "STANDARD": 15, "SIGNIFICANT": 30}
    assert intake["review_rounds"]["shared_whole_round_budget"] is True
    assert config["model_effort_guidance"]["interview"]["recommended_effort"] == "low"
