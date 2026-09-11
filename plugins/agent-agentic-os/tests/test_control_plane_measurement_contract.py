"""A12: Measurement schema, semantics, and privacy contract tests for P02.

Tests the canonical measurement observation contract:
- Producer fixture fidelity (AC02, AC03, A18)
- Null versus zero distinctions
- Measured vs reported vs estimated vs unavailable provenance
- Units, ranges, and scope semantics
- Token subsets and non-additive aggregation
- Deterministic canonicalization and SHA-256 digest
- Settlement: idempotency, conflicts, cumulative precedence, and corrections
- Transition-attempt versus committed-transition identity
- Independent execution attempts
- Requested versus observed model
- Privacy and allowlist enforcement (AC08)
"""

import json
from pathlib import Path
import sys
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.measurement import (
    MeasurementError,
    MeasurementValidationError,
    MeasurementPrivacyViolation,
    MeasurementSettlementConflict,
    MeasurementObservation,
    ObservationCapture,
    ObservationProducer,
    ObservationCorrelation,
    ObservationEvent,
    ObservationExecution,
    ObservationUsage,
    ObservationScope,
    SettlementResult,
    canonicalize_observation_json,
    compute_canonical_digest,
    validate_observation_dict,
    validate_observation_json,
    settle_observations,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "cli-agents"
    / "references"
    / "p0-codex-observation-fixture.json"
)


def _valid_observation_dict():
    """Returns a minimal valid observation dictionary with a non-draft valid digest."""
    obs = {
        "artifact_kind": "p0_measurement_observation",
        "schema_version": "1.0-draft",
        "capture": {
            "method": "cli_wrapper",
            "captured_at_utc": "2026-09-10T12:00:00Z",
            "source_runtime": "codex_cli",
            "source_runtime_version": "1.2.3",
            "sanitization": "allowlist_only",
        },
        "producer": {
            "namespace": "io.richfrem.cli-agents.codex",
            "version": "1.0.0",
            "install_fingerprint": "abc123def456",
        },
        "correlation": {
            "task_id": "task_1",
            "task_generation_id": "gen_1",
            "run_id": "run_1",
            "invocation_id": "inv_1",
            "attempt_id": "attempt_1",
        },
        "event": {
            "event_id": "018f6d42-6b2e-7cc0-8f1b-1234567890ab",
            "occurred_at_utc": "2026-09-10T12:00:01Z",
            "coverage_state": "observed",
            "canonical_digest": None,  # Will compute below
        },
        "execution": {
            "exit_code": 0,
            "duration_ms": 1500,
            "duration_provenance": "measured",
            "requested_model": "codex-standard",
            "observed_model": "codex-standard-2026",
        },
        "usage": {
            "provenance": "measured",
            "input_tokens": 100,
            "output_tokens": 50,
            "cached_tokens": 20,
            "reasoning_tokens": 10,
        },
    }
    raw = json.dumps(obs)
    digest = compute_canonical_digest(raw)
    obs["event"]["canonical_digest"] = digest
    return obs


# =========================================================================
# 1. Producer Fixture Fidelity (AC02, AC03, A18)
# =========================================================================


