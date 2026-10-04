#!/usr/bin/env python3
"""
Manifest Validator for Agent Orchestration
===========================================

Validates graph-manifest.json files against:
1. JSON schema (graph-manifest-schema.json) with strict stdlib fallback
2. DAG acyclicity (topological sort / cycle detection)
3. Unique node IDs and dependency validity
4. Strict sequential total ordering of mutation nodes
5. Fallback node target integrity (no self-fallback, no cycles, no primary depending on fallback)
6. Approval gate semantics for autonomous execution mode (--check-approval-none)
7. Non-empty primary node set

Zero external dependencies outside standard library and optional jsonschema.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple, Optional


def load_schema(schema_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Locate and load graph-manifest-schema.json."""
    candidate_paths = []
    if schema_path:
        candidate_paths.append(Path(schema_path))
    
    script_dir = Path(__file__).resolve().parent
    candidate_paths.extend([
        script_dir.parent / "references" / "graph-manifest-schema.json",
        script_dir / "graph-manifest-schema.json",
        Path.cwd() / "plugins" / "agent-orchestration" / "references" / "graph-manifest-schema.json",
        Path.cwd() / ".agents" / "references" / "graph-manifest-schema.json",
        Path.cwd() / ".agents" / "skills" / "graph-planner" / "references" / "graph-manifest-schema.json",
    ])

    for p in candidate_paths:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load schema from {p}: {e}", file=sys.stderr)
    return None


def interpret_schema(instance: Any, schema: Dict[str, Any], path: str = "root") -> List[str]:
    """Pure stdlib JSON Schema interpreter supporting type, enum, pattern, min/max, properties, items, oneOf, allOf/if/then/const."""
    errors = []

    # 1. Type validation
    expected_type = schema.get("type")
    if expected_type:
        type_valid = True
        if expected_type == "object":
            type_valid = isinstance(instance, dict)
        elif expected_type == "array":
            type_valid = isinstance(instance, list)
        elif expected_type == "string":
            type_valid = isinstance(instance, str)
        elif expected_type == "integer":
            type_valid = isinstance(instance, int) and not isinstance(instance, bool)
        elif expected_type == "number":
            type_valid = isinstance(instance, (int, float)) and not isinstance(instance, bool)
        elif expected_type == "boolean":
            type_valid = isinstance(instance, bool)

        if not type_valid:
            actual_type = type(instance).__name__
            errors.append(f"Type error at [{path}]: expected '{expected_type}', got '{actual_type}'")
            return errors

    # 2. Const validation
    if "const" in schema:
        if instance != schema["const"]:
            errors.append(f"Const error at [{path}]: expected '{schema['const']}', got '{instance}'")
            return errors

    # 3. Enum validation
    if "enum" in schema:
        if instance not in schema["enum"]:
            errors.append(f"Enum error at [{path}]: '{instance}' not in allowed enum {schema['enum']}")

    # 4. Pattern validation
    if isinstance(instance, str) and "pattern" in schema:
        if not re.search(schema["pattern"], instance):
            errors.append(f"Pattern error at [{path}]: '{instance}' does not match pattern '{schema['pattern']}'")

    # 5. Numeric min/max
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"Range error at [{path}]: {instance} is less than minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"Range error at [{path}]: {instance} is greater than maximum {schema['maximum']}")

    # 6. Array minItems & items
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"Array error at [{path}]: contains {len(instance)} items, minimum required is {schema['minItems']}")
        if "items" in schema:
            items_schema = schema["items"]
            for idx, item in enumerate(instance):
                errors.extend(interpret_schema(item, items_schema, f"{path}[{idx}]"))

    # 7. Object properties, required, additionalProperties
    if isinstance(instance, dict):
        if "required" in schema:
            for req in schema["required"]:
                if req not in instance:
                    errors.append(f"Missing required property at [{path}]: '{req}'")

        props_schema = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            allowed_keys = set(props_schema.keys())
            extra_keys = set(instance.keys()) - allowed_keys
            if extra_keys:
                errors.append(f"Unrecognized property at [{path}]: {', '.join(sorted(extra_keys))}")

        for k, v in instance.items():
            if k in props_schema:
                errors.extend(interpret_schema(v, props_schema[k], f"{path}.{k}"))

    # 8. oneOf
    if "oneOf" in schema:
        matched = False
        for idx, sub_schema in enumerate(schema["oneOf"]):
            sub_errs = interpret_schema(instance, sub_schema, f"{path}#oneOf[{idx}]")
            if not sub_errs:
                matched = True
                break
        if not matched:
            errors.append(f"oneOf error at [{path}]: value does not match any valid schema variant")

    # 9. allOf / if / then
    if "allOf" in schema:
        for idx, cond in enumerate(schema["allOf"]):
            if "if" in cond and "then" in cond:
                if_errs = interpret_schema(instance, cond["if"], f"{path}#if[{idx}]")
                if not if_errs:
                    then_errs = interpret_schema(instance, cond["then"], f"{path}#then[{idx}]")
                    errors.extend(then_errs)
            else:
                errors.extend(interpret_schema(instance, cond, f"{path}#allOf[{idx}]"))

    return errors


