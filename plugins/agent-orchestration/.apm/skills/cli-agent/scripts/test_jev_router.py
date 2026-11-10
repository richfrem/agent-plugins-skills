"""test_jev_router.py - Unit tests for JEV Router in cli-agent."""

from __future__ import annotations

import os
import sys
import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from jev_router import JEVRouter, RoutingDecision


@pytest.fixture
def router() -> JEVRouter:
    r = JEVRouter()
    r.route_task("warmup intent check")
    return r


def test_jev_router_zero_tokens(router: JEVRouter) -> None:
    decision = router.route_task("Format markdown table columns in README.md")
    assert decision.tokens_consumed == 0
    assert decision.tier == "TIER_1_MICRO"
    assert decision.recommended_runtime == "openrouter"
    assert decision.complexity_class == "MECHANICAL_CHORE"


def test_jev_router_latency(router: JEVRouter) -> None:
    durations = []
    for _ in range(50):
        d = router.route_task("Fix trailing comma in JSON manifest")
        durations.append(d.latency_ms)
    sorted_durations = sorted(durations)
    median_lat = sorted_durations[len(durations) // 2]
    trimmed = sorted_durations[5:45]
    trimmed_mean = sum(trimmed) / len(trimmed)
    assert median_lat < 3.0, f"Expected <3ms median latency, got {median_lat:.3f}ms"
    assert trimmed_mean < 3.0, f"Expected <3ms trimmed mean latency, got {trimmed_mean:.3f}ms"


def test_jev_router_epistemic_firewall(router: JEVRouter) -> None:
    tasks = [
        "Derive mathematical proof that non-generative JEPAs converge to Platonic manifold",
        "Design orthogonal Procrustes alignment algorithm across embedding spaces",
        "Resolve constitutional conflict between Protocol 128 and Protocol 78",
        "Formulate Popperian research mission for anti-Asch sycophancy resistance",
    ]
    for t in tasks:
        d = router.route_task(t)
        assert d.tier == "TIER_3_FRONTIER", f"Task '{t}' failed epistemic firewall: got {d.tier}"
        assert d.complexity_class == "EPISTEMIC_ARCHITECTURAL"


def test_jev_router_routine_chores(router: JEVRouter) -> None:
    tasks = [
        ("Format markdown table in document", "MECHANICAL_CHORE", "openrouter", "meta-llama/llama-3.2-3b-instruct"),
        ("Write pytest unit test verifying sha256 hash", "CODING_SYNTAX", "openrouter", "qwen/qwen3-coder-30b-a3b-instruct"),
        ("Scan commit messages and categorize feat vs fix", "GENERAL_TRIAGE", "openrouter", "meta-llama/llama-3.2-1b-instruct"),
    ]
    for desc, expected_comp, expected_runtime, expected_model in tasks:
        d = router.route_task(desc)
        assert d.tier == "TIER_1_MICRO"
        assert d.complexity_class == expected_comp
        assert d.recommended_runtime == expected_runtime
        assert d.recommended_model == expected_model


def test_jev_router_offline_fallback(router: JEVRouter) -> None:
    d = router.route_task("Format markdown table", offline=True)
    assert d.tier == "TIER_2_LOCAL"
    assert d.recommended_runtime == "llama"
    assert d.recommended_model == "local-server"
    assert d.offline_fallback is True