def test_load_actual_codex_producer_fixture():
    assert FIXTURE_PATH.is_file(), f"Fixture not found at {FIXTURE_PATH}"
    with open(FIXTURE_PATH, "rb") as f:
        raw_bytes = f.read()

    obs = validate_observation_json(raw_bytes, is_draft_fixture=True)
    assert isinstance(obs, MeasurementObservation)
    assert obs.artifact_kind == "p0_measurement_observation"
    assert obs.schema_version == "1.0-draft"
    assert obs.capture.source_runtime == "codex_cli"
    assert obs.capture.source_runtime_version is None
    assert obs.capture.source_runtime_version_unavailable_reason == "Fixture only; no installed runtime was sampled."
    assert obs.producer.namespace == "io.richfrem.cli-agents.codex"
    assert obs.correlation.task_id == "task_fixture_p0"
    assert obs.event.event_id == "018f6d42-6b2e-7cc0-8f1b-1234567890ab"
    assert obs.event.coverage_state == "observed"
    assert obs.event.canonical_digest is None
    assert obs.event.canonical_digest_unavailable_reason == "Draft fixture; runtime canonicalization is not implemented."
    assert obs.execution.exit_code == 0
    assert obs.execution.duration_ms == 1250
    assert obs.execution.duration_provenance == "synthetic_fixture"
    assert obs.execution.requested_model == "unavailable"
    assert obs.execution.observed_model is None
    assert obs.execution.observed_model_unavailable_reason == "No live runtime capture was authorized."
    assert obs.usage.provenance == "unavailable"
    assert obs.usage.input_tokens is None
    assert obs.usage.output_tokens is None
    assert obs.usage.cached_tokens is None
    assert obs.usage.reasoning_tokens is None
    assert obs.usage.unavailable_reason == "No verified structured Codex CLI usage output has been captured."


# =========================================================================
# 2. Strict JSON Rejections & Bounds (P00 Canonicalization Rules)
# =========================================================================


def test_strict_json_duplicate_keys_rejected():
    raw = b"""{"artifact_kind": "p0_measurement_observation", "artifact_kind": "p0_measurement_observation"}"""
    with pytest.raises(MeasurementValidationError, match="[Dd]uplicate key"):
        validate_observation_json(raw)


def test_strict_json_decimals_and_exponents_rejected():
    base = _valid_observation_dict()
    # Decimal in duration_ms
    raw_dec = json.dumps(base).replace('"duration_ms": 1500', '"duration_ms": 1500.5')
    with pytest.raises(MeasurementValidationError, match="[Ff]loat|[Dd]ecimal"):
        validate_observation_json(raw_dec)

    # Exponent in exit_code
    raw_exp = json.dumps(base).replace('"exit_code": 0', '"exit_code": 1e2')
    with pytest.raises(MeasurementValidationError, match="[Ff]loat|[Dd]ecimal|[Ee]xponent"):
        validate_observation_json(raw_exp)


def test_strict_json_minus_zero_rejected():
    base = _valid_observation_dict()
    raw = json.dumps(base).replace('"exit_code": 0', '"exit_code": -0')
    with pytest.raises(MeasurementValidationError, match="-0"):
        validate_observation_json(raw)


def test_strict_json_non_finite_rejected():
    raw_nan = b"""{"exit_code": NaN}"""
    with pytest.raises(MeasurementValidationError):
        validate_observation_json(raw_nan)

    raw_inf = b"""{"exit_code": Infinity}"""
    with pytest.raises(MeasurementValidationError):
        validate_observation_json(raw_inf)


def test_strict_json_integer_bounds():
    base = _valid_observation_dict()
    base["execution"]["duration_ms"] = 9007199254740992  # Exceeds max safe int
    raw = json.dumps(base)
    with pytest.raises(MeasurementValidationError, match="bounds|range"):
        validate_observation_json(raw)


# =========================================================================
# 3. Canonicalization and Digest Validation (p0-event-identity-schema)
# =========================================================================


def test_canonicalization_sorts_keys_and_normalizes_timestamps():
    data = {
        "z_key": "last",
        "a_key": "first",
        "capture": {
            "captured_at_utc": "2026-09-10T12:00:00.1Z",
            "method": "test",
            "sanitization": "allowlist",
            "source_runtime": "codex",
            "source_runtime_version": "1",
        },
        "event": {
            "event_id": "018f6d42-6b2e-7cc0-8f1b-1234567890ab",
            "occurred_at_utc": "2026-09-10T17:30:00+05:30",
            "coverage_state": "observed",
            "canonical_digest": "will_be_removed",
        },
    }
    canon_bytes = canonicalize_observation_json(data)
    canon_str = canon_bytes.decode("utf-8")

    # event.canonical_digest must be removed
    assert "canonical_digest" not in canon_str
    # Keys must be sorted in Unicode code point order
    assert canon_str.find('"a_key"') < canon_str.find('"capture"')
    assert canon_str.find('"capture"') < canon_str.find('"event"')
    assert canon_str.find('"event"') < canon_str.find('"z_key"')

    # Timestamps normalized to YYYY-MM-DDTHH:MM:SS.ffffffZ
    assert '"captured_at_utc":"2026-09-10T12:00:00.100000Z"' in canon_str
    assert '"occurred_at_utc":"2026-09-10T12:00:00.000000Z"' in canon_str



