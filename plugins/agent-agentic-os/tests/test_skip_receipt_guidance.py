"""
tests/test_skip_receipt_guidance.py
===================================

Purpose:
    Failing-first tests for T16 (auth-ciba-increment-b, issue #639): guidance must never let an agent
    record a review-skip decision on the human's behalf (incident 2026-09-19, receipt 158).
    The PLAN_REVIEW and PLAN_REVIEW->AWAITING_APPROVAL hints, and work-intake SKILL.md, must say the
    human records the skip through the interactive command and that the agent never runs
    `record-review-skip` from a chat message.

Key Input Dependencies:
    - scripts/control_plane/transition_templates.yaml
    - skills/work-intake/SKILL.md

Key Functions (test cases):
    - test_plan_review_hints_name_the_human_as_skip_recorder
    - test_work_intake_skill_has_the_hard_rule
    - test_no_hint_tells_the_agent_to_record_a_skip_itself
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YAML = (ROOT / "scripts/control_plane/transition_templates.yaml").read_text()
SKILL = (ROOT / "skills/work-intake/SKILL.md").read_text()


def _hint_lines():
    return [l for l in YAML.splitlines() if "next_steps_hint" in l]


def test_plan_review_hints_name_the_human_as_skip_recorder():
    hints = [h for h in _hint_lines() if "record-review-skip" in h or "explicit skip receipt" in h]
    assert hints
    for h in hints:
        assert "human" in h.lower() and "--interactive" in h, h[:120]


def test_no_hint_tells_the_agent_to_record_a_skip_itself():
    for h in _hint_lines():
        assert not re.search(r"(?<!human )(?<!the human )record an intentional skip with record-review-skip", h), h[:120]
        assert "If No, record the explicit skip receipt and" not in h


def test_work_intake_skill_has_the_hard_rule():
    assert "never record a review skip" in SKILL.lower() or "never run `record-review-skip`" in SKILL.lower()
    assert "on the human's behalf" in SKILL.lower()


def _review_hints():
    return [l for l in _hint_lines() if "review-selection-v1" in l]


def test_review_hints_tell_the_agent_to_reread_recorded_decisions():
    hints = _review_hints()
    assert len(hints) == 2
    for h in hints:
        assert "inspect-decisions" in h, h[:120]


def test_review_hints_have_a_missing_profile_fallback():
    for h in _review_hints():
        assert "context/agent-capability-profile.json" in h and "missing" in h.lower() and "do not assume" in h.lower(), h[:120]


def test_review_hints_say_the_human_types_runtime_model_effort():
    for h in _review_hints():
        assert "the human types" in h.lower(), h[:120]


def test_review_hints_point_at_list_review_options():
    for h in _review_hints():
        assert "list-review-options" in h, h[:120]
