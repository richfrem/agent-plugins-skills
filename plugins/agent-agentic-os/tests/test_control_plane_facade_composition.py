"""
test_control_plane_facade_composition.py — Facade Composition Confirmation (issue-524, Step 8)
====================================================================================================

Purpose:
    Confirms ControlPlane is genuinely a thin, composing facade — not a class that quietly
    re-absorbed the responsibilities it delegated, or a "replacement god-service" per
    docs/plans/issue-524-spec.md's Section 5 Step 8 warning. Revised after external
    post-implementation review (round 2) found the original version of this file only checked
    for naive substrings ("hashlib" anywhere in the file, including this file's own prose) and
    did not actually prove delegation — a default ControlPlane could still contain raw SQL
    while passing those checks. This version:
    (1) Uses `ast` to confirm agent_control.py never imports sqlite3/hashlib/time at the module
        level (real absence of the capability to use them directly, not a string-search proxy);
    (2) confirms ControlPlane composes all 5 real adapters by default;
    (3) injects a hand-built fake PersistencePort (no SQLite at all) and proves task creation,
        lookup, transition application, receipt/review/verifier operations, and worktree
        updates all actually delegate to it — the assertion is "the fake was called with the
        right arguments and its return value flowed through", not "a substring is absent".

Key Input Dependencies:
    None — static AST inspection plus a default-constructed ControlPlane and a fake
    PersistencePort double.

Key Functions:
    - test_control_plane_composes_all_adapters_by_default()
    - test_agent_control_has_no_infrastructure_imports()
    - test_fake_persistence_port_proves_full_delegation()
"""

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane
from control_plane.adapters import FilesystemAdapter, CryptoAdapter, ModelCatalogAdapter, ClockAdapter, SqlitePersistenceAdapter
from control_plane.ports import PersistencePort

AGENT_CONTROL_FILE = SCRIPTS_DIR / "agent_control.py"
BANNED_MODULES = {"sqlite3", "hashlib", "time"}


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


def test_control_plane_composes_all_adapters_by_default(tmp_path):
    """A default-constructed ControlPlane wires all 5 real adapters as instance attributes —
    the facade composes, it doesn't reabsorb their responsibilities."""
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    assert isinstance(cp._fs, FilesystemAdapter)
    assert isinstance(cp._crypto, CryptoAdapter)
    assert isinstance(cp._clock, ClockAdapter)
    assert isinstance(cp._model_catalog, ModelCatalogAdapter)
    assert isinstance(cp._persistence, SqlitePersistenceAdapter)


def test_agent_control_has_no_infrastructure_imports():
    """agent_control.py must never import sqlite3, hashlib, or time at module level — this is
    an AST-based check of actual import statements, not a substring search (a substring search
    on the literal word "hashlib" previously false-failed on this very docstring's own prose
    explaining the invariant — fixed by parsing imports instead of grepping text)."""
    source = AGENT_CONTROL_FILE.read_text(encoding="utf-8")
    imported = _collect_imported_module_names(source)
    violations = imported & BANNED_MODULES
    assert not violations, f"agent_control.py imports banned infrastructure modules: {violations}"


