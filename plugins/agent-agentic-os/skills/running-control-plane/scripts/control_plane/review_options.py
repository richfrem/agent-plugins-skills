#!/usr/bin/env python3
"""
control_plane/review_options.py
===============================

Purpose:
    Read-only helper for the `list-review-options` verb (auth-ciba-increment-b H1, issue #639). The review-
    selection questions take the runtime, model and effort as typed text; this prints the exact identifiers
    an installed CLI reports so the human copies them instead of remembering or mistyping them. Each CLI is
    probed through ITS OWN `models` command (no runtime dependency on the cli-agents catalog, per the plugin
    loose-coupling rule). A runtime with no known probe is listed as "installed, no model probe". Nothing is
    written and nothing is inferred: a missing CLI or a failing probe is reported as such.

Key Input Dependencies:
    - The runtime CLIs on PATH (currently `agy models` is probed); optional context/agent-capability-profile.json
      (mentioned, not required or parsed)

Key Functions:
    - collect_review_options() -- probe the runtimes and return a list of result dicts
    - format_review_options()  -- render the results as text for the terminal
    - choices_for()            -- menu items (runtime | model | effort) for the review-selection questions
    - ChoiceSet                -- items plus an optional warning when no menu could be built

Constants:
    - RUNTIME_PROBES, EFFORT_LEVELS, PROBE_TIMEOUT_SECONDS, PROFILE_RELATIVE_PATH, VERIFIED_EFFORTS
"""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# runtime name -> argv of its own model-listing command (None: installed but no probe implemented here)
RUNTIME_PROBES: Dict[str, Optional[List[str]]] = {
    "agy": ["agy", "models"],
    "claude": None,
    "codex": None,
    "copilot": None,
}
EFFORT_LEVELS = ("low", "medium", "high")
PROBE_TIMEOUT_SECONDS = 20
PROFILE_RELATIVE_PATH = "context/agent-capability-profile.json"
# Effort levels verified from the runtime's own help (`agy --help`: --effort low|medium|high); other
# runtimes are not listed here because nothing verifies them, so their effort question is free text + warning.
VERIFIED_EFFORTS: Dict[str, tuple] = {"agy": ("low", "medium", "high")}


def _parse_models(stdout: str) -> List[Dict[str, str]]:
    """Model rows are `<id>\\t<display name>`; header/progress lines without a tab are ignored."""
    models = []
    for line in stdout.splitlines():
        if "\t" not in line:
            continue
        model_id, _, display = line.partition("\t")
        if model_id.strip():
            models.append({"id": model_id.strip(), "display": display.strip()})
    return models


def collect_review_options(path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Probe each known runtime. `path` overrides PATH for lookup and execution (used by tests)."""
    results: List[Dict[str, Any]] = []
    for runtime, argv in RUNTIME_PROBES.items():
        binary = shutil.which(runtime, path=path)
        if binary is None:
            results.append({"runtime": runtime, "status": "not_found"})
            continue
        if argv is None:
            results.append({"runtime": runtime, "status": "no_probe", "binary": binary})
            continue
        try:
            done = subprocess.run([binary] + argv[1:], capture_output=True, text=True, timeout=PROBE_TIMEOUT_SECONDS, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            results.append({"runtime": runtime, "status": "probe_failed", "binary": binary, "detail": str(exc)})
            continue
        if done.returncode != 0:
            results.append({"runtime": runtime, "status": "probe_failed", "binary": binary, "detail": f"exit {done.returncode}"})
            continue
        results.append({"runtime": runtime, "status": "ok", "binary": binary, "models": _parse_models(done.stdout)})
    return results


def format_review_options(results: List[Dict[str, Any]]) -> str:
    """Render the probe results; the human copies the identifiers exactly when a review question asks."""
    lines = ["Review options (read-only; copy the identifiers below exactly when the review questions ask):", ""]
    for item in results:
        name = item["runtime"]
        if item["status"] == "not_found":
            lines.append(f"runtime {name}: not found on PATH")
        elif item["status"] == "no_probe":
            lines.append(f"runtime {name}: installed at {item['binary']} (no model probe here; use that CLI's own model list)")
        elif item["status"] == "probe_failed":
            lines.append(f"runtime {name}: probe failed ({item['detail']}); models not listed")
        else:
            lines.append(f"runtime {name}: installed at {item['binary']}")
            lines.append("  model ids:")
            lines.extend(f"    {m['id']}    {m['display']}" for m in item["models"]) if item["models"] else lines.append("    (none reported)")
    lines += ["", "effort levels: " + ", ".join(EFFORT_LEVELS),
              "Type the runtime, then the model id, then the effort at the three review questions; the model id often already includes the effort.",
              "A capability profile at context/agent-capability-profile.json, when present, is the project's own record of approved choices."]
    return "\n".join(lines)


@dataclass
class ChoiceSet:
    """Menu items for a review-selection question. `items` empty + `warning` means free text is allowed
    and the answer cannot be validated; `installed` False items are shown but not selectable."""

    items: List[Dict[str, Any]] = field(default_factory=list)
    warning: Optional[str] = None


def default_profile_path() -> Path:
    """The capability profile at the shared (canonical) repository root, like the identity folder."""
    from control_plane.identity_layout import canonical_repo_root

    return canonical_repo_root(".") / PROFILE_RELATIVE_PATH


def _profile_models(runtime: str, profile_path: Optional[Path]) -> List[str]:
    """Model ids the capability profile records for a runtime (`providers.<runtime>.model_tiers`), if any."""
    path = Path(profile_path) if profile_path else default_profile_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        tiers = data["providers"][runtime]["model_tiers"]
    except (OSError, ValueError, KeyError, TypeError):
        return []
    ids: List[str] = []
    for value in tiers.values() if isinstance(tiers, dict) else []:
        if isinstance(value, str) and value and value not in ids:
            ids.append(value)
    return ids


def choices_for(kind: str, runtime: Optional[str] = None, path: Optional[str] = None,
                profile_path: Optional[Path] = None) -> ChoiceSet:
    """Build the menu for one review-selection question. Never guesses: a runtime or model that no probe
    or profile confirms yields an empty ChoiceSet with a warning, so the human is told the answer is unchecked."""
    if kind == "runtime":
        items = [{"id": name, "display": name, "installed": shutil.which(name, path=path) is not None} for name in RUNTIME_PROBES]
        if not any(i["installed"] for i in items):
            return ChoiceSet([], "no supported CLI (codex, claude, agy, copilot) was found on PATH; the answer cannot be validated")
        return ChoiceSet(items)
    if kind == "model":
        if runtime in RUNTIME_PROBES and RUNTIME_PROBES[runtime] is not None:
            probed = next((r for r in collect_review_options(path=path) if r["runtime"] == runtime), None)
            if probed and probed["status"] == "ok" and probed["models"]:
                return ChoiceSet([{"id": m["id"], "display": m["display"], "installed": True} for m in probed["models"]])
        ids = _profile_models(runtime or "", profile_path)
        if ids:
            return ChoiceSet([{"id": i, "display": i, "installed": True} for i in ids])
        return ChoiceSet([], f"no model list is available for '{runtime}' (no probe, no capability profile entry); the answer cannot be validated")
    if kind == "effort":
        levels = VERIFIED_EFFORTS.get(runtime or "")
        if levels:
            return ChoiceSet([{"id": lv, "display": lv, "installed": True} for lv in levels])
        return ChoiceSet([], f"effort levels for '{runtime}' are not verified; the answer cannot be validated")
    raise ValueError(f"unknown choices kind: {kind}")