def test_canonical_digest_mismatch_raises_artifact_invalid():
    base = _valid_observation_dict()
    base["event"]["canonical_digest"] = "a" * 64  # Invalid digest
    with pytest.raises(MeasurementValidationError, match="digest mismatch|artifact_invalid"):
        validate_observation_dict(base)


# =========================================================================
# 4. Null versus Zero Semantics
# =========================================================================


def test_zero_tokens_is_valid_measured_value():
    base = _valid_observation_dict()
    base["usage"]["input_tokens"] = 0
    base["usage"]["output_tokens"] = 0
    base["usage"]["cached_tokens"] = 0
    base["usage"]["reasoning_tokens"] = 0
    base["usage"]["unavailable_reason"] = None
    # All tokens are integers (0), so unavailable_reason must NOT be set
    raw = json.dumps(base)
    base["event"]["canonical_digest"] = compute_canonical_digest(raw)
    obs = validate_observation_dict(base)
    assert obs.usage.input_tokens == 0
    assert obs.usage.cached_tokens == 0
    assert obs.usage.unavailable_reason is None


def test_null_token_requires_unavailable_reason():
    base = _valid_observation_dict()
    base["usage"]["cached_tokens"] = None
    base["usage"]["unavailable_reason"] = None
    with pytest.raises(MeasurementValidationError, match="unavailable_reason"):
        validate_observation_dict(base)

    # Adding non-empty reason satisfies the contract
    base["usage"]["unavailable_reason"] = "Provider does not report cache hits"
    base["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base))
    obs = validate_observation_dict(base)
    assert obs.usage.cached_tokens is None
    assert obs.usage.unavailable_reason == "Provider does not report cache hits"


def test_unavailable_provenance_requires_all_tokens_null():
    base = _valid_observation_dict()
    base["usage"]["provenance"] = "unavailable"
    base["usage"]["input_tokens"] = 10  # Non-null violates unavailable provenance
    base["usage"]["unavailable_reason"] = "No usage"
    with pytest.raises(MeasurementValidationError, match="all token fields null"):
        validate_observation_dict(base)


def test_duration_ms_zero_is_valid_negative_is_rejected():
    base = _valid_observation_dict()
    base["execution"]["duration_ms"] = 0
    base["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base))
    obs = validate_observation_dict(base)
    assert obs.execution.duration_ms == 0

    base["execution"]["duration_ms"] = -1
    with pytest.raises(MeasurementValidationError, match="non-negative"):
        validate_observation_dict(base)


# =========================================================================
# 5. Token Subsets and Non-Additive Semantics
# =========================================================================


def test_token_subsets_are_not_additively_summed_to_invent_totals():
    base = _valid_observation_dict()
    # input: 100, cached: 20 (cached is a subset of input)
    # output: 50, reasoning: 10 (reasoning is a subset of output)
    base["usage"]["input_tokens"] = 100
    base["usage"]["output_tokens"] = 50
    base["usage"]["cached_tokens"] = 20
    base["usage"]["reasoning_tokens"] = 10
    base["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base))

    obs = validate_observation_dict(base)
    result = settle_observations([obs])

    # Settle result must report components distinctly and refuse to sum 100+50+20+10=180
    assert result.total_input_tokens == 100
    assert result.total_output_tokens == 50
    assert result.cached_tokens_subset == 20
    assert result.reasoning_tokens_subset == 10
    assert result.invented_aggregate_tokens is None  # Never invent additive total


# =========================================================================
# 6. Settlement: Idempotency, Conflicts, Cumulative Precedence, Corrections
# =========================================================================


def test_settlement_identical_redelivery_is_idempotent():
    base = _valid_observation_dict()
    obs1 = validate_observation_dict(base)
    obs2 = validate_observation_dict(base)

    result = settle_observations([obs1, obs2])
    assert result.status == "observed"
    assert len(result.observations) == 1
    assert result.duplicate_count == 1


def test_settlement_conflicting_digest_redelivery_is_ambiguous():
    base1 = _valid_observation_dict()
    obs1 = validate_observation_dict(base1)

    base2 = dict(base1)
    base2["execution"] = dict(base1["execution"])
    base2["execution"]["exit_code"] = 1  # Different execution content
    base2["event"] = dict(base1["event"])
    base2["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base2))
    obs2 = validate_observation_dict(base2)

    with pytest.raises(MeasurementSettlementConflict, match="ambiguous|conflict"):
        settle_observations([obs1, obs2])


def test_settlement_cumulative_final_supersedes_snapshots():
    base_snap = _valid_observation_dict()
    base_snap["event"]["event_id"] = "018f6d42-6b2e-7cc0-8f1b-1234567890aa"
    base_snap["usage"]["scope"] = "snapshot"
    base_snap["usage"]["input_tokens"] = 50
    base_snap["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base_snap))
    obs_snap = validate_observation_dict(base_snap)

    base_final = _valid_observation_dict()
    base_final["event"]["event_id"] = "018f6d42-6b2e-7cc0-8f1b-1234567890ab"
    base_final["usage"]["scope"] = "final"
    base_final["usage"]["input_tokens"] = 120
    base_final["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base_final))
    obs_final = validate_observation_dict(base_final)

    result = settle_observations([obs_snap, obs_final], scope=ObservationScope.CUMULATIVE)
    assert result.total_input_tokens == 120  # Final supersedes earlier snapshot
    assert len(result.observations) == 2  # Earlier snapshot retained in history


def test_settlement_late_correction_links_and_updates_active_aggregate():
    base_orig = _valid_observation_dict()
    base_orig["event"]["event_id"] = "018f6d42-6b2e-7cc0-8f1b-1234567890aa"
    base_orig["usage"]["input_tokens"] = 100
    base_orig["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base_orig))
    obs_orig = validate_observation_dict(base_orig)

    base_corr = _valid_observation_dict()
    base_corr["event"]["event_id"] = "018f6d42-6b2e-7cc0-8f1b-1234567890ab"
    base_corr["event"]["causal_parent_event_id"] = "018f6d42-6b2e-7cc0-8f1b-1234567890aa"
    base_corr["usage"]["scope"] = "correction"
    base_corr["usage"]["input_tokens"] = 115
    base_corr["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base_corr))
    obs_corr = validate_observation_dict(base_corr)

    result = settle_observations([obs_orig, obs_corr])
    assert result.total_input_tokens == 115
    assert len(result.observations) == 2
    assert obs_corr.event.causal_parent_event_id == obs_orig.event.event_id


def test_settlement_incompatible_sources_remains_unsettled():
    base1 = _valid_observation_dict()
    base1["producer"]["namespace"] = "io.richfrem.provider1"
    base1["usage"]["scope"] = "cumulative"
    base1["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base1))
    obs1 = validate_observation_dict(base1)

    base2 = _valid_observation_dict()
    base2["event"]["event_id"] = "018f6d42-6b2e-7cc0-8f1b-1234567890ac"
    base2["producer"]["namespace"] = "io.richfrem.provider2"
    base2["usage"]["scope"] = "delta"  # Incompatible scope
    base2["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base2))
    obs2 = validate_observation_dict(base2)

    result = settle_observations([obs1, obs2])
    assert result.is_settled is False
    assert result.unsettled_reason == "Incompatible measurement scopes: cumulative vs delta"


# =========================================================================
# 7. Transition-Attempt vs Committed-Transition & Independent Attempts
# =========================================================================


def test_transition_attempt_distinct_from_committed_transition():
    # Denied transition attempt: records transition_attempt_id, but committed_transition_id is None
    base = _valid_observation_dict()
    base["correlation"]["transition_attempt_id"] = "ta_123"
    base["correlation"]["committed_transition_id"] = None
    base["event"]["coverage_state"] = "observed"
    base["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base))

    obs = validate_observation_dict(base)
    assert obs.correlation.transition_attempt_id == "ta_123"
    assert obs.correlation.committed_transition_id is None
    assert obs.claims_committed_transition is False

    # Committed transition: records both
    base["correlation"]["committed_transition_id"] = "ct_456"
    base["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base))
    obs_comm = validate_observation_dict(base)
    assert obs_comm.correlation.committed_transition_id == "ct_456"
    assert obs_comm.claims_committed_transition is True


def test_independent_execution_attempts_must_have_distinct_ids():
    base1 = _valid_observation_dict()
    base1["correlation"]["attempt_id"] = "attempt_1"
    base1["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base1))
    obs1 = validate_observation_dict(base1)

    # Re-executing with the same attempt_id must be rejected
    base2 = _valid_observation_dict()
    base2["event"]["event_id"] = "018f6d42-6b2e-7cc0-8f1b-1234567890bb"
    base2["correlation"]["attempt_id"] = "attempt_1"  # Reused attempt_id!
    base2["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base2))
    obs2 = validate_observation_dict(base2)

    with pytest.raises(MeasurementSettlementConflict, match="reused attempt_id|attempt identity"):
        settle_observations([obs1, obs2], distinct_execution_attempts=True)


# =========================================================================
# 8. Requested versus Observed Model
# =========================================================================


def test_requested_vs_observed_model_distinction():
    base = _valid_observation_dict()
    base["execution"]["requested_model"] = "codex-preview"
    base["execution"]["observed_model"] = None
    base["execution"]["observed_model_unavailable_reason"] = "CLI does not report resolved model"
    base["event"]["canonical_digest"] = compute_canonical_digest(json.dumps(base))

    obs = validate_observation_dict(base)
    assert obs.execution.requested_model == "codex-preview"
    assert obs.execution.observed_model is None
    assert obs.execution.observed_model_unavailable_reason == "CLI does not report resolved model"

    # If observed_model is a string, observed_model_unavailable_reason is prohibited
    base["execution"]["observed_model"] = "codex-preview-0901"
    with pytest.raises(MeasurementValidationError, match="observed_model_unavailable_reason"):
        validate_observation_dict(base)


# =========================================================================
# 9. Privacy and Allowlist Enforcement (AC08)
# =========================================================================


@pytest.mark.parametrize(
    "sensitive_key",
    [
        "prompt",
        "output",
        "stdout",
        "stderr",
        "secret",
        "api_key",
        "token",
        "system_prompt",
        "user_input",
        "environment",
        "source_code",
    ],
)
def test_privacy_rejects_unallowlisted_sensitive_keys(sensitive_key):
    base = _valid_observation_dict()
    base[sensitive_key] = "sensitive payload data"
    with pytest.raises((MeasurementPrivacyViolation, MeasurementValidationError), match="[Uu]nallowlisted|[Ff]orbidden|[Aa]dditional"):
        validate_observation_dict(base)

    # Also test nested under usage or execution
    base2 = _valid_observation_dict()
    base2["usage"][sensitive_key] = "leak"
    with pytest.raises((MeasurementPrivacyViolation, MeasurementValidationError)):
        validate_observation_dict(base2)


def test_privacy_rejects_oversized_payload():
    large_reason = "X" * (1024 * 1024 + 10)  # > 1 MiB
    base = _valid_observation_dict()
    base["usage"]["cached_tokens"] = None
    base["usage"]["unavailable_reason"] = large_reason
    raw = json.dumps(base).encode("utf-8")
    with pytest.raises(MeasurementPrivacyViolation, match="size limit|1 MiB"):
        validate_observation_json(raw)