class _FakePersistencePort(PersistencePort):
    """Hand-built fake with zero SQLite — records every call and returns scripted values, so
    tests can prove ControlPlane's CRUD methods delegate rather than reimplementing SQL."""

    def __init__(self):
        self.calls: List[tuple] = []
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._locked_verifiers: List[Dict[str, Any]] = []
        self._receipts: List[Dict[str, Any]] = []
        self.schema_ensured = False

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        self.calls.append(("get_task", task_id))
        return self._tasks.get(task_id)

    def insert_task(self, task_id, title, task_type, runtime_tool, spec_path, model_tier, model_id) -> None:
        self.calls.append(("insert_task", task_id, title, task_type, runtime_tool, spec_path, model_tier, model_id))
        self._tasks[task_id] = {
            "task_id": task_id, "title": title, "task_type": task_type, "runtime_tool": runtime_tool,
            "spec_path": spec_path, "model_tier": model_tier, "model_id": model_id, "state": "INTAKE",
        }

    def read_current_state(self, task_id: str) -> Optional[str]:
        self.calls.append(("read_current_state", task_id))
        task = self._tasks.get(task_id)
        return task["state"] if task else None

    def apply_transition(self, task_id, from_state, to_state, actor, reason) -> bool:
        self.calls.append(("apply_transition", task_id, from_state, to_state, actor, reason))
        if self._tasks[task_id]["state"] != from_state:
            return False
        self._tasks[task_id]["state"] = to_state
        return True

    def count_asymmetric_persistence(self, task_id, details_like=None, destination_like_any=None) -> int:
        self.calls.append(("count_asymmetric_persistence", task_id, details_like, destination_like_any))
        return 0

    def count_receipts(self, task_id, gate_name, exit_code=None) -> int:
        self.calls.append(("count_receipts", task_id, gate_name, exit_code))
        return 0

    def count_locked_verifiers(self, task_id) -> int:
        self.calls.append(("count_locked_verifiers", task_id))
        return len(self._locked_verifiers)

    def get_locked_verifiers(self, task_id) -> List[Dict[str, Any]]:
        self.calls.append(("get_locked_verifiers", task_id))
        return list(self._locked_verifiers)

    def has_passing_critic_review(self, task_id) -> bool:
        self.calls.append(("has_passing_critic_review", task_id))
        return False

    def has_receipt(self, task_id, gate_name) -> bool:
        self.calls.append(("has_receipt", task_id, gate_name))
        return False

    def insert_verification_receipt(self, task_id, gate_name, command_executed, exit_code, receipt_token) -> None:
        self.calls.append(("insert_verification_receipt", task_id, gate_name, command_executed, exit_code, receipt_token))
        self._receipts.append({"task_id": task_id, "gate_name": gate_name, "receipt_token": receipt_token})

    def insert_critic_review(self, task_id, iteration, model, verdict, findings) -> None:
        self.calls.append(("insert_critic_review", task_id, iteration, model, verdict, findings))

    def insert_locked_verifier(self, task_id, file_path, expected_sha256) -> None:
        self.calls.append(("insert_locked_verifier", task_id, file_path, expected_sha256))
        self._locked_verifiers.append({"file_path": file_path, "expected_sha256": expected_sha256})

    def insert_asymmetric_persistence(self, task_id, destination, status, details) -> None:
        self.calls.append(("insert_asymmetric_persistence", task_id, destination, status, details))

    def get_verification_receipts(self, task_id) -> List[Dict[str, Any]]:
        self.calls.append(("get_verification_receipts", task_id))
        return [r for r in self._receipts if r["task_id"] == task_id]

    def update_worktree_fields(self, task_id, worktree_path, worktree_branch, worktree_state) -> None:
        self.calls.append(("update_worktree_fields", task_id, worktree_path, worktree_branch, worktree_state))
        self._tasks[task_id]["worktree_state"] = worktree_state

    def ensure_schema(self) -> None:
        self.schema_ensured = True


def test_fake_persistence_port_proves_full_delegation(tmp_path, monkeypatch):
    """Injects a fake PersistencePort with zero SQLite and drives task creation, lookup,
    transition application, receipt recording, critic review, and worktree update through
    ControlPlane — proving every one of these operations actually delegates to the port
    rather than ControlPlane reimplementing the SQL itself. If ControlPlane silently
    reabsorbed any of this logic, the fake would never be called and this test would fail
    with a missing-call assertion, not just an absent substring."""
    fake = _FakePersistencePort()
    cp = ControlPlane(db_path=tmp_path / "unused.db")
    monkeypatch.setattr(cp, "_persistence", fake)

    cp.create_task(task_id="t1", title="Fake Persistence Task", runtime_tool="claude")
    assert ("insert_task", "t1", "Fake Persistence Task", "GENERAL", "claude", None, None, None) in fake.calls
    assert cp.get_task("t1") == fake._tasks["t1"]

    cp.transition(task_id="t1", to_state="INTERVIEW", actor="user", reason="test")
    assert ("apply_transition", "t1", "INTAKE", "INTERVIEW", "user", "test") in fake.calls
    assert fake._tasks["t1"]["state"] == "INTERVIEW"

    token = cp.record_verification_receipt(task_id="t1", gate_name="test_suite", command_executed="pytest", exit_code=0)
    assert any(c[0] == "insert_verification_receipt" and c[1] == "t1" for c in fake.calls)
    assert cp.get_verification_receipts("t1") == [{"task_id": "t1", "gate_name": "test_suite", "receipt_token": token}]

    cp.record_critic_review(task_id="t1", iteration=1, model="test-model", verdict="PASS", findings="ok")
    assert ("insert_critic_review", "t1", 1, "test-model", "PASS", "ok") in fake.calls

    cp.log_asymmetric_persistence(task_id="t1", destination="wiki/decisions/x.md", status="OBSERVED", details="d")
    assert ("insert_asymmetric_persistence", "t1", "wiki/decisions/x.md", "OBSERVED", "d") in fake.calls

    fake._tasks["t1"]["state"] = "WORKTREE_REVIEW"  # satisfy the push-barrier policy check
    cp.update_worktree(task_id="t1", worktree_path="/tmp/wt", worktree_branch="b", worktree_state="pushed_to_origin")
    assert ("update_worktree_fields", "t1", "/tmp/wt", "b", "pushed_to_origin") in fake.calls
