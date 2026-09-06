"""
test_control_plane_policy.py — Unified Gate-Policy Engine Unit Tests (issue-524, Step 4)
============================================================================================

Purpose:
    Unit tests for control_plane/policy.py in complete isolation from SQLite — every rule is
    exercised via a hand-built `ctx` dict of plain Python callables/values, proving the domain
    layer's gate logic is testable without a live database (the exact benefit the issue asked
    for). Also enforces the dependency-direction invariant (DoD item 5) and the structural
    confirmation that the 4 old scattered mechanisms no longer exist in agent_control.py
    (DoD item 4).

Key Input Dependencies:
    None — pure in-memory ctx dicts, no filesystem/SQLite/subprocess.

Key Functions:
    - test_policy_module_has_no_banned_infrastructure_imports()
    - test_agent_control_no_longer_defines_old_scattered_gate_mechanisms()
    - test_prior_art_rule_blocks_evolution_task_without_scan()
    - test_prior_art_rule_passes_for_general_task()
    - test_done_rule_blocks_and_passes_across_all_branches()
    - test_rolled_back_rule_blocks_and_passes()
    - test_worktree_push_operation_rule_permits_each_allowed_state_and_blocks_others()
    - test_evaluate_transition_noop_for_unregistered_edge()
"""

import ast
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

BANNED_MODULES = {"sqlite3", "subprocess", "hashlib", "time", "os"}
POLICY_FILE = SCRIPTS_DIR / "control_plane" / "policy.py"
AGENT_CONTROL_FILE = SCRIPTS_DIR / "agent_control.py"


def _collect_imported_module_names(source: str) -> set:
    tree = ast.parse(source)
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
    return names


def test_policy_module_has_no_banned_infrastructure_imports():
    """control_plane/policy.py must never import sqlite3/subprocess/hashlib/time/os — the
    domain layer receives everything it needs via the ctx dict (dependency-direction invariant)."""
    source = POLICY_FILE.read_text(encoding="utf-8")
    imported = _collect_imported_module_names(source)
    violations = imported & BANNED_MODULES
    assert not violations, f"control_plane/policy.py imports banned infrastructure modules: {violations}"


def test_agent_control_no_longer_defines_old_scattered_gate_mechanisms():
    """Structural confirmation (DoD item 4): _check_prior_art_guard, _check_done_guard,
    _check_rolled_back_guard, _check_gate_requirement, and the module-level GATE_REQUIREMENTS
    dict no longer exist as live definitions in agent_control.py."""
    source = AGENT_CONTROL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(source)

    defined_names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined_names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    defined_names.add(target.id)

    banned_definitions = {
        "_check_prior_art_guard", "_check_done_guard", "_check_rolled_back_guard",
        "_check_gate_requirement", "GATE_REQUIREMENTS",
        "_gate_receipt_exists", "_gate_critic_review_pass_exists", "_gate_any_of",
    }
    violations = defined_names & banned_definitions
    assert not violations, f"agent_control.py still defines old scattered gate mechanisms: {violations}"


def _base_ctx(**overrides):
    ctx = {
        "task_id": "t1",
        "task": {"task_type": "GENERAL"},
        "has_receipt": lambda gate_name: False,
        "has_passing_critic_review": lambda: False,
        "count_receipts": lambda gate_name, exit_code=None: 0,
        "count_locked_verifiers": lambda: 0,
        "count_asymmetric_persistence": lambda details_like=None, destination_like_any=None: 0,
        "verify_sovereignty": lambda: True,
    }
    ctx.update(overrides)
    return ctx


def test_prior_art_rule_blocks_evolution_task_without_scan():
    from control_plane import policy

    ctx = _base_ctx(task={"task_type": "EVOLUTION"})
    with pytest.raises(policy.PolicyViolation, match="Prior art scan required"):
        policy.evaluate_transition(ctx, "INTAKE", "INTERVIEW")


def test_prior_art_rule_passes_for_general_task():
    from control_plane import policy

    ctx = _base_ctx(task={"task_type": "GENERAL"})
    policy.evaluate_transition(ctx, "INTAKE", "INTERVIEW")  # must not raise


