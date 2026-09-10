"""Tests for the shared versioned runtime/model catalog contract."""

import json
from pathlib import Path

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
    assert catalog["strategy"]["heartbeat"] == "gemini-3.8-flash-low"
    assert catalog["strategy"]["default"] == "gemini-3.8-flash-low"
    assert "gemini-3.5-flash-low" not in agy_models
    flash_low = next(model for model in catalog["models"] if model["cli_id"] == "gemini-3.8-flash-low")
    assert flash_low["context_window_k"] == 1024
    assert flash_low["max_output_k"] == 64
    assert flash_low["pricing_usd_per_1m"]["input"] == 0.75
    assert flash_low["pricing_usd_per_1m"]["output"] == 3.75


def test_codex_catalog_tracks_current_openai_frontier_and_budget_choices():
    catalog = load_catalog(REFERENCE_DIR / "codex-models.json")
    model_ids = {model["cli_id"] for model in catalog["models"]}
    assert {"gpt-6-astra", "gpt-5.6-terra", "gpt-5.6-luna"} <= model_ids
    assert catalog["strategy"]["heartbeat"] == "gpt-5.6-luna"
    assert catalog["strategy"]["default"] == "gpt-5.6-luna"
    assert "gpt-5.6-luna" in catalog["capability_tiers"]["low"]
    assert "gpt-5.6-terra" in catalog["capability_tiers"]["medium"]
    assert "gpt-6-astra" in catalog["capability_tiers"]["high"]


def test_claude_catalog_tracks_current_frontier_choices():
    catalog = load_catalog(REFERENCE_DIR / "claude-models.json")
    model_ids = {model["cli_id"] for model in catalog["models"]}
    assert {"claude-fable-5-1", "claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5"} <= model_ids
    assert catalog["strategy"]["highest_capability"] == "claude-fable-5-1"
    assert catalog["strategy"]["agentic_coding"] == "claude-opus-5"
    assert catalog["strategy"]["heartbeat"] == "claude-haiku-4-5"


def test_copilot_catalog_tracks_current_supported_choices():
    catalog = load_catalog(REFERENCE_DIR / "copilot-models.json")
    model_ids = {model["cli_id"] for model in catalog["models"]}
    assert {"claude-fable-5.1", "claude-opus-5", "mai-code-1.1-flash", "kimi-k3", "grok-4.6"} <= model_ids
    assert "gemini-3.8-flash" in model_ids
    assert catalog["strategy"]["complex_reasoning"] == "claude-opus-5"
    assert catalog["strategy"]["critical_only"] == "claude-fable-5.1"
    assert "claude-opus-5" in catalog["capability_tiers"]["high"]


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
