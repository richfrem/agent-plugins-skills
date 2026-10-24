#!/usr/bin/env python3
"""
Unit tests for validate_manifest.py
Validates:
- JSON schema enforcement (additionalProperties: false, schema_version)
- DAG acyclicity & topological sort
- Total ordering of sequential mutations
- Read-only DAG acceptance
- Leading approval gate semantics for --check-approval-none
- Fallback node reference integrity (no self-fallback, no cycles, no primary depending on fallback)
- Strict stdlib fallback validation when jsonschema is absent
"""

import json
import os
import sys
import unittest
from pathlib import Path

PLUGIN_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(PLUGIN_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PLUGIN_SCRIPTS))

from validate_manifest import (
    load_schema,
    validate_schema,
    validate_schema_fallback,
    validate_graph_topology
)


class TestValidateManifest(unittest.TestCase):

    def setUp(self):
        self.schema = load_schema()
        self.assertIsNotNone(self.schema, "Failed to load graph-manifest-schema.json")

    def _make_manifest(self, nodes, graph_id="test-graph", budget=None, caller=None):
        manifest = {
            "schema_version": "1.0.0",
            "graph_id": graph_id,
            "version": "1.0.0",
            "budget": budget or {
                "token_ceiling_total": 50000,
                "max_parallel_concurrency": 4,
                "max_retries_per_node": 2
            },
            "nodes": nodes
        }
        if caller is not None:
            manifest["caller"] = caller
        return manifest

    def test_valid_minimal_graph(self):
        nodes = [
            {
                "id": "node-1",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo scan",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "node-2",
                "type": "sync_barrier",
                "tier": "deterministic_script",
                "command_or_eval": "echo barrier",
                "input_bindings": ["node-1"],
                "output_contract": "barrier.json",
                "depends_on": ["node-1"],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        schema_errs = validate_schema(manifest, self.schema)
        topo_errs = validate_graph_topology(manifest)
        self.assertEqual(schema_errs, [])
        self.assertEqual(topo_errs, [])

    def test_cycle_detection(self):
        nodes = [
            {
                "id": "node-a",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo a",
                "input_bindings": [],
                "output_contract": "a.json",
                "depends_on": ["node-b"],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "node-b",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo b",
                "input_bindings": [],
                "output_contract": "b.json",
                "depends_on": ["node-a"],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("Cyclic dependency" in err for err in topo_errs))

    def test_duplicate_node_ids(self):
        nodes = [
            {
                "id": "dup-id",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo 1",
                "input_bindings": [],
                "output_contract": "1.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "dup-id",
                "type": "sync_barrier",
                "tier": "deterministic_script",
                "command_or_eval": "echo 2",
                "input_bindings": [],
                "output_contract": "2.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("Duplicate node ID" in err for err in topo_errs))

    def test_unknown_depends_on(self):
        nodes = [
            {
                "id": "node-1",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo 1",
                "input_bindings": [],
                "output_contract": "1.json",
                "depends_on": ["non-existent-node"],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("unknown node" in err for err in topo_errs))

    def test_concurrent_mutations_rejected(self):
        nodes = [
            {
                "id": "mut-1",
                "type": "sequential_mutation",
                "tier": "frontier_engine",
                "command_or_eval": "touch a.txt",
                "mutation_targets": ["a.txt"],
                "input_bindings": [],
                "output_contract": "a.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "mut-2",
                "type": "sequential_mutation",
                "tier": "frontier_engine",
                "command_or_eval": "touch b.txt",
                "mutation_targets": ["b.txt"],
                "input_bindings": [],
                "output_contract": "b.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("Mutation total ordering violation" in err for err in topo_errs))

    def test_readonly_dag_accepted(self):
        nodes = [
            {
                "id": "read-1",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "cat file1.md",
                "input_bindings": [],
                "output_contract": "r1.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "read-2",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "cat file2.md",
                "input_bindings": [],
                "output_contract": "r2.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "barrier",
                "type": "sync_barrier",
                "tier": "deterministic_script",
                "command_or_eval": "echo joined",
                "input_bindings": ["read-1", "read-2"],
                "output_contract": "b.json",
                "depends_on": ["read-1", "read-2"],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        schema_errs = validate_schema(manifest, self.schema)
        topo_errs = validate_graph_topology(manifest)
        self.assertEqual(schema_errs, [])
        self.assertEqual(topo_errs, [])

    def test_additional_properties_rejected(self):
        manifest = self._make_manifest([])
        manifest["unauthorized_top_level_key"] = "bad"
        schema_errs = validate_schema(manifest, self.schema)
        self.assertTrue(any("unauthorized_top_level_key" in err for err in schema_errs))

    def test_approval_none_without_leading_gate_rejected(self):
        nodes = [
            {
                "id": "mut-1",
                "type": "sequential_mutation",
                "tier": "frontier_engine",
                "command_or_eval": "touch a.txt",
                "mutation_targets": ["a.txt"],
                "input_bindings": [],
                "output_contract": "a.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest, check_approval_none=True)
        self.assertTrue(any("Approval gate violation" in err for err in topo_errs))

    def test_approval_none_with_leading_gate_accepted(self):
        nodes = [
            {
                "id": "gate-approval",
                "role": "approval",
                "type": "verifier_gate",
                "tier": "deterministic_script",
                "command_or_eval": "true",
                "input_bindings": [],
                "output_contract": "app.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "mut-1",
                "type": "sequential_mutation",
                "tier": "frontier_engine",
                "command_or_eval": "touch a.txt",
                "mutation_targets": ["a.txt"],
                "input_bindings": ["gate-approval"],
                "output_contract": "a.json",
                "depends_on": ["gate-approval"],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        schema_errs = validate_schema(manifest, self.schema)
        topo_errs = validate_graph_topology(manifest, check_approval_none=True)
        self.assertEqual(schema_errs, [])
        self.assertEqual(topo_errs, [])

    def test_self_fallback_rejected(self):
        nodes = [
            {
                "id": "node-1",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo scan",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "fallback_node",
                "fallback_node_id": "node-1"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("Self-fallback detected" in err for err in topo_errs))

    def test_primary_depending_on_fallback_rejected(self):
        nodes = [
            {
                "id": "node-primary",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo 1",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": ["node-fb"],  # Primary depends on fallback node!
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "node-with-fb",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo 2",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "fallback_node",
                "fallback_node_id": "node-fb"
            },
            {
                "id": "node-fb",
                "role": "fallback",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo fb",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("cannot depend on fallback node" in err for err in topo_errs))

    def test_fallback_cycle_rejected(self):
        nodes = [
            {
                "id": "node-a",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo a",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "fallback_node",
                "fallback_node_id": "node-b"
            },
            {
                "id": "node-b",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo b",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "fallback_node",
                "fallback_node_id": "node-a"  # A -> B -> A cycle
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("Fallback cycle detected" in err for err in topo_errs))

    def test_stdlib_fallback_validation_enforces_rules(self):
        # Invalid manifest evaluated via validate_schema_fallback
        bad_manifest = {
            "version": "1.0.0",  # missing schema_version, graph_id, budget, nodes
            "nodes": [
                {
                    "id": "m1",
                    "type": "sequential_mutation",
                    "tier": "frontier_engine",
                    "command_or_eval": "echo",
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                    # missing mutation_targets
                }
            ]
        }
        errs = validate_schema_fallback(bad_manifest, self.schema)
        self.assertTrue(any("schema_version" in e for e in errs))
        self.assertTrue(any("graph_id" in e for e in errs))
        self.assertTrue(any("mutation_targets" in e for e in errs))

    def test_schema_parity_between_jsonschema_and_fallback(self):
        # A manifest with invalid type, enum, pattern, and range violations
        bad_manifest = {
            "schema_version": "1.0.0",
            "graph_id": "test-graph",
            "version": "banana",  # pattern violation
            "budget": {
                "token_ceiling_total": 5000,
                "max_parallel_concurrency": 999,  # maximum violation
                "max_retries_per_node": 1
            },
            "nodes": [
                {
                    "id": "bad id!",  # pattern violation
                    "type": "teleport",  # enum violation
                    "tier": "quantum",  # enum violation
                    "command_or_eval": 12345,  # type violation
                    "input_bindings": [],
                    "output_contract": "out.json",
                    "depends_on": [],
                    "failure_escalation": "rollback_and_halt"
                }
            ]
        }
        fallback_errs = validate_schema_fallback(bad_manifest, self.schema)
        # Verify fallback caught all 6 specific violations
        self.assertTrue(any("version" in e and "pattern" in e.lower() for e in fallback_errs))
        self.assertTrue(any("max_parallel_concurrency" in e and "greater" in e.lower() for e in fallback_errs))
        self.assertTrue(any("bad id!" in e for e in fallback_errs))
        self.assertTrue(any("teleport" in e for e in fallback_errs))
        self.assertTrue(any("quantum" in e for e in fallback_errs))
        self.assertTrue(any("command_or_eval" in e and "type" in e.lower() for e in fallback_errs))

        # Check jsonschema parity if jsonschema is installed
        try:
            import jsonschema
            json_errs = validate_schema(bad_manifest, self.schema)
            self.assertEqual(len(fallback_errs), len(json_errs), "Fallback and jsonschema must find same number of violations")
        except ImportError:
            pass

    def test_fallback_target_requires_role_fallback(self):
        # Target node exists but lacks role: "fallback"
        nodes = [
            {
                "id": "node-1",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo 1",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "fallback_node",
                "fallback_node_id": "final-tests"
            },
            {
                "id": "final-tests",
                "type": "verifier_gate",
                "tier": "deterministic_script",
                "command_or_eval": "echo test",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
                # Missing role: "fallback"!
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("Fallback role violation" in err for err in topo_errs))

    def test_orphan_fallback_node_fails(self):
        # Node has role: "fallback" but no node targets it
        nodes = [
            {
                "id": "node-1",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo 1",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            },
            {
                "id": "orphan-fb",
                "role": "fallback",
                "type": "parallel_read",
                "tier": "fast_engine",
                "command_or_eval": "echo fb",
                "input_bindings": [],
                "output_contract": "out.json",
                "depends_on": [],
                "failure_escalation": "rollback_and_halt"
            }
        ]
        manifest = self._make_manifest(nodes)
        topo_errs = validate_graph_topology(manifest)
        self.assertTrue(any("Orphan fallback node" in err for err in topo_errs))


if __name__ == "__main__":
    unittest.main()
