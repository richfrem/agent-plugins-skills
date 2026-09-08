"""
test_control_plane_model_catalog_adapter.py — Model-Catalog Extraction (issue-524, Step 7)
===============================================================================================

Purpose:
    Unit tests for control_plane/adapters.py's ModelCatalogAdapter in isolation, plus an
    integration test proving ControlPlane.resolve_recommended_model() delegates the full
    resolution to the injected ModelCatalogPort (issue-524, post-round-3-review correction:
    the port now covers tool-alias/tier-strategy/fallback logic, not just JSON file reads).

Key Input Dependencies:
    - Temporary JSON files via pytest's tmp_path fixture
    - Real plugins/cli-agents/references/ files (for the genuine end-to-end test)

Key Functions:
    - test_load_catalog_returns_none_when_missing()
    - test_load_catalog_returns_parsed_dict_when_present()
    - test_load_catalog_returns_none_on_malformed_json()
    - test_load_cheapest_returns_none_when_missing()
    - test_load_cheapest_returns_model_for_tool_key()
    - test_control_plane_uses_injected_model_catalog_port()
    - test_model_catalog_adapter_helper_components_against_temp_files()
    - test_model_catalog_adapter_resolve_recommended_model_against_real_repo_files()
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.adapters import ModelCatalogAdapter
from control_plane.ports import ModelCatalogPort
from agent_control import ControlPlane


def test_load_catalog_returns_none_when_missing(tmp_path):
    adapter = ModelCatalogAdapter()
    assert adapter.load_catalog(tmp_path / "nonexistent.json") is None


def test_load_catalog_returns_parsed_dict_when_present(tmp_path):
    catalog_file = tmp_path / "copilot-models.json"
    catalog_file.write_text(json.dumps({"strategy": {"default": "gpt-5-mini"}}), encoding="utf-8")
    adapter = ModelCatalogAdapter()
    result = adapter.load_catalog(catalog_file)
    assert result == {"strategy": {"default": "gpt-5-mini"}}


def test_load_catalog_returns_none_on_malformed_json(tmp_path):
    catalog_file = tmp_path / "broken.json"
    catalog_file.write_text("{not valid json", encoding="utf-8")
    adapter = ModelCatalogAdapter()
    assert adapter.load_catalog(catalog_file) is None


def test_load_cheapest_returns_none_when_missing(tmp_path):
    adapter = ModelCatalogAdapter()
    assert adapter.load_cheapest(tmp_path / "cheapest_models.json", "copilot") is None


def test_load_cheapest_returns_model_for_tool_key(tmp_path):
    cheapest_file = tmp_path / "cheapest_models.json"
    cheapest_file.write_text(json.dumps({"copilot": {"model": "gpt-5.4-nano"}}), encoding="utf-8")
    adapter = ModelCatalogAdapter()
    assert adapter.load_cheapest(cheapest_file, "copilot") == "gpt-5.4-nano"
    assert adapter.load_cheapest(cheapest_file, "claude") is None


class _RecordingModelCatalogPort(ModelCatalogPort):
    """Test double recording every call instead of touching real files. Implements
    resolve_recommended_model() directly (issue-524, post-round-2-review correction: the
    port's resolution responsibility is no longer just file reads) — returns a scripted
    result so the test can assert ControlPlane delegated to it wholesale."""

    def __init__(self, resolved_result=None, catalog_data=None, cheapest_model=None):
        self._resolved_result = resolved_result
        self._catalog_data = catalog_data
        self._cheapest_model = cheapest_model
        self.resolve_calls = []
        self.catalog_calls = []
        self.cheapest_calls = []

    def resolve_recommended_model(self, runtime_tool: str, tier: str = "low") -> Dict[str, str]:
        self.resolve_calls.append((runtime_tool, tier))
        return self._resolved_result

    def load_catalog(self, catalog_path: Path) -> Optional[Dict[str, Any]]:
        self.catalog_calls.append(catalog_path)
        return self._catalog_data

    def load_cheapest(self, cheapest_path: Path, tool_key: str) -> Optional[str]:
        self.cheapest_calls.append((cheapest_path, tool_key))
        return self._cheapest_model


def test_control_plane_uses_injected_model_catalog_port(tmp_path):
    """Integration: resolve_recommended_model() calls the injected ModelCatalogPort's
    resolve_recommended_model() wholesale, not inline tool-alias/tier-strategy logic —
    proves ControlPlane.resolve_recommended_model() is a pure delegate (issue-524,
    post-round-2-review correction)."""
    recorder = _RecordingModelCatalogPort(
        resolved_result={"runtime_tool": "copilot", "tier": "medium", "model_id": "recorded-model"},
    )
    cp = ControlPlane(db_path=tmp_path / "control_plane.db", model_catalog_adapter=recorder)

    result = cp.resolve_recommended_model(runtime_tool="copilot", tier="medium")

    assert recorder.resolve_calls == [("copilot", "medium")]
    assert result["model_id"] == "recorded-model"


def test_model_catalog_adapter_helper_components_against_temp_files(tmp_path):
    """Unit test of ModelCatalogAdapter's relocated HELPER components (_resolve_tool_catalog,
    load_cheapest, load_catalog, _pick_tier_model) against temp-directory JSON files —
    exercises each piece of the tool-alias/tier-strategy/fallback logic individually. This
    does NOT call the public resolve_recommended_model() method itself (that method's
    repo-root discovery is derived from this adapter module's own __file__ location, so it
    cannot be pointed at an arbitrary tmp_path without either monkeypatching __file__ or
    adding a repo-root override parameter to the adapter — neither of which this test does).
    See test_model_catalog_adapter_resolve_recommended_model_against_real_repo_files below
    for a genuine end-to-end call of the public method. Renamed after external review round 3
    correctly flagged the original name/docstring ("end_to_end") as overstating what this
    test actually proves."""
    cli_refs = tmp_path / "plugins" / "cli-agents" / "references"
    cli_refs.mkdir(parents=True)
    (cli_refs / "copilot-models.json").write_text(json.dumps({
        "_meta": {"schema_version": 2},
        "runtime": {
            "runtime_id": "copilot",
            "provider": "GitHub",
            "availability": "available",
            "native_capabilities": {"planning": "unknown", "worktree": "portable", "subagents": "unknown"},
            "effort_modes": ["low", "medium", "high"],
        },
        "models": [
            {"cli_id": "gpt-5-mini", "status": "GA", "context_window_k": 1, "max_output_k": None, "tool_support": {"prompt": True}, "pricing_usd_per_1m": {"input": 0.25, "output": 2.0}},
            {"cli_id": "gpt-5.4-nano", "status": "GA", "context_window_k": 1, "max_output_k": None, "tool_support": {"prompt": True}, "pricing_usd_per_1m": {"input": 0.2, "output": 1.25}},
        ],
        "capability_tiers": {"low": ["gpt-5.4-nano", "gpt-5-mini"], "medium": ["gpt-5-mini"], "high": ["gpt-5-mini"]},
        "strategy": {"default": "gpt-5-mini", "heartbeat": "gpt-5.4-nano"},
    }), encoding="utf-8")
    (cli_refs / "cheapest_models.json").write_text(
        json.dumps({"copilot": {"model": "gpt-5.4-nano"}}), encoding="utf-8"
    )

    adapter = ModelCatalogAdapter()
    tool_key, catalog_file = adapter._resolve_tool_catalog("copilot", cli_refs)
    assert tool_key == "copilot"
    assert catalog_file == cli_refs / "copilot-models.json"

    cheapest = adapter.load_cheapest(cli_refs / "cheapest_models.json", tool_key)
    assert cheapest == "gpt-5.4-nano"

    cat_data = adapter.load_catalog(catalog_file)
    picked = adapter._pick_tier_model(cat_data, "low", cheapest)
    assert picked == "gpt-5.4-nano"


def test_model_catalog_adapter_resolve_recommended_model_against_real_repo_files():
    """Genuine end-to-end call of the PUBLIC resolve_recommended_model() method, against the
    real plugins/cli-agents/references/ files in this repo (the same files
    ControlPlane.resolve_recommended_model() resolves against in production) — proves the
    complete, real code path works, not just its individual helper pieces."""
    adapter = ModelCatalogAdapter()
    result = adapter.resolve_recommended_model(runtime_tool="copilot", tier="low")
    assert result["runtime_tool"] == "copilot"
    assert result["tier"] == "low"
    assert result["model_id"]  # some non-empty model id was resolved (real catalog or fallback)


def test_control_plane_defaults_to_real_model_catalog_adapter(tmp_path):
    """When no model_catalog_adapter is passed, ControlPlane wires a real ModelCatalogAdapter."""
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    assert isinstance(cp._model_catalog, ModelCatalogAdapter)