def test_prior_art_rule_passes_for_evolution_task_with_scan_logged():
    from control_plane import policy

    ctx = _base_ctx(
        task={"task_type": "EVOLUTION"},
        count_asymmetric_persistence=lambda details_like=None, destination_like_any=None: (
            1 if details_like == "%prior_art_scan%" else 0
        ),
    )
    policy.evaluate_transition(ctx, "INTAKE", "INTERVIEW")  # must not raise


def test_done_rule_blocks_and_passes_across_all_branches():
    from control_plane import policy

    # Branch 1: missing test_suite receipt
    ctx = _base_ctx()
    with pytest.raises(policy.PolicyViolation, match="No passing test_suite verification receipt"):
        policy.evaluate_transition(ctx, "VERIFY_EXIT", "DONE")

    # Branch 2: test_suite present, missing asymmetric persistence
    ctx = _base_ctx(
        count_receipts=lambda gate_name, exit_code=None: 1 if gate_name == "test_suite" else 0,
    )
    with pytest.raises(policy.PolicyViolation, match="Asymmetric persistence required before DONE"):
        policy.evaluate_transition(ctx, "VERIFY_EXIT", "DONE")

    # Branch 3: test_suite + persistence present, missing leak_check
    ctx = _base_ctx(
        count_receipts=lambda gate_name, exit_code=None: 1 if gate_name == "test_suite" else 0,
        count_asymmetric_persistence=lambda details_like=None, destination_like_any=None: 1,
    )
    with pytest.raises(policy.PolicyViolation, match="Missing clean leak check receipt"):
        policy.evaluate_transition(ctx, "VERIFY_EXIT", "DONE")

    # Branch 4: everything present, no locked verifiers -> passes
    ctx = _base_ctx(
        count_receipts=lambda gate_name, exit_code=None: 1,
        count_asymmetric_persistence=lambda details_like=None, destination_like_any=None: 1,
    )
    policy.evaluate_transition(ctx, "VERIFY_EXIT", "DONE")  # must not raise

    # Branch 5: locked verifiers present, sovereignty check invoked and passes
    sovereignty_calls = []
    ctx = _base_ctx(
        count_receipts=lambda gate_name, exit_code=None: 1,
        count_asymmetric_persistence=lambda details_like=None, destination_like_any=None: 1,
        count_locked_verifiers=lambda: 1,
        verify_sovereignty=lambda: sovereignty_calls.append(1),
    )
    policy.evaluate_transition(ctx, "VERIFY_EXIT", "DONE")
    assert sovereignty_calls == [1]


def test_rolled_back_rule_blocks_and_passes():
    from control_plane import policy

    ctx = _base_ctx()
    with pytest.raises(policy.PolicyViolation, match="Asymmetric persistence required"):
        policy.evaluate_transition(ctx, "IN_WORKTREE", "ROLLED_BACK")

    ctx = _base_ctx(count_asymmetric_persistence=lambda details_like=None, destination_like_any=None: 1)
    policy.evaluate_transition(ctx, "IN_WORKTREE", "ROLLED_BACK")  # must not raise


@pytest.mark.parametrize("allowed_state", ["WORKTREE_REVIEW", "MULTI_AGENT_CODE_REVIEW", "VERIFY_EXIT"])
def test_worktree_push_operation_rule_permits_each_allowed_state_and_blocks_others(allowed_state):
    from control_plane import policy

    op_ctx = {"task_id": "t1", "task_state": allowed_state}
    policy.evaluate_operation(op_ctx, "worktree_push")  # must not raise

    op_ctx_blocked = {"task_id": "t1", "task_state": "IN_WORKTREE"}
    with pytest.raises(policy.PolicyViolation, match="Post-implementation review stage gate required"):
        policy.evaluate_operation(op_ctx_blocked, "worktree_push")


def test_evaluate_transition_noop_for_unregistered_edge():
    from control_plane import policy

    ctx = _base_ctx()
    policy.evaluate_transition(ctx, "ESCALATED", "INTAKE")  # no rules registered; must not raise
