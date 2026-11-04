"""Tests for the shared versioned runtime/model catalog contract."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import pytest

from model_catalog import CatalogContractError, load_catalog, select_model, validate_catalog


REFERENCE_DIR = Path(__file__).resolve().parent.parent / "references"
CATALOG_NAMES = ("copilot", "agy", "claude", "codex")


def test_all_runtime_catalogs_have_versioned_capability_contract():
    for runtime_id in CATALOG_NAMES:
        catalog = load_catalog(REFERENCE_DIR / f"{runtime_id}-models.json")
        assert catalog["_meta"]["schema_version"] == 2
        assert catalog["runtime"]["runtime_id"] == runtime_id
        assert catalog["runtime"]["availability"] in {"available", "limited", "unknown"}
        assert set(catalog["runtime"]["native_capabilities"]) >= {
            "planning",
            "worktree",
            "subagents",
        }
        assert set(catalog["capability_tiers"]) == {"low", "medium", "high"}
        assert validate_catalog(catalog) == []


def test_agy_defaults_use_current_flash_38_low_runtime_identifier():
    catalog = load_catalog(REFERENCE_DIR / "agy-models.json")
    agy_models = {model["cli_id"] for model in catalog["models"]}

    assert "gemini-3.8-flash-low" in agy_models
    assert catalog["strategy"]["heartbeat"] == "gemini-3.8-flash"
    assert catalog["strategy"]["default"] == "gemini-3.8-flash"
    assert "gemini-3.5-flash-low" not in agy_models
    flash_low = next(model for model in catalog["models"] if model["cli_id"] == "gemini-3.8-flash-low")
    assert flash_low["context_window_k"] == 1024
    assert flash_low["max_output_k"] == 64
    assert flash_low["pricing_usd_per_1m"]["input"] == 0.75
    assert flash_low["pricing_usd_per_1m"]["output"] == 3.75


def test_codex_catalog_tracks_current_openai_frontier_and_budget_choices():
    catalog = load_catalog(REFERENCE_DIR / "codex-models.json")
    model_ids = {model["cli_id"] for model in catalog["models"]}
    assert {"gpt-6-astra", "gpt-6.1-terra", "gpt-6-luna", "gpt-5.6-terra", "gpt-5.6-luna"} <= model_ids
    assert catalog["strategy"]["heartbeat"] == "gpt-6-luna"
    assert catalog["strategy"]["default"] == "gpt-6-luna"
    assert "gpt-6-luna" in catalog["capability_tiers"]["low"]
    assert "gpt-6.1-terra" in catalog["capability_tiers"]["medium"]
    assert "gpt-6-astra" in catalog["capability_tiers"]["high"]


def test_codex_catalog_matches_current_interactive_model_picker():
    catalog = load_catalog(REFERENCE_DIR / "codex-models.json")
    # Installed Codex CLI picker cache (2026-11-04): gpt-6.1-sol, gpt-6-astra, gpt-6.1-terra, gpt-6-sol, gpt-6-luna, gpt-5.6-*.
    valid_ids = {"gpt-6-astra", "gpt-6.1-sol", "gpt-5.6-sol", "gpt-6.1-terra", "gpt-6-luna"}
    offered_ids = {
        model_id
        for tier in catalog["capability_tiers"].values()
        for model_id in tier
    }

    assert offered_ids == valid_ids
    assert catalog["strategy"]["code_analysis"] == "gpt-6.1-terra"
    assert select_model(catalog, "low") == "gpt-6-luna"


def test_claude_catalog_tracks_current_frontier_choices():
    catalog = load_catalog(REFERENCE_DIR / "claude-models.json")
    model_ids = {model["cli_id"] for model in catalog["models"]}
    assert {"claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5",
            "claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5"} <= model_ids
    assert catalog["strategy"]["highest_capability"] == "claude-fable-5-1"
    assert catalog["strategy"]["agentic_coding"] == "claude-opus-5-5"
    assert catalog["strategy"]["heartbeat"] == "claude-haiku-5-5"
    assert catalog["strategy"]["default"] == "claude-sonnet-5-5"


def test_claude_55_prices_match_official_page_and_a_real_session_cost():
    catalog = load_catalog(REFERENCE_DIR / "claude-models.json")
    price = {m["cli_id"]: m["pricing_usd_per_1m"] for m in catalog["models"]}
    assert price["claude-sonnet-5-5"] == {"input": 2.0, "cached_input": 0.1, "cache_write": 2.5, "cache_write_1h": 4.0, "output": 10.0}
    assert price["claude-opus-5-5"]["output"] == 20.0 and price["claude-haiku-5-5"]["output"] == 0.5
    # Real Claude Code session on claude-sonnet-5-5 reported $29.55 for 4.0k input, 592.9k output, 175.5M cache read, 1.5M cache write (1h TTL).
    p = price["claude-sonnet-5-5"]
    cost = 4.0e3 / 1e6 * p["input"] + 592.9e3 / 1e6 * p["output"] + 175.5e6 / 1e6 * p["cached_input"] + 1.5e6 / 1e6 * p["cache_write_1h"]
    assert abs(cost - 29.55) / 29.55 < 0.01


def test_copilot_catalog_tracks_current_supported_choices():
    catalog = load_catalog(REFERENCE_DIR / "copilot-models.json")
    model_ids = {model["cli_id"] for model in catalog["models"]}
    assert {"claude-fable-5.1", "claude-opus-5", "mai-code-1.1-flash", "kimi-k3", "grok-4.6"} <= model_ids
    assert "gemini-3.8-flash" in model_ids
    assert catalog["strategy"]["complex_reasoning"] == "claude-opus-5"
    assert catalog["strategy"]["critical_only"] == "gpt-6-astra"
    assert "claude-opus-5" in catalog["capability_tiers"]["high"]


def test_claude_catalog_matches_current_interactive_model_picker():
    catalog = load_catalog(REFERENCE_DIR / "claude-models.json")
    offered_ids = {
        model_id
        for tier in catalog["capability_tiers"].values()
        for model_id in tier
    }

    assert offered_ids == {"claude-sonnet-5-5", "claude-fable-5-1", "claude-opus-5-5", "claude-haiku-5-5"}
    assert select_model(catalog, "medium") == "claude-sonnet-5-5"


def test_agy_catalog_matches_current_interactive_model_picker():
    catalog = load_catalog(REFERENCE_DIR / "agy-models.json")
    offered_ids = {
        model_id
        for tier in catalog["capability_tiers"].values()
        for model_id in tier
    }

    # Live `agy models` picker (2026-11-04): Gemini 4 Argon, Gemini 3.8 Flash, Claude Opus/Sonnet 5.5, GPT-OSS 120B.
    assert offered_ids == {
        "gemini-3.8-flash",
        "gemini-4-argon-medium",
        "gemini-4-argon-high",
        "gpt-oss-120b",
        "claude-sonnet-5-5-high",
        "claude-opus-5-5-high",
    }
    assert [select_model(catalog, tier) for tier in ("low", "medium", "high")] == ["gemini-3.8-flash", "gemini-4-argon-medium", "gemini-4-argon-high"]


def test_copilot_catalog_matches_current_picker_and_cheap_model_prices():
    catalog = load_catalog(REFERENCE_DIR / "copilot-models.json")
    offered_ids = {
        model_id
        for tier in catalog["capability_tiers"].values()
        for model_id in tier
    }
    assert "gpt-6-astra" in offered_ids
    assert "mai-code-1.1-flash" in offered_ids
    assert "kimi-k3" not in offered_ids

    models = {model["cli_id"]: model for model in catalog["models"]}
    assert models["mai-code-1.1-flash"]["credits_per_1m"] == {
        "input": 25, "cached_input": 2.5, "cache_write": 0, "output": 200
    }
    assert models["gpt-5.6-luna"]["credits_per_1m"] == {
        "input": 20, "cached_input": 2, "cache_write": 25, "output": 120
    }


def test_catalog_validation_fails_when_runtime_or_capability_metadata_is_missing():
    catalog = {
        "_meta": {"schema_version": 2},
        "models": [{"cli_id": "cheap", "status": "GA"}],
        "capability_tiers": {"low": ["cheap"], "medium": [], "high": []},
    }

    errors = validate_catalog(catalog)

    assert any("runtime" in error for error in errors)
    assert any("native_capabilities" in error for error in errors)


def test_catalog_validation_fails_when_model_capability_metadata_is_missing():
    catalog = {
        "_meta": {"schema_version": 2},
        "runtime": {
            "runtime_id": "test", "provider": "Test", "availability": "available",
            "native_capabilities": {"planning": "unknown", "worktree": "portable", "subagents": "unknown"},
            "effort_modes": ["low", "medium", "high"],
        },
        "models": [{"cli_id": "cheap", "status": "GA", "pricing_usd_per_1m": {"input": 0.2, "output": 1.0}}],
        "capability_tiers": {"low": ["cheap"], "medium": ["cheap"], "high": ["cheap"]},
    }
    assert "models[0].tool_support is required" in validate_catalog(catalog)


def test_select_model_chooses_least_cost_available_model_for_tier():
    catalog = {
        "_meta": {"schema_version": 2},
        "runtime": {
            "runtime_id": "test",
            "provider": "Test",
            "availability": "available",
            "native_capabilities": {"planning": "unknown", "worktree": "portable", "subagents": "unknown"},
            "effort_modes": ["low", "medium", "high"],
        },
        "models": [
            {"cli_id": "expensive", "status": "GA", "context_window_k": 1, "max_output_k": None, "tool_support": {"prompt": True}, "pricing_usd_per_1m": {"input": 2.0, "output": 10.0}},
            {"cli_id": "cheap", "status": "GA", "context_window_k": 1, "max_output_k": None, "tool_support": {"prompt": True}, "pricing_usd_per_1m": {"input": 0.2, "output": 1.0}},
        ],
        "capability_tiers": {"low": ["expensive", "cheap"], "medium": ["expensive"], "high": ["expensive"]},
    }

    assert select_model(catalog, "low") == "cheap"


def test_select_model_fails_when_no_compatible_model_is_available():
    catalog = {
        "_meta": {"schema_version": 2},
        "runtime": {
            "runtime_id": "test",
            "provider": "Test",
            "availability": "available",
            "native_capabilities": {"planning": "unknown", "worktree": "portable", "subagents": "unknown"},
            "effort_modes": ["low", "medium", "high"],
        },
        "models": [{"cli_id": "withdrawn", "status": "withdrawn", "available": False, "context_window_k": 1, "max_output_k": None, "tool_support": {"prompt": True}, "pricing_usd_per_1m": {"input": 1.0, "output": 1.0}}],
        "capability_tiers": {"low": ["withdrawn"], "medium": [], "high": []},
    }

    with pytest.raises(CatalogContractError, match="No compatible model"):
        select_model(catalog, "low")


def test_select_model_skips_unavailable_preferred_model():
    catalog = {
        "_meta": {"schema_version": 2},
        "runtime": {
            "runtime_id": "test", "provider": "Test", "availability": "available",
            "native_capabilities": {"planning": "unknown", "worktree": "portable", "subagents": "unknown"},
            "effort_modes": ["low", "medium", "high"],
        },
        "models": [
            {"cli_id": "withdrawn", "status": "withdrawn", "context_window_k": 1, "max_output_k": None, "tool_support": {"prompt": True}, "pricing_usd_per_1m": {"input": 0.1, "output": 0.1}},
            {"cli_id": "available", "status": "GA", "context_window_k": 1, "max_output_k": None, "tool_support": {"prompt": True}, "pricing_usd_per_1m": {"input": 1.0, "output": 1.0}},
        ],
        "capability_tiers": {"low": ["withdrawn", "available"], "medium": ["available"], "high": ["available"]},
    }
    assert select_model(catalog, "low", preferred_model="withdrawn") == "available"


def _null_price_catalog(models, tiers):
    return {
        "_meta": {"schema_version": 2},
        "runtime": {
            "runtime_id": "test",
            "provider": "Test",
            "availability": "available",
            "native_capabilities": {"planning": "unknown", "worktree": "portable", "subagents": "unknown"},
            "effort_modes": ["low", "medium", "high"],
        },
        "models": [
            {"cli_id": cid, "status": "available", "context_window_k": None, "max_output_k": None,
             "tool_support": {"prompt": True}, "pricing_usd_per_1m": pricing}
            for cid, pricing in models
        ],
        "capability_tiers": tiers,
    }


def test_select_model_prefers_a_priced_model_over_unknown_pricing():
    catalog = _null_price_catalog(
        [("unknown-price", {"input": None, "output": None}), ("priced", {"input": 1.0, "output": 5.0})],
        {"low": ["unknown-price", "priced"], "medium": ["priced"], "high": ["priced"]},
    )
    assert select_model(catalog, "low") == "priced"


def test_select_model_with_all_prices_unknown_is_deterministic_not_a_crash():
    catalog = _null_price_catalog(
        [("zeta", {"input": None, "output": None}), ("alpha", {})],
        {"low": ["zeta", "alpha"], "medium": ["alpha"], "high": ["alpha"]},
    )
    assert select_model(catalog, "low") == "alpha"
