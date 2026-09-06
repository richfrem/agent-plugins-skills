"""
test_control_plane_ports.py — Dependency-Direction Invariant Check (issue-524, Step 2)
========================================================================================

Purpose:
    Verifies control_plane/ports.py declares pure interfaces with zero infrastructure
    imports, per docs/plans/issue-524-spec.md's dependency-direction invariant (DoD item 5,
    Section 5 Step 2): domain/policy code must not import sqlite3, subprocess, hashlib,
    time-based I/O, or concrete filesystem/model-catalog storage. This test statically
    inspects the module's import statements via `ast`, rather than trusting a manual read,
    so a future edit that accidentally reintroduces a banned import fails loudly.

Key Input Dependencies:
    - plugins/agent-agentic-os/scripts/control_plane/ports.py (module under test)

Key Functions:
    - test_ports_module_has_no_banned_infrastructure_imports()
    - test_ports_module_is_importable_standalone()
    - test_all_port_classes_are_abstract()
"""

import ast
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

BANNED_MODULES = {"sqlite3", "subprocess", "hashlib", "time", "os"}
PORTS_FILE = SCRIPTS_DIR / "control_plane" / "ports.py"


def _collect_imported_module_names(source: str) -> set:
    """Parses Python source and returns the set of top-level module names imported."""
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


def test_ports_module_has_no_banned_infrastructure_imports():
    """control_plane/ports.py must import only stdlib abc/typing/pathlib — never sqlite3,
    subprocess, hashlib, time, or os (filesystem side-effects belong in adapters)."""
    source = PORTS_FILE.read_text(encoding="utf-8")
    imported = _collect_imported_module_names(source)
    violations = imported & BANNED_MODULES
    assert not violations, f"control_plane/ports.py imports banned infrastructure modules: {violations}"


def test_ports_module_is_importable_standalone():
    """The ports module must import cleanly on its own, with no side effects requiring a
    live database, filesystem state, or network access."""
    from control_plane import ports  # noqa: F401 — import success is the assertion
    assert hasattr(ports, "PersistencePort")
    assert hasattr(ports, "FilesystemPort")
    assert hasattr(ports, "CryptoPort")
    assert hasattr(ports, "ClockPort")
    assert hasattr(ports, "ModelCatalogPort")


def test_all_port_classes_are_abstract():
    """Every port interface must be a true ABC that cannot be instantiated directly —
    proves each interface still has at least one unimplemented abstract method."""
    from control_plane import ports

    for cls in (ports.PersistencePort, ports.FilesystemPort, ports.CryptoPort,
                ports.ClockPort, ports.ModelCatalogPort):
        with pytest.raises(TypeError):
            cls()
