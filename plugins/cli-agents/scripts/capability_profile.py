"""Load and validate the local, secret-safe CLI capability profile."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional


class ProfileStatus(str, Enum):
    """Lifecycle states exposed to setup and routing callers."""

    UNCONFIGURED = "unconfigured"
    PARTIAL = "partial"
    INVALID = "invalid"
    STALE = "stale"
    READY = "ready"


@dataclass(frozen=True)
class ProfileResult:
    """Validated profile result without exposing raw command output or secrets."""

    status: ProfileStatus
    profile: dict[str, Any]
    errors: tuple[str, ...] = field(default_factory=tuple)
    stale_reasons: tuple[str, ...] = field(default_factory=tuple)


_REQUIRED_FIELDS = (
    "schema_version",
    "providers",
    "constraints",
    "fallback_order",
    "source",
    "updated_at",
)
_ALLOWED_TOP_LEVEL_FIELDS = set(_REQUIRED_FIELDS) | {"plugin_snapshot", "catalog_snapshot"}
_ALLOWED_PROVIDER_FIELDS = {"available", "model_tiers"}
_ALLOWED_MODEL_TIERS = {"low", "medium", "high"}
_FORBIDDEN_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "credentials",
    "password",
    "private_key",
    "secret",
    "token",
}
_FORBIDDEN_KEY_HINTS = ("prompt", "raw_output", "raw_response", "provider_output")


def load_profile(
    path: Path,
    *,
    expected_schema_version: int = 1,
    expected_plugin_snapshot: Optional[str] = None,
    expected_catalog_snapshot: Optional[str] = None,
) -> ProfileResult:
    """Load a profile and classify it without probing providers or storing secrets."""

    profile_path = Path(path)
    if not profile_path.is_file():
        return ProfileResult(ProfileStatus.UNCONFIGURED, {})

    try:
        raw = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return ProfileResult(ProfileStatus.INVALID, {}, (f"profile unreadable: {exc}",))

    errors = _validate_profile(raw, expected_schema_version)
    if errors:
        return ProfileResult(ProfileStatus.INVALID, {}, tuple(errors))

    stale_reasons = []
    if "plugin_snapshot" in raw and expected_plugin_snapshot is None:
        stale_reasons.append("plugin_snapshot_unverified")
    if "catalog_snapshot" in raw and expected_catalog_snapshot is None:
        stale_reasons.append("catalog_snapshot_unverified")
    if expected_plugin_snapshot is not None and raw.get("plugin_snapshot") != expected_plugin_snapshot:
        stale_reasons.append("plugin_snapshot")
    if expected_catalog_snapshot is not None and raw.get("catalog_snapshot") != expected_catalog_snapshot:
        stale_reasons.append("catalog_snapshot")
    if stale_reasons:
        return ProfileResult(ProfileStatus.STALE, raw, stale_reasons=tuple(stale_reasons))

    if any(field not in raw for field in _REQUIRED_FIELDS):
        return ProfileResult(ProfileStatus.PARTIAL, raw)
    return ProfileResult(ProfileStatus.READY, raw)


def write_profile(path: Path, profile: Mapping[str, Any]) -> None:
    """Atomically write a complete profile with owner-only permissions."""

    errors = _validate_profile(dict(profile), expected_schema_version=1)
    if errors or any(field not in profile for field in _REQUIRED_FIELDS):
        details = "; ".join(errors or ["profile is incomplete"])
        raise ValueError(f"cannot write profile: {details}")

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    try:
        os.chmod(temporary, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(profile, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, destination)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def _validate_profile(raw: Any, expected_schema_version: int) -> list[str]:
    """Return validation errors; partial but structurally valid profiles are allowed."""

    if not isinstance(raw, dict):
        return ["profile must be a JSON object"]
    errors: list[str] = []
    for key in raw:
        if key not in _ALLOWED_TOP_LEVEL_FIELDS:
            errors.append(f"profile.{key} is not permitted")
    if raw.get("schema_version") != expected_schema_version:
        errors.append(f"schema_version must be {expected_schema_version}")
    if not isinstance(raw.get("providers", {}), dict):
        errors.append("providers must be an object")
    if "constraints" in raw and not isinstance(raw["constraints"], dict):
        errors.append("constraints must be an object")
    if "fallback_order" in raw and not isinstance(raw["fallback_order"], list):
        errors.append("fallback_order must be an array")
    if "source" in raw and not isinstance(raw["source"], str):
        errors.append("source must be a string")
    if "updated_at" in raw:
        if not isinstance(raw["updated_at"], str):
            errors.append("updated_at must be an ISO-8601 string")
        else:
            try:
                datetime.fromisoformat(raw["updated_at"].replace("Z", "+00:00"))
            except ValueError:
                errors.append("updated_at must be an ISO-8601 string")
    errors.extend(_secret_key_errors(raw))
    providers = raw.get("providers", {})
    if not isinstance(providers, dict):
        return errors
    for provider, data in providers.items():
        if not isinstance(provider, str) or not isinstance(data, dict):
            errors.append("each provider entry must be an object")
            continue
        if "available" in data and not isinstance(data["available"], bool):
            errors.append(f"providers.{provider}.available must be boolean")
        if "model_tiers" in data and not isinstance(data["model_tiers"], dict):
            errors.append(f"providers.{provider}.model_tiers must be an object")
        elif isinstance(data.get("model_tiers"), dict):
            for tier, model in data["model_tiers"].items():
                if tier not in _ALLOWED_MODEL_TIERS:
                    errors.append(f"providers.{provider}.model_tiers.{tier} is not permitted")
                elif not isinstance(model, str) or not model.strip():
                    errors.append(f"providers.{provider}.model_tiers.{tier} must be a non-empty string")
        for key in data:
            if key not in _ALLOWED_PROVIDER_FIELDS:
                errors.append(f"providers.{provider}.{key} is not permitted")
    return errors


def _secret_key_errors(value: Any, prefix: str = "profile") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if (
                normalized in _FORBIDDEN_KEYS
                or any(token in normalized for token in ("api_key", "token", "password"))
                or any(hint in normalized for hint in _FORBIDDEN_KEY_HINTS)
            ):
                errors.append(f"{prefix}.{key} is not permitted")
            errors.extend(_secret_key_errors(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_secret_key_errors(child, f"{prefix}[{index}]"))
    return errors
