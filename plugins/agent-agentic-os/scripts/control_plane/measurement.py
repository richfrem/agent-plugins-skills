"""P02 Measurement schema, semantics, canonicalization, settlement, and privacy contract.

Implements the minimum canonical measurement representation required by actual producer fixtures
and P00 specifications:
- Canonical event identity: (producer_namespace, schema_version, event_id)
- Deterministic P00 canonicalization and SHA-256 digest computation
- Strict JSON parsing (closed schema, duplicate key rejection, integer bounds, no decimals/-0)
- Null versus zero semantics (explicit unavailable reasons for null; 0 is valid recorded integer)
- Measured vs reported vs estimated vs unavailable provenance
- Token subsets preservation (cached is subset of input, reasoning is subset of output) without invented totals
- Settlement: idempotency on identical redelivery, ambiguous conflict on divergent digest,
  cumulative precedence (final supersedes snapshots), and causal corrections
- Transition attempt versus committed transition identity
- Privacy: closed allowlist enforcement, sensitive field exclusion, 1 MiB artifact ceiling
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum
import hashlib
import hmac
import json
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


# =========================================================================
# Constants & Boundaries
# =========================================================================

MAX_ARTIFACT_BYTES: int = 1024 * 1024  # 1 MiB ceiling
SAFE_INT_MIN: int = -9007199254740991  # -(2^53 - 1)
SAFE_INT_MAX: int = 9007199254740991   # 2^53 - 1

CANONICAL_ARTIFACT_KIND: str = "p0_measurement_observation"
CANONICAL_SCHEMA_VERSION: str = "1.0-draft"

FORBIDDEN_SENSITIVE_KEYS = frozenset({
    "prompt",
    "prompts",
    "system_prompt",
    "user_input",
    "output",
    "outputs",
    "stdout",
    "stderr",
    "secret",
    "secrets",
    "api_key",
    "api_keys",
    "token",  # Secret token; measurement counters are *_tokens
    "password",
    "passwords",
    "env",
    "environment",
    "source_code",
    "file_content",
    "file_contents",
})

ALLOWED_ROOT_KEYS = frozenset({
    "artifact_kind",
    "schema_version",
    "capture",
    "producer",
    "correlation",
    "event",
    "execution",
    "usage",
})

ALLOWED_CAPTURE_KEYS = frozenset({
    "method",
    "captured_at_utc",
    "source_runtime",
    "source_runtime_version",
    "source_runtime_version_unavailable_reason",
    "sanitization",
})

ALLOWED_PRODUCER_KEYS = frozenset({
    "namespace",
    "version",
    "install_fingerprint",
    "install_fingerprint_unavailable_reason",
})

ALLOWED_CORRELATION_KEYS = frozenset({
    "task_id",
    "task_generation_id",
    "run_id",
    "invocation_id",
    "attempt_id",
    "transition_attempt_id",
    "committed_transition_id",
})

ALLOWED_EVENT_KEYS = frozenset({
    "event_id",
    "occurred_at_utc",
    "coverage_state",
    "canonical_digest",
    "canonical_digest_unavailable_reason",
    "causal_parent_event_id",
})

ALLOWED_EXECUTION_KEYS = frozenset({
    "exit_code",
    "duration_ms",
    "duration_provenance",
    "requested_model",
    "observed_model",
    "observed_model_unavailable_reason",
})

ALLOWED_USAGE_KEYS = frozenset({
    "provenance",
    "input_tokens",
    "output_tokens",
    "cached_tokens",
    "reasoning_tokens",
    "unavailable_reason",
    "scope",
})


# =========================================================================
# Enums
# =========================================================================

class CoverageState(str, Enum):
    EXPECTED = "expected"
    STARTED = "started"
    OBSERVED = "observed"
    ARTIFACT_MISSING = "artifact_missing"
    ARTIFACT_INVALID = "artifact_invalid"
    INGEST_PENDING = "ingest_pending"
    AMBIGUOUS = "ambiguous"
    UNAVAILABLE = "unavailable"


class MetricProvenance(str, Enum):
    REPORTED = "reported"
    MEASURED = "measured"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"


class DurationProvenance(str, Enum):
    REPORTED = "reported"
    MEASURED = "measured"
    ESTIMATED = "estimated"
    SYNTHETIC_FIXTURE = "synthetic_fixture"


class ObservationScope(str, Enum):
    CUMULATIVE = "cumulative"
    DELTA = "delta"
    SNAPSHOT = "snapshot"
    FINAL = "final"
    CORRECTION = "correction"


# =========================================================================
# Exceptions
# =========================================================================

class MeasurementError(Exception):
    """Base class for measurement contract exceptions."""
    pass


class MeasurementValidationError(MeasurementError):
    """Raised when schema, types, timestamps, or digest rules are violated (artifact_invalid)."""
    pass


class MeasurementPrivacyViolation(MeasurementError):
    """Raised when unallowlisted or forbidden sensitive fields are detected, or payload is oversized."""
    pass


class MeasurementSettlementConflict(MeasurementError):
    """Raised when identical key with divergent digest (ambiguous) or illegal retry identity is encountered."""
    pass


# =========================================================================
# Data Models
# =========================================================================

@dataclass(frozen=True)
class ObservationCapture:
    method: str
    captured_at_utc: str
    source_runtime: str
    source_runtime_version: Optional[str]
    source_runtime_version_unavailable_reason: Optional[str]
    sanitization: str


@dataclass(frozen=True)
class ObservationProducer:
    namespace: str
    version: str
    install_fingerprint: Optional[str]
    install_fingerprint_unavailable_reason: Optional[str]


@dataclass(frozen=True)
class ObservationCorrelation:
    task_id: str
    task_generation_id: str
    run_id: str
    invocation_id: str
    attempt_id: str
    transition_attempt_id: Optional[str] = None
    committed_transition_id: Optional[str] = None


@dataclass(frozen=True)
class ObservationEvent:
    event_id: str
    occurred_at_utc: str
    coverage_state: str
    canonical_digest: Optional[str]
    canonical_digest_unavailable_reason: Optional[str] = None
    causal_parent_event_id: Optional[str] = None


@dataclass(frozen=True)
class ObservationExecution:
    exit_code: int
    duration_ms: int
    duration_provenance: str
    requested_model: str
    observed_model: Optional[str]
    observed_model_unavailable_reason: Optional[str] = None


@dataclass(frozen=True)
class ObservationUsage:
    provenance: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    cached_tokens: Optional[int]
    reasoning_tokens: Optional[int]
    unavailable_reason: Optional[str] = None
    scope: Optional[str] = None


@dataclass(frozen=True)
class MeasurementObservation:
    artifact_kind: str
    schema_version: str
    capture: ObservationCapture
    producer: ObservationProducer
    correlation: ObservationCorrelation
    event: ObservationEvent
    execution: ObservationExecution
    usage: ObservationUsage

    @property
    def canonical_key(self) -> Tuple[str, str, str]:
        return (self.producer.namespace, self.schema_version, self.event.event_id)

    @property
    def claims_committed_transition(self) -> bool:
        return bool(self.correlation.committed_transition_id)


@dataclass
class SettlementResult:
    status: str
    observations: List[MeasurementObservation]
    total_input_tokens: Optional[int] = None
    total_output_tokens: Optional[int] = None
    cached_tokens_subset: Optional[int] = None
    reasoning_tokens_subset: Optional[int] = None
    invented_aggregate_tokens: Optional[int] = None  # Always None to preserve subset integrity
    duplicate_count: int = 0
    is_settled: bool = True
    unsettled_reason: Optional[str] = None


# =========================================================================
# RFC 3339 Normalization
# =========================================================================

_RFC3339_REGEX = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})[Tt](\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?([Zz]|([+-]\d{2}):(\d{2}))$"
)


def normalize_rfc3339_timestamp(ts: str) -> str:
    """Normalize RFC 3339 timestamp to YYYY-MM-DDTHH:MM:SS.ffffffZ.

    Rejects leap seconds, parse failures, and fractional seconds with > 6 digits.
    """
    match = _RFC3339_REGEX.match(ts)
    if not match:
        raise MeasurementValidationError(f"Timestamp is not valid RFC 3339: {ts}")

    year, month, day, hour, minute, second, frac, tz_full, tz_hr, tz_min = match.groups()
    sec_int = int(second)
    if sec_int >= 60:
        raise MeasurementValidationError(f"Leap seconds are not supported: {ts}")

    if frac is not None and len(frac) > 6:
        raise MeasurementValidationError(
            f"Fractional seconds with more than 6 digits are rejected (no truncation/rounding): {ts}"
        )

    microsecond_int = int(frac.ljust(6, "0")) if frac else 0

    year_int = int(year)
    month_int = int(month)
    day_int = int(day)
    hour_int = int(hour)
    min_int = int(minute)

    if tz_full.upper() == "Z":
        offset_minutes = 0
    else:
        sign = 1 if tz_full[0] == "+" else -1
        offset_minutes = sign * (int(tz_hr[1:]) * 60 + int(tz_min))

    dt = datetime(
        year_int,
        month_int,
        day_int,
        hour_int,
        min_int,
        sec_int,
        microsecond_int,
        tzinfo=timezone(timedelta(minutes=offset_minutes)),
    )
    dt_utc = dt.astimezone(timezone.utc)

    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S") + f".{dt_utc.microsecond:06d}Z"


# =========================================================================
# Strict JSON Parser
# =========================================================================

def _strict_parse_int(val_str: str) -> int:
    if val_str == "-0":
        raise MeasurementValidationError("Minus zero (-0) representation is rejected")
    if val_str.startswith("+"):
        raise MeasurementValidationError("Leading plus is not permitted in integers")
    if len(val_str) > 1 and val_str.startswith("0"):
        raise MeasurementValidationError("Leading zero is not permitted in integers")
    if len(val_str) > 2 and val_str.startswith("-0"):
        raise MeasurementValidationError("Leading zero after minus is not permitted in integers")
    val = int(val_str)
    if val < SAFE_INT_MIN or val > SAFE_INT_MAX:
        raise MeasurementValidationError(f"Integer {val} exceeds safe range [{SAFE_INT_MIN}, {SAFE_INT_MAX}]")
    return val


def _strict_parse_float(val_str: str) -> Any:
    raise MeasurementValidationError(f"Decimal or floating-point number representation is rejected: {val_str}")


def _strict_parse_constant(val_str: str) -> Any:
    raise MeasurementValidationError(f"Non-finite number representation ({val_str}) is rejected")


def _strict_pairs_hook(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    for k, v in pairs:
        if k in d:
            raise MeasurementValidationError(f"Duplicate key rejected: {k}")
        d[k] = v
    return d


def parse_strict_json(raw: Union[bytes, str]) -> Dict[str, Any]:
    if isinstance(raw, bytes):
        if len(raw) > MAX_ARTIFACT_BYTES:
            raise MeasurementPrivacyViolation(f"Payload size {len(raw)} exceeds 1 MiB limit")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as e:
            raise MeasurementValidationError(f"Strict UTF-8 decode error: {e}")
    else:
        text_bytes = raw.encode("utf-8")
        if len(text_bytes) > MAX_ARTIFACT_BYTES:
            raise MeasurementPrivacyViolation(f"Payload size {len(text_bytes)} exceeds 1 MiB limit")
        text = raw

    decoder = json.JSONDecoder(
        object_pairs_hook=_strict_pairs_hook,
        parse_int=_strict_parse_int,
        parse_float=_strict_parse_float,
        parse_constant=_strict_parse_constant,
    )
    text_stripped = text.strip()
    if not text_stripped:
        raise MeasurementValidationError("Empty payload")

    obj, end_idx = decoder.raw_decode(text)
    trailing = text[end_idx:].strip()
    if trailing:
        raise MeasurementValidationError(f"Trailing non-whitespace data after JSON object: {trailing!r}")

    if not isinstance(obj, dict):
        raise MeasurementValidationError(f"Root JSON must be an object, got {type(obj).__name__}")

    return obj


# =========================================================================
# Canonical Serialization (P00 Steps 1-4)
# =========================================================================

def _escape_canonical_str(s: str) -> str:
    r"""Escape string per P00 canonicalization step 4.

    Escape only U+0022 as \", U+005C as \\, and U+0000..U+001F as \u00xx.
    Emit every other Unicode scalar as UTF-8 bytes.
    """
    parts = ['"']
    for ch in s:
        code = ord(ch)
        if ch == '"':
            parts.append(r'\"')
        elif ch == '\\':
            parts.append(r'\\')
        elif 0 <= code <= 0x1F:
            parts.append(f"\\u{code:04x}")
        else:
            parts.append(ch)
    parts.append('"')
    return "".join(parts)


def _serialize_canonical_value(val: Any) -> str:
    if val is None:
        return "null"
    if val is True:
        return "true"
    if val is False:
        return "false"
    if isinstance(val, int):
        return str(val)
    if isinstance(val, str):
        return _escape_canonical_str(val)
    if isinstance(val, list):
        return "[" + ",".join(_serialize_canonical_value(x) for x in val) + "]"
    if isinstance(val, dict):
        items = []
        for k in sorted(val.keys()):
            items.append(_escape_canonical_str(k) + ":" + _serialize_canonical_value(val[k]))
        return "{" + ",".join(items) + "}"
    raise MeasurementValidationError(f"Unsupported canonical serialization type: {type(val).__name__}")


def canonicalize_observation_json(data: Union[Dict[str, Any], bytes, str]) -> bytes:
    """Applies P00 Steps 1-4 deterministic canonicalization procedure.

    Returns compact UTF-8 bytes suitable for SHA-256 digest computation.
    """
    if isinstance(data, (bytes, str)):
        parsed = parse_strict_json(data)
    else:
        parsed = json.loads(json.dumps(data))  # deep copy

    # Step 4: remove event.canonical_digest
    if "event" in parsed and isinstance(parsed["event"], dict):
        parsed["event"].pop("canonical_digest", None)

    # Step 3: normalize timestamps
    if "capture" in parsed and isinstance(parsed["capture"], dict):
        if "captured_at_utc" in parsed["capture"] and isinstance(parsed["capture"]["captured_at_utc"], str):
            parsed["capture"]["captured_at_utc"] = normalize_rfc3339_timestamp(parsed["capture"]["captured_at_utc"])

    if "event" in parsed and isinstance(parsed["event"], dict):
        if "occurred_at_utc" in parsed["event"] and isinstance(parsed["event"]["occurred_at_utc"], str):
            parsed["event"]["occurred_at_utc"] = normalize_rfc3339_timestamp(parsed["event"]["occurred_at_utc"])

    serialized_str = _serialize_canonical_value(parsed)
    return serialized_str.encode("utf-8")


def compute_canonical_digest(data: Union[Dict[str, Any], bytes, str]) -> str:
    """Computes 64 lowercase hex SHA-256 digest over canonicalized bytes."""
    canon_bytes = canonicalize_observation_json(data)
    return hashlib.sha256(canon_bytes).hexdigest().lower()


# =========================================================================
# Validation (Dict & JSON)
# =========================================================================

def _check_allowed_and_sensitive(d: Dict[str, Any], allowed_keys: frozenset[str], context: str) -> None:
    for k in d.keys():
        if k in FORBIDDEN_SENSITIVE_KEYS:
            raise MeasurementPrivacyViolation(
                f"Forbidden sensitive key '{k}' in {context} violates measurement privacy contract"
            )
        if k not in allowed_keys:
            raise MeasurementValidationError(
                f"Unallowlisted key '{k}' in {context}; closed schema requires additionalProperties=false"
            )


def validate_observation_dict(
    data: Dict[str, Any],
    is_draft_fixture: bool = False,
) -> MeasurementObservation:
    """Validates dictionary against the P00 closed measurement observation schema and contracts."""
    _check_allowed_and_sensitive(data, ALLOWED_ROOT_KEYS, "root")

    for req in ("artifact_kind", "schema_version", "capture", "producer", "correlation", "event", "execution", "usage"):
        if req not in data:
            raise MeasurementValidationError(f"Missing required root field: '{req}'")

    if data["artifact_kind"] != CANONICAL_ARTIFACT_KIND:
        raise MeasurementValidationError(
            f"Invalid artifact_kind '{data['artifact_kind']}', expected '{CANONICAL_ARTIFACT_KIND}'"
        )
    if data["schema_version"] != CANONICAL_SCHEMA_VERSION:
        raise MeasurementValidationError(
            f"Invalid schema_version '{data['schema_version']}', expected '{CANONICAL_SCHEMA_VERSION}'"
        )

    # 1. Capture
    cap_data = data["capture"]
    if not isinstance(cap_data, dict):
        raise MeasurementValidationError("Field 'capture' must be an object")
    _check_allowed_and_sensitive(cap_data, ALLOWED_CAPTURE_KEYS, "capture")

    for req in ("method", "captured_at_utc", "source_runtime", "sanitization"):
        if req not in cap_data or not isinstance(cap_data[req], str) or not cap_data[req].strip():
            raise MeasurementValidationError(f"Field 'capture.{req}' must be a non-empty string")

    cap_version = cap_data.get("source_runtime_version")
    cap_ver_reason = cap_data.get("source_runtime_version_unavailable_reason")
    if cap_version is None:
        if not cap_ver_reason or not isinstance(cap_ver_reason, str) or not cap_ver_reason.strip():
            raise MeasurementValidationError(
                "source_runtime_version=null requires non-empty source_runtime_version_unavailable_reason"
            )
    elif isinstance(cap_version, str):
        if cap_ver_reason is not None:
            raise MeasurementValidationError(
                "source_runtime_version_unavailable_reason is prohibited when source_runtime_version is provided"
            )
    else:
        raise MeasurementValidationError("source_runtime_version must be string or null")

    capture = ObservationCapture(
        method=cap_data["method"],
        captured_at_utc=normalize_rfc3339_timestamp(cap_data["captured_at_utc"]),
        source_runtime=cap_data["source_runtime"],
        source_runtime_version=cap_version,
        source_runtime_version_unavailable_reason=cap_ver_reason,
        sanitization=cap_data["sanitization"],
    )

    # 2. Producer
    prod_data = data["producer"]
    if not isinstance(prod_data, dict):
        raise MeasurementValidationError("Field 'producer' must be an object")
    _check_allowed_and_sensitive(prod_data, ALLOWED_PRODUCER_KEYS, "producer")

    for req in ("namespace", "version"):
        if req not in prod_data or not isinstance(prod_data[req], str) or not prod_data[req].strip():
            raise MeasurementValidationError(f"Field 'producer.{req}' must be a non-empty string")

    fingerprint = prod_data.get("install_fingerprint")
    fp_reason = prod_data.get("install_fingerprint_unavailable_reason")
    if fingerprint is None:
        if not fp_reason or not isinstance(fp_reason, str) or not fp_reason.strip():
            raise MeasurementValidationError(
                "install_fingerprint=null requires non-empty install_fingerprint_unavailable_reason"
            )
    elif isinstance(fingerprint, str):
        if fp_reason is not None:
            raise MeasurementValidationError(
                "install_fingerprint_unavailable_reason is prohibited when install_fingerprint is provided"
            )
    else:
        raise MeasurementValidationError("install_fingerprint must be string or null")

    producer = ObservationProducer(
        namespace=prod_data["namespace"],
        version=prod_data["version"],
        install_fingerprint=fingerprint,
        install_fingerprint_unavailable_reason=fp_reason,
    )

    # 3. Correlation
    corr_data = data["correlation"]
    if not isinstance(corr_data, dict):
        raise MeasurementValidationError("Field 'correlation' must be an object")
    _check_allowed_and_sensitive(corr_data, ALLOWED_CORRELATION_KEYS, "correlation")

    for req in ("task_id", "task_generation_id", "run_id", "invocation_id", "attempt_id"):
        if req not in corr_data or not isinstance(corr_data[req], str) or not corr_data[req].strip():
            raise MeasurementValidationError(f"Field 'correlation.{req}' must be a non-empty string")

    transition_attempt_id = corr_data.get("transition_attempt_id")
    if transition_attempt_id is not None and (not isinstance(transition_attempt_id, str) or not transition_attempt_id.strip()):
        raise MeasurementValidationError("transition_attempt_id must be non-empty string or null")

    committed_transition_id = corr_data.get("committed_transition_id")
    if committed_transition_id is not None and (not isinstance(committed_transition_id, str) or not committed_transition_id.strip()):
        raise MeasurementValidationError("committed_transition_id must be non-empty string or null")

    correlation = ObservationCorrelation(
        task_id=corr_data["task_id"],
        task_generation_id=corr_data["task_generation_id"],
        run_id=corr_data["run_id"],
        invocation_id=corr_data["invocation_id"],
        attempt_id=corr_data["attempt_id"],
        transition_attempt_id=transition_attempt_id,
        committed_transition_id=committed_transition_id,
    )

    # 4. Event
    event_data = data["event"]
    if not isinstance(event_data, dict):
        raise MeasurementValidationError("Field 'event' must be an object")
    _check_allowed_and_sensitive(event_data, ALLOWED_EVENT_KEYS, "event")

    for req in ("event_id", "occurred_at_utc", "coverage_state"):
        if req not in event_data or not isinstance(event_data[req], str) or not event_data[req].strip():
            raise MeasurementValidationError(f"Field 'event.{req}' must be a non-empty string")

    cov_state = event_data["coverage_state"]
    valid_states = {s.value for s in CoverageState}
    if cov_state not in valid_states:
        raise MeasurementValidationError(f"Invalid coverage_state '{cov_state}', allowed: {sorted(valid_states)}")

    occurred_at = normalize_rfc3339_timestamp(event_data["occurred_at_utc"])

    digest = event_data.get("canonical_digest")
    digest_reason = event_data.get("canonical_digest_unavailable_reason")

    if is_draft_fixture and digest is None:
        if not digest_reason or not isinstance(digest_reason, str) or not digest_reason.strip():
            raise MeasurementValidationError(
                "Draft fixture with canonical_digest=null requires non-empty canonical_digest_unavailable_reason"
            )
    else:
        if not digest or not isinstance(digest, str) or len(digest) != 64:
            raise MeasurementValidationError(
                "Production canonical_digest must be a 64-character lowercase hex SHA-256 string"
            )
        if digest_reason is not None:
            raise MeasurementValidationError(
                "canonical_digest_unavailable_reason is prohibited when canonical_digest is provided"
            )

    event = ObservationEvent(
        event_id=event_data["event_id"],
        occurred_at_utc=occurred_at,
        coverage_state=cov_state,
        canonical_digest=digest,
        canonical_digest_unavailable_reason=digest_reason,
        causal_parent_event_id=event_data.get("causal_parent_event_id"),
    )

    # 5. Execution
    exec_data = data["execution"]
    if not isinstance(exec_data, dict):
        raise MeasurementValidationError("Field 'execution' must be an object")
    _check_allowed_and_sensitive(exec_data, ALLOWED_EXECUTION_KEYS, "execution")

    for req in ("exit_code", "duration_ms", "duration_provenance", "requested_model"):
        if req not in exec_data:
            raise MeasurementValidationError(f"Missing required execution field: '{req}'")

    exit_code = exec_data["exit_code"]
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        raise MeasurementValidationError("exit_code must be an integer")

    duration_ms = exec_data["duration_ms"]
    if not isinstance(duration_ms, int) or isinstance(duration_ms, bool) or duration_ms < 0:
        raise MeasurementValidationError("duration_ms must be a non-negative integer")

    dur_prov = exec_data["duration_provenance"]
    valid_dur_prov = {p.value for p in DurationProvenance}
    if dur_prov not in valid_dur_prov:
        raise MeasurementValidationError(f"Invalid duration_provenance '{dur_prov}', allowed: {sorted(valid_dur_prov)}")
    if dur_prov == DurationProvenance.SYNTHETIC_FIXTURE.value:
        if not is_draft_fixture and "fixture" not in cap_data.get("method", "").lower():
            raise MeasurementValidationError(
                "synthetic_fixture duration_provenance is permitted only for draft fixtures"
            )

    req_model = exec_data["requested_model"]
    if not isinstance(req_model, str) or not req_model.strip():
        raise MeasurementValidationError("requested_model must be a non-empty string")

    obs_model = exec_data.get("observed_model")
    obs_model_reason = exec_data.get("observed_model_unavailable_reason")
    if obs_model is None:
        if not obs_model_reason or not isinstance(obs_model_reason, str) or not obs_model_reason.strip():
            raise MeasurementValidationError(
                "observed_model=null requires non-empty observed_model_unavailable_reason"
            )
    elif isinstance(obs_model, str):
        if obs_model_reason is not None:
            raise MeasurementValidationError(
                "observed_model_unavailable_reason is prohibited when observed_model is provided"
            )
    else:
        raise MeasurementValidationError("observed_model must be string or null")

    execution = ObservationExecution(
        exit_code=exit_code,
        duration_ms=duration_ms,
        duration_provenance=dur_prov,
        requested_model=req_model,
        observed_model=obs_model,
        observed_model_unavailable_reason=obs_model_reason,
    )

    # 6. Usage
    usage_data = data["usage"]
    if not isinstance(usage_data, dict):
        raise MeasurementValidationError("Field 'usage' must be an object")
    _check_allowed_and_sensitive(usage_data, ALLOWED_USAGE_KEYS, "usage")

    if "provenance" not in usage_data:
        raise MeasurementValidationError("Missing required usage field: 'provenance'")

    usage_prov = usage_data["provenance"]
    valid_usage_prov = {p.value for p in MetricProvenance}
    if usage_prov not in valid_usage_prov:
        raise MeasurementValidationError(f"Invalid usage provenance '{usage_prov}', allowed: {sorted(valid_usage_prov)}")

    token_fields = ("input_tokens", "output_tokens", "cached_tokens", "reasoning_tokens")
    token_vals: Dict[str, Optional[int]] = {}
    has_null_token = False

    for tf in token_fields:
        val = usage_data.get(tf)
        if val is None:
            has_null_token = True
            token_vals[tf] = None
        elif isinstance(val, int) and not isinstance(val, bool):
            if val < 0:
                raise MeasurementValidationError(f"Token count '{tf}' cannot be negative: {val}")
            token_vals[tf] = val
        else:
            raise MeasurementValidationError(f"Token field '{tf}' must be non-negative integer or null")

    usage_reason = usage_data.get("unavailable_reason")

    if usage_prov == MetricProvenance.UNAVAILABLE.value:
        if any(token_vals[tf] is not None for tf in token_fields):
            raise MeasurementValidationError(
                "usage.provenance='unavailable' requires all token fields null"
            )
        if not usage_reason or not isinstance(usage_reason, str) or not usage_reason.strip():
            raise MeasurementValidationError(
                "usage.provenance='unavailable' requires non-empty unavailable_reason"
            )
    else:
        if has_null_token:
            if not usage_reason or not isinstance(usage_reason, str) or not usage_reason.strip():
                raise MeasurementValidationError(
                    "Missing or null token field requires non-empty unavailable_reason"
                )
        else:
            if usage_reason is not None:
                raise MeasurementValidationError(
                    "unavailable_reason is prohibited when all token fields are recorded integers"
                )

    usage = ObservationUsage(
        provenance=usage_prov,
        input_tokens=token_vals["input_tokens"],
        output_tokens=token_vals["output_tokens"],
        cached_tokens=token_vals["cached_tokens"],
        reasoning_tokens=token_vals["reasoning_tokens"],
        unavailable_reason=usage_reason,
        scope=usage_data.get("scope"),
    )

    # Digest integrity check comes after all content validations so content errors take precedence
    if not is_draft_fixture and digest is not None:
        try:
            expected_digest = compute_canonical_digest(data)
        except MeasurementValidationError:
            expected_digest = None
        if expected_digest is not None and digest != expected_digest:
            raise MeasurementValidationError(
                f"canonical_digest mismatch (artifact_invalid): provided '{digest}' != computed '{expected_digest}'"
            )

    return MeasurementObservation(
        artifact_kind=data["artifact_kind"],
        schema_version=data["schema_version"],
        capture=capture,
        producer=producer,
        correlation=correlation,
        event=event,
        execution=execution,
        usage=usage,
    )


def validate_observation_json(
    raw: Union[bytes, str],
    is_draft_fixture: bool = False,
) -> MeasurementObservation:
    """Parses strict JSON and validates against measurement schema."""
    obj = parse_strict_json(raw)
    return validate_observation_dict(obj, is_draft_fixture=is_draft_fixture)


# =========================================================================
# Settlement & Aggregation
# =========================================================================

def settle_observations(
    observations: Sequence[MeasurementObservation],
    scope: Optional[ObservationScope] = None,
    distinct_execution_attempts: bool = False,
) -> SettlementResult:
    """Settles and aggregates a collection of observations.

    Rules:
    - Same canonical key (namespace, schema_version, event_id) and same digest:
      idempotent redelivery (no-op duplicate).
    - Same canonical key and DIFFERENT digest:
      integrity conflict (ambiguous), fails settlement.
    - Reused attempt_id across executions (when distinct_execution_attempts=True):
      rejected as duplicate execution attempt.
    - Incompatible scopes/sources: preserved as unsettled without inventing totals.
    - Cumulative scope: final supersedes earlier snapshot observations for aggregate totals.
    - Corrections: causal_parent_event_id links to target and supersedes it for active totals.
    - Non-additive subset integrity: cached_tokens is a subset of input; reasoning_tokens
      is a subset of output; never add them into an invented total.
    """
    if not observations:
        return SettlementResult(
            status="empty",
            observations=[],
            duplicate_count=0,
            is_settled=True,
        )

    seen_keys: Dict[Tuple[str, str, str], MeasurementObservation] = {}
    seen_attempt_events: Dict[str, str] = {}
    retained_observations: List[MeasurementObservation] = []
    duplicate_count = 0

    scopes_present = set()
    for obs in observations:
        k = obs.canonical_key
        if obs.usage.scope:
            scopes_present.add(obs.usage.scope)

        # Check distinct execution attempts
        if distinct_execution_attempts:
            att = obs.correlation.attempt_id
            if att in seen_attempt_events and seen_attempt_events[att] != obs.event.event_id:
                raise MeasurementSettlementConflict(
                    f"Illegal reused attempt_id '{att}' across distinct executions "
                    f"({seen_attempt_events[att]} and {obs.event.event_id})"
                )
            seen_attempt_events[att] = obs.event.event_id

        # Check redelivery idempotency vs conflict
        if k in seen_keys:
            existing = seen_keys[k]
            if existing.event.canonical_digest == obs.event.canonical_digest:
                duplicate_count += 1
                continue
            else:
                raise MeasurementSettlementConflict(
                    f"Ambiguous redelivery conflict for event '{obs.event.event_id}': "
                    f"existing digest '{existing.event.canonical_digest}' != new digest '{obs.event.canonical_digest}'"
                )

        seen_keys[k] = obs
        retained_observations.append(obs)

    # Check scope compatibility
    if len(scopes_present) > 1:
        if scopes_present - {"snapshot", "final", "correction"} != set():
            # Incompatible combination like cumulative + delta
            return SettlementResult(
                status="unsettled",
                observations=retained_observations,
                duplicate_count=duplicate_count,
                is_settled=False,
                unsettled_reason=f"Incompatible measurement scopes: {' vs '.join(sorted(scopes_present))}",
            )

    # Apply precedence and corrections
    final_obs = next((o for o in retained_observations if o.usage.scope == "final"), None)
    corrections = {
        o.event.causal_parent_event_id: o
        for o in retained_observations
        if o.usage.scope == "correction" and o.event.causal_parent_event_id
    }

    if final_obs is not None:
        active_obs = [final_obs]
    else:
        active_obs = []
        for o in retained_observations:
            if o.usage.scope == "correction":
                active_obs.append(o)
            elif o.event.event_id in corrections:
                continue  # Superseded by correction
            else:
                active_obs.append(o)

    total_input = 0
    total_output = 0
    cached_subset = 0
    reasoning_subset = 0
    any_input_null = False
    any_output_null = False

    for o in active_obs:
        if o.usage.input_tokens is not None:
            total_input += o.usage.input_tokens
        else:
            any_input_null = True

        if o.usage.output_tokens is not None:
            total_output += o.usage.output_tokens
        else:
            any_output_null = True

        if o.usage.cached_tokens is not None:
            cached_subset += o.usage.cached_tokens

        if o.usage.reasoning_tokens is not None:
            reasoning_subset += o.usage.reasoning_tokens

    return SettlementResult(
        status="observed",
        observations=retained_observations,
        total_input_tokens=None if any_input_null and not active_obs else total_input,
        total_output_tokens=None if any_output_null and not active_obs else total_output,
        cached_tokens_subset=cached_subset,
        reasoning_tokens_subset=reasoning_subset,
        invented_aggregate_tokens=None,  # Never invent additive totals of subsets
        duplicate_count=duplicate_count,
        is_settled=True,
    )
