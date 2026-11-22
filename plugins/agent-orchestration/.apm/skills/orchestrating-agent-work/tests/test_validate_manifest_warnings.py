"""Advisory planning warnings of validate_manifest.py: never errors, never change the exit code."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_manifest import advisory_warnings  # noqa: E402

VALIDATOR = SCRIPTS / "validate_manifest.py"
BUDGET = {"token_ceiling_total": 10000, "max_parallel_concurrency": 3, "max_retries_per_node": 1}


def _node(nid, ntype, deps=(), **extra):
    node = {"id": nid, "type": ntype, "tier": "deterministic_script", "command_or_eval": "true",
            "input_bindings": list(deps), "output_contract": {"type": "exit_code", "equals": 0},
            "depends_on": list(deps), "failure_escalation": "rollback_and_halt"}
    if ntype == "sequential_mutation":
        node["mutation_targets"] = [f"{nid}.txt"]
    node.update(extra)
    return node


def _serial_chain(n=3, caller=None):
    nodes, prev = [], []
    for i in range(n):
        nodes.append(_node(f"m{i}", "sequential_mutation", prev))
        prev = [f"m{i}"]
    manifest = {"schema_version": "1.0.0", "graph_id": "serial-chain", "version": "1.0.0", "budget": BUDGET, "nodes": nodes}
    if caller is not None:
        manifest["caller"] = caller
    return manifest


def _with_fan_out():
    nodes = [_node("r1", "parallel_read"), _node("r2", "parallel_read"),
             _node("join", "sync_barrier", ["r1", "r2"]),
             _node("m0", "sequential_mutation", ["join"]), _node("m1", "sequential_mutation", ["m0"]),
             _node("m2", "sequential_mutation", ["m1"])]
    return {"schema_version": "1.0.0", "graph_id": "fan-out", "version": "1.0.0", "budget": BUDGET,
            "caller": {"planning_notes": "two independent scans, then ordered edits"}, "nodes": nodes}


def test_serial_chain_of_three_warns_about_missing_parallel_branches():
    warnings = advisory_warnings(_serial_chain(3))
    assert any("3 sequential mutations and 0 parallel branches" in w for w in warnings)


def test_missing_planning_notes_warns():
    warnings = advisory_warnings(_serial_chain(3, caller={"note": "x"}))
    assert any("no caller.planning_notes" in w for w in warnings)


def test_planning_notes_silence_the_notes_warning():
    warnings = advisory_warnings(_serial_chain(3, caller={"planning_notes": "serial on purpose: shared files"}))
    assert not any("planning_notes" in w for w in warnings)


def test_graph_with_fan_out_and_notes_has_no_warnings():
    assert advisory_warnings(_with_fan_out()) == []


def test_two_dependent_reads_are_not_fan_out():
    manifest = _serial_chain(3)
    manifest["nodes"] += [_node("r1", "parallel_read"), _node("r2", "parallel_read", ["r1"])]
    assert any("0 parallel branches" in w for w in advisory_warnings(manifest))


def test_fewer_than_three_mutations_never_warn():
    assert advisory_warnings(_serial_chain(2)) == []


def _validate(tmp_path, manifest):
    path = tmp_path / "graph-manifest.json"
    path.write_text(json.dumps(manifest))
    return subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True)


def test_warnings_are_printed_but_do_not_change_the_exit_code(tmp_path):
    result = _validate(tmp_path, _serial_chain(3))
    assert result.returncode == 0
    assert "PASS:" in result.stdout
    assert "WARNING:" in result.stdout


def test_clean_graph_prints_no_warning(tmp_path):
    result = _validate(tmp_path, _with_fan_out())
    assert result.returncode == 0
    assert "WARNING:" not in result.stdout
