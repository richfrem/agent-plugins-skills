"""Regression tests for human-friendly transition answer canonicalization."""

import pytest
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.coordinator import TransitionCoordinatorError, _canonicalize_declared_answer


def test_shorthand_human_answer_resolves_to_registered_yaml_option():
    options = ["Proceed with review [Recommended]", "Continue revising prior stage"]

    assert _canonicalize_declared_answer("Proceed with review", options) == options[0]


def test_answer_matching_is_case_and_whitespace_tolerant():
    options = ["Proceed with review [Recommended]", "Continue revising prior stage"]

    assert _canonicalize_declared_answer("  proceed WITH review  ", options) == options[0]


def test_ambiguous_normalized_answers_fail_closed():
    options = ["Proceed [Recommended]", "Proceed"]

    with pytest.raises(TransitionCoordinatorError, match="ambiguous"):
        _canonicalize_declared_answer("Proceed", options)
