"""Shared validation and least-cost selection for CLI runtime catalogs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = 2
CAPABILITY_TIERS = ("low", "medium", "high")
NATIVE_CAPABILITY_KEYS = ("planning", "worktree", "subagents")
ALLOWED_CAPABILITY_MODES = {"native", "portable", "unknown"}
UNAVAILABLE_STATUSES = {"withdrawn", "deprecated", "unavailable"}


class CatalogContractError(ValueError):
    """Raised when a catalog cannot satisfy the versioned runtime contract."""


def validate_catalog(catalog: Dict[str, Any]) -> List[str]:
    """Return all schema/metadata errors without silently accepting partial catalogs."""
    errors: List[str] = []
    if not isinstance(catalog, dict):
        return ["catalog must be an object"]

    meta = catalog.get("_meta")
    if not isinstance(meta, dict) or meta.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"_meta.schema_version must be {SCHEMA_VERSION}")

    runtime = catalog.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("runtime metadata is required")
        errors.append("runtime.native_capabilities is required")
    else:
        for field in ("runtime_id", "provider", "availability", "effort_modes"):
            if not runtime.get(field):
                errors.append(f"runtime.{field} is required")
        capabilities = runtime.get("native_capabilities")
        if not isinstance(capabilities, dict):
            errors.append("runtime.native_capabilities is required")
        else:
            for key in NATIVE_CAPABILITY_KEYS:
                if key not in capabilities:
                    errors.append(f"runtime.native_capabilities.{key} is required")
                elif capabilities[key] not in ALLOWED_CAPABILITY_MODES:
                    errors.append(f"runtime.native_capabilities.{key} has an invalid mode")
        effort_modes = runtime.get("effort_modes")
        if isinstance(effort_modes, list) and not set(CAPABILITY_TIERS).issubset(effort_modes):
            errors.append("runtime.effort_modes must include low, medium, and high")

    models = catalog.get("models")
    if not isinstance(models, list) or not models:
        errors.append("models must be a non-empty list")
        model_ids: set[str] = set()
    else:
        model_ids = set()
        for index, model in enumerate(models):
            if not isinstance(model, dict) or not model.get("cli_id"):
                errors.append(f"models[{index}].cli_id is required")
                continue
            model_id = model["cli_id"]
            if model_id in model_ids:
                errors.append(f"duplicate model cli_id: {model_id}")
            model_ids.add(model_id)
            for field in ("context_window_k", "max_output_k", "pricing_usd_per_1m", "tool_support"):
                if field not in model:
                    errors.append(f"models[{index}].{field} is required")

    tiers = catalog.get("capability_tiers")
    if not isinstance(tiers, dict):
        errors.append("capability_tiers is required")
    else:
        for tier in CAPABILITY_TIERS:
            candidates = tiers.get(tier)
            if not isinstance(candidates, list):
                errors.append(f"capability_tiers.{tier} must be a list")
            else:
                missing = [model_id for model_id in candidates if model_id not in model_ids]
                if missing:
                    errors.append(f"capability_tiers.{tier} references unknown model(s): {missing}")

    return errors


def load_catalog(path: Path) -> Dict[str, Any]:
    """Load and validate one authoritative catalog, failing closed on drift."""
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CatalogContractError(f"Unable to load catalog {path}: {exc}") from exc
    errors = validate_catalog(catalog)
    if errors:
        raise CatalogContractError(f"Invalid catalog {path}: {'; '.join(errors)}")
    return catalog


def _is_available(model: Dict[str, Any]) -> bool:
    if model.get("available") is False:
        return False
    return str(model.get("status", "")).lower() not in UNAVAILABLE_STATUSES


def select_model(catalog: Dict[str, Any], tier: str, preferred_model: Optional[str] = None) -> str:
    """Choose the least-cost available model in a declared capability tier."""
    errors = validate_catalog(catalog)
    if errors:
        raise CatalogContractError(f"Invalid catalog: {'; '.join(errors)}")
    normalized_tier = tier.lower()
    if normalized_tier not in CAPABILITY_TIERS:
        raise CatalogContractError(f"Unsupported capability tier: {tier}")

    by_id = {model["cli_id"]: model for model in catalog["models"] if _is_available(model)}
    candidates = [by_id[model_id] for model_id in catalog["capability_tiers"][normalized_tier] if model_id in by_id]
    if not candidates:
        raise CatalogContractError(f"No compatible model is available for tier '{normalized_tier}'")
    if preferred_model and preferred_model in {model["cli_id"] for model in candidates}:
        return preferred_model

    def cost_key(model: Dict[str, Any]) -> tuple[float, float, str]:
        pricing = model.get("pricing_usd_per_1m") or {}
        return (float(pricing.get("input", float("inf"))), float(pricing.get("output", float("inf"))), model["cli_id"])

    return min(candidates, key=cost_key)["cli_id"]
