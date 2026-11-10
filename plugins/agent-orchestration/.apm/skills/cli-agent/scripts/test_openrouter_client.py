"""test_openrouter_client.py - Unit tests for the cli-agent OpenRouter micro-tier client.

No network calls: fallbacks are monkeypatched and the ledger lives in tmp_path.
"""

from __future__ import annotations

import json
import os
import sys

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import openrouter_client as oc  # noqa: E402


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    path = tmp_path / "spend.json"
    monkeypatch.setenv("OPENROUTER_SPEND_LEDGER", str(path))
    monkeypatch.delenv("OPENROUTER_MONTHLY_CAP_USD", raising=False)
    return path


@pytest.fixture
def no_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(oc, "get_api_key", lambda: None)


def test_default_cap_is_ten_dollars(ledger):
    assert oc.monthly_hard_cap_usd() == 10.00


def test_cap_env_override(ledger, monkeypatch):
    monkeypatch.setenv("OPENROUTER_MONTHLY_CAP_USD", "2.5")
    assert oc.monthly_hard_cap_usd() == 2.5


def test_prohibited_auto_routers_rejected(ledger):
    for model in ("openrouter/free", "openrouter/auto"):
        with pytest.raises(ValueError, match="Prohibited model"):
            oc.invoke_micro_tier("hello", model=model)


def test_pricing_comes_from_live_audited_catalog():
    catalog = oc.load_pricing_catalog()
    assert "meta-llama/llama-3.2-1b-instruct" in catalog
    rates = catalog["meta-llama/llama-3.2-1b-instruct"]
    cost = oc.calculate_cost("meta-llama/llama-3.2-1b-instruct", 1000, 100, catalog)
    expected = (1000 / 1e6) * rates["prompt"] + (100 / 1e6) * rates["completion"]
    assert abs(cost - expected) < 1e-12


def test_unknown_model_uses_conservative_fallback_rate():
    cost = oc.calculate_cost("vendor/not-in-catalog", 1_000_000, 1_000_000, {})
    assert cost == pytest.approx(oc.FALLBACK_RATE["prompt"] + oc.FALLBACK_RATE["completion"])


def test_record_spend_accumulates(ledger):
    assert oc.get_cumulative_spend() == 0.0
    oc.record_spend(0.001)
    oc.record_spend(0.002)
    assert oc.get_cumulative_spend() == pytest.approx(0.003)
    data = json.loads(ledger.read_text())
    assert data["hard_cap_usd"] == 10.00


def test_cap_reached_diverts_to_local(ledger, monkeypatch):
    oc.record_spend(10.0)
    called = {}

    def fake_local(prompt, max_tokens=512):
        called["prompt"] = prompt
        return oc.MicroTierResponse(prompt, "local-server", 1, 1, 0.0, 0.0, True, "OK_LOCAL")

    monkeypatch.setattr(oc, "call_local_llm", fake_local)
    res = oc.invoke_micro_tier("format this")
    assert res.fallback_triggered is True and called["prompt"] == "format this"


def test_cap_reached_without_fallback_raises(ledger):
    oc.record_spend(10.0)
    with pytest.raises(RuntimeError, match="budget exceeded"):
        oc.invoke_micro_tier("x", allow_local_fallback=False)


def test_missing_key_diverts_to_local(ledger, no_key, monkeypatch):
    monkeypatch.setattr(
        oc, "call_local_llm",
        lambda prompt, max_tokens=512: oc.MicroTierResponse("ok", "local-server", 1, 1, 0.0, 0.0, True, "OK_LOCAL"),
    )
    res = oc.invoke_micro_tier("x")
    assert res.status == "OK_LOCAL" and res.cost_usd == 0.0


def test_missing_key_without_fallback_raises(ledger, no_key):
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        oc.invoke_micro_tier("x", allow_local_fallback=False)


def test_local_fallback_failure_is_reported_not_raised(ledger, monkeypatch):
    monkeypatch.setenv("LOCAL_LLM_URL", "http://127.0.0.1:9/v1/chat/completions")
    res = oc.call_local_llm("x")
    assert res.status.startswith("FAILED") and res.fallback_triggered is True