def validate_schema_fallback(manifest: Dict[str, Any], schema: Optional[Dict[str, Any]] = None) -> List[str]:
    """Pure stdlib structural validator interpreting graph-manifest-schema.json directly when jsonschema is absent."""
    if not schema:
        schema = load_schema()
    if not schema:
        return ["Schema definition file 'graph-manifest-schema.json' could not be located"]
    return interpret_schema(manifest, schema)


def validate_schema(manifest: Dict[str, Any], schema: Optional[Dict[str, Any]]) -> List[str]:
    """Validate manifest against JSON schema if jsonschema is available, else fallback."""
    errors = []
    if schema:
        try:
            import jsonschema
            validator = jsonschema.Draft7Validator(schema)
            for err in validator.iter_errors(manifest):
                path_str = " -> ".join([str(p) for p in err.path]) if err.path else "root"
                errors.append(f"Schema violation at [{path_str}]: {err.message}")
            return errors
        except ImportError:
            pass

    # Run strict stdlib structural fallback interpreting the schema directly
    return validate_schema_fallback(manifest, schema)


def validate_graph_topology(manifest: Dict[str, Any], check_approval_none: bool = False) -> List[str]:
    """Perform topological, structural, and ordering validation on manifest nodes."""
    errors = []
    nodes = manifest.get("nodes", [])
    if not isinstance(nodes, list) or len(nodes) == 0:
        return ["Manifest contains no valid 'nodes' array"]

    node_ids: Set[str] = set()
    node_map: Dict[str, Dict[str, Any]] = {}
    fallback_map: Dict[str, str] = {}  # source_id -> fallback_id

    # 1. Unique IDs & map creation
    for idx, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"Node at index {idx} is not an object")
            continue
        nid = node.get("id")
        if not nid or not isinstance(nid, str):
            errors.append(f"Node at index {idx} has invalid or missing 'id'")
            continue
        if nid in node_ids:
            errors.append(f"Duplicate node ID detected: '{nid}'")
        node_ids.add(nid)
        node_map[nid] = node

        if node.get("failure_escalation") == "fallback_node":
            f_id = node.get("fallback_node_id")
            if not f_id:
                errors.append(f"Node '{nid}' declares failure_escalation='fallback_node' but lacks 'fallback_node_id'")
            elif f_id == nid:
                errors.append(f"Self-fallback detected: Node '{nid}' cannot name itself as fallback_node_id")
            else:
                fallback_map[nid] = f_id

    fallback_node_ids = set(fallback_map.values())
    primary_node_ids = [nid for nid in node_ids if nid not in fallback_node_ids]
    if len(primary_node_ids) == 0:
        errors.append("Zero primary nodes: All nodes in manifest are designated as fallbacks")

    # Invariant: Nodes targeted as fallback_node_id MUST have role='fallback'
    for src_id, fb_id in fallback_map.items():
        if fb_id in node_map:
            target_role = node_map[fb_id].get("role")
            if target_role != "fallback":
                errors.append(
                    f"Fallback role violation: Node '{src_id}' targets fallback_node_id '{fb_id}', "
                    f"but node '{fb_id}' declares role='{target_role}' instead of 'fallback'."
                )

    # Invariant: Any node with role='fallback' must be targeted as a fallback_node_id
    for nid, node in node_map.items():
        if node.get("role") == "fallback" and nid not in fallback_node_ids:
            errors.append(
                f"Orphan fallback node: Node '{nid}' declares role='fallback' but is not referenced "
                "by any node's fallback_node_id."
            )

    # 2. Dependency reference check & fallback validation
    for nid, node in node_map.items():
        deps = node.get("depends_on", [])
        if not isinstance(deps, list):
            errors.append(f"Node '{nid}' 'depends_on' must be an array")
            continue
        for dep in deps:
            if dep not in node_map:
                errors.append(f"Node '{nid}' depends on unknown node '{dep}'")
            if dep == nid:
                errors.append(f"Node '{nid}' depends on itself")
            # Invariant: Primary nodes must never depend on fallback nodes
            if nid not in fallback_node_ids and dep in fallback_node_ids:
                errors.append(f"Invalid dependency: Primary node '{nid}' cannot depend on fallback node '{dep}'")

        f_id = node.get("fallback_node_id")
        if f_id and f_id not in node_map:
            errors.append(f"Node '{nid}' references non-existent fallback_node_id '{f_id}'")

    # Check for fallback cycles (e.g., A -> B -> A)
    for start_node, target_node in fallback_map.items():
        curr = target_node
        seen = {start_node}
        while curr in fallback_map:
            if curr in seen:
                errors.append(f"Fallback cycle detected: '{curr}' leads back into fallback cycle")
                break
            seen.add(curr)
            curr = fallback_map[curr]

    # 3. Cycle Detection in primary DAG (Topological Sort / Kahn's algorithm)
    in_degree = {nid: 0 for nid in node_map}
    adj: Dict[str, List[str]] = {nid: [] for nid in node_map}

    for nid, node in node_map.items():
        for dep in node.get("depends_on", []):
            if dep in node_map:
                adj[dep].append(nid)
                in_degree[nid] += 1

    queue = [nid for nid in node_map if in_degree[nid] == 0]
    visited_count = 0

    while queue:
        curr = queue.pop(0)
        visited_count += 1
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited_count < len(node_map):
        errors.append(f"Cyclic dependency detected: Graph contains a cycle (visited {visited_count} of {len(node_map)} nodes)")

    # 4. Strict Total Ordering of Mutation Nodes
    mutation_nodes = [node for node in nodes if isinstance(node, dict) and node.get("type") == "sequential_mutation"]
    if len(mutation_nodes) > 1:
        # Build reachability map for mutations
        reachable: Dict[str, Set[str]] = {m["id"]: set() for m in mutation_nodes}
        for m in mutation_nodes:
            q = list(m.get("depends_on", []))
            visited_deps = set(q)
            while q:
                d = q.pop(0)
                if d in node_map:
                    for parent in node_map[d].get("depends_on", []):
                        if parent not in visited_deps:
                            visited_deps.add(parent)
                            q.append(parent)
            reachable[m["id"]] = visited_deps

        # For every pair of mutations (A, B), either A reachable from B or B reachable from A
        for i in range(len(mutation_nodes)):
            for j in range(i + 1, len(mutation_nodes)):
                m1 = mutation_nodes[i]["id"]
                m2 = mutation_nodes[j]["id"]
                m1_depends_on_m2 = m2 in reachable[m1]
                m2_depends_on_m1 = m1 in reachable[m2]
                if not (m1_depends_on_m2 or m2_depends_on_m1):
                    errors.append(
                        f"Mutation total ordering violation: Mutation nodes '{m1}' and '{m2}' "
                        f"are unordered / parallel. All sequential_mutation nodes must form a strict linear chain."
                    )

    # 5. Approval Gate Check for --approval none on mutation graphs
    if check_approval_none and len(mutation_nodes) > 0:
        root_nodes = [n for n in nodes if not n.get("depends_on")]
        approval_gate = None
        for n in root_nodes:
            if n.get("type") == "verifier_gate" and n.get("role") == "approval":
                approval_gate = n
                break

        if not approval_gate:
            errors.append(
                "Approval gate violation: Graph contains sequential_mutation nodes but lacks a leading "
                "root verifier_gate with role='approval'. Running with --approval none is prohibited."
            )
        else:
            app_id = approval_gate["id"]
            for m in mutation_nodes:
                mid = m["id"]
                q = list(m.get("depends_on", []))
                seen = set(q)
                found = False
                while q:
                    curr = q.pop(0)
                    if curr == app_id:
                        found = True
                        break
                    if curr in node_map:
                        for p in node_map[curr].get("depends_on", []):
                            if p not in seen:
                                seen.add(p)
                                q.append(p)
                if not found:
                    errors.append(
                        f"Approval dependency violation: sequential_mutation node '{mid}' "
                        f"does not depend on leading approval gate '{app_id}'"
                    )

    # 6. Verifier gate tier check
    for n in nodes:
        if isinstance(n, dict) and n.get("type") == "verifier_gate":
            if n.get("tier") != "deterministic_script":
                errors.append(f"Verifier gate '{n.get('id')}' must use tier='deterministic_script', found '{n.get('tier')}'")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Graph Manifest Validator")
    parser.add_argument("manifest", help="Path to graph-manifest.json file")
    parser.add_argument("--schema", help="Optional path to custom graph-manifest-schema.json")
    parser.add_argument("--check-approval-none", action="store_true",
                        help="Enforce that mutation graphs have a leading approval gate and all mutations depend on it")

    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"ERROR: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON syntax in {manifest_path}: {e}", file=sys.stderr)
        sys.exit(1)

    schema = load_schema(args.schema)
    all_errors = []

    if schema:
        schema_errors = validate_schema(manifest, schema)
        all_errors.extend(schema_errors)
    else:
        # If schema file missing, still run strict stdlib structural fallback
        fallback_errors = validate_schema_fallback(manifest)
        all_errors.extend(fallback_errors)

    topology_errors = validate_graph_topology(manifest, check_approval_none=args.check_approval_none)
    all_errors.extend(topology_errors)

    if all_errors:
        print(f"FAILED: Manifest validation failed for {manifest_path} with {len(all_errors)} error(s):", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"PASS: Manifest '{manifest.get('graph_id')}' (v{manifest.get('version')}) is structurally valid.")
    sys.exit(0)


if __name__ == "__main__":
    main()
