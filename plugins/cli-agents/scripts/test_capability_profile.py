"""Contract tests for the local, secret-safe capability profile."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from capability_profile import ProfileStatus, load_profile, write_profile


def _write_profile(tmp_path, payload):
    path = tmp_path / "agent-profile.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_missing_profile_is_unconfigured(tmp_path):
    result = load_profile(tmp_path / "missing.json")

    assert result.status is ProfileStatus.UNCONFIGURED
    assert result.profile == {}


def test_partial_profile_is_reported_without_inventing_provider_access(tmp_path):
    path = _write_profile(
        tmp_path,
        {"schema_version": 1, "providers": {"codex": {"available": True}}},
    )

    result = load_profile(path)

    assert result.status is ProfileStatus.PARTIAL
    assert result.profile["providers"]["codex"]["available"] is True


def test_invalid_profile_reports_validation_errors(tmp_path):
    path = _write_profile(tmp_path, {"schema_version": "one", "providers": []})

    result = load_profile(path)

    assert result.status is ProfileStatus.INVALID
    assert result.errors


def test_malformed_provider_entry_is_invalid(tmp_path):
    path = _write_profile(
        tmp_path,
        {
            "schema_version": 1,
            "providers": {"codex": "not-an-object"},
            "constraints": {},
            "fallback_order": ["codex"],
            "source": "user-confirmed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    result = load_profile(path)

    assert result.status is ProfileStatus.INVALID
    assert any("provider entry" in error for error in result.errors)


def test_malformed_json_is_invalid_without_raising(tmp_path):
    path = tmp_path / "agent-profile.json"
    path.write_text("{not-json", encoding="utf-8")

    result = load_profile(path)

    assert result.status is ProfileStatus.INVALID
    assert result.errors


def test_secret_bearing_profile_is_invalid_and_not_exposed(tmp_path):
    path = _write_profile(
        tmp_path,
        {
            "schema_version": 1,
            "providers": {"codex": {"available": True, "api_key": "do-not-store"}},
            "constraints": {},
            "fallback_order": ["codex"],
            "source": "user-confirmed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    result = load_profile(path)

    assert result.status is ProfileStatus.INVALID
    assert any("api_key" in error for error in result.errors)
    assert result.profile == {}


def test_unknown_fields_and_raw_provider_output_are_invalid(tmp_path):
    path = _write_profile(
        tmp_path,
        {
            "schema_version": 1,
            "providers": {"codex": {
                "available": True,
                "model_tiers": {"low": 42},
                "raw_output": "provider response",
            }},
            "constraints": {},
            "fallback_order": ["codex"],
            "source": "user-confirmed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "unexpected_field": "not part of the contract",
        },
    )

    result = load_profile(path)

    assert result.status is ProfileStatus.INVALID
    assert any("not permitted" in error for error in result.errors)


def test_unavailable_provider_profile_remains_ready_but_is_not_authorized(tmp_path):
    path = _write_profile(
        tmp_path,
        {
            "schema_version": 1,
            "providers": {"codex": {"available": False, "model_tiers": {"low": "gpt-low"}}},
            "constraints": {},
            "fallback_order": ["codex"],
            "source": "user-confirmed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    result = load_profile(path)

    assert result.status is ProfileStatus.READY
    assert result.profile["providers"]["codex"]["available"] is False


def test_profile_is_stale_when_schema_or_catalog_snapshot_changes(tmp_path):
    path = _write_profile(
        tmp_path,
        {
            "schema_version": 1,
            "providers": {"codex": {"available": True}},
            "constraints": {"workplace_restrictions": [], "network_restricted": False},
            "fallback_order": ["codex"],
            "source": "user-confirmed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "plugin_snapshot": "old-plugin",
            "catalog_snapshot": "old-catalog",
        },
    )

    result = load_profile(
        path,
        expected_plugin_snapshot="new-plugin",
        expected_catalog_snapshot="new-catalog",
    )

    assert result.status is ProfileStatus.STALE
    assert set(result.stale_reasons) == {"plugin_snapshot", "catalog_snapshot"}


def test_snapshot_bearing_profile_is_stale_without_expected_snapshots(tmp_path):
    path = _write_profile(
        tmp_path,
        {
            "schema_version": 1,
            "providers": {"codex": {"available": True, "model_tiers": {"low": "gpt-low"}}},
            "constraints": {},
            "fallback_order": ["codex"],
            "source": "user-confirmed",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "plugin_snapshot": "unknown-current-plugin",
        },
    )

    result = load_profile(path)

    assert result.status is ProfileStatus.STALE
    assert result.stale_reasons == ("plugin_snapshot_unverified",)


def test_write_profile_validates_and_uses_private_file_permissions(tmp_path):
    path = tmp_path / "nested" / "agent-profile.json"
    profile = {
        "schema_version": 1,
        "providers": {"codex": {"available": True, "model_tiers": {"low": "gpt-low"}}},
        "constraints": {"workplace_restrictions": [], "network_restricted": False},
        "fallback_order": ["codex"],
        "source": "user-confirmed",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    write_profile(path, profile)

    assert load_profile(path).status is ProfileStatus.READY
    assert path.stat().st_mode & 0o077 == 0
