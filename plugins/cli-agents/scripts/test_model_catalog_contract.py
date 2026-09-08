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
