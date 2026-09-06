"""
test_control_plane_architecture_diagram_contract.py — Diagram/Code Alignment Contract (issue-524)
======================================================================================================

Purpose:
    docs/diagrams/control-plane-architecture.mermaid is a durable architectural contract, not
    decorative documentation — it exists so a future regression (SQL creeping back into
    ControlPlane, policy reading SQLite directly, a declared port losing its adapter) is
    visible as a diagram/code mismatch, not just discoverable by re-reading the whole file.
    This test parses control_plane/ports.py and control_plane/adapters.py via `ast` to get the
    real, current list of Port and Adapter class names, and asserts the diagram names every one
    of them, plus the facade class and the policy module. If a new port/adapter is added to the
    code without updating the diagram, this test fails — forcing the diagram to be kept honest.

Key Input Dependencies:
    - docs/diagrams/control-plane-architecture.mermaid (repo root, relative path resolved below)
    - plugins/agent-agentic-os/scripts/control_plane/ports.py
    - plugins/agent-agentic-os/scripts/control_plane/adapters.py

Key Functions:
    - test_diagram_names_every_port_class()
    - test_diagram_names_every_adapter_class()
    - test_diagram_names_facade_and_policy_module()
    - test_diagram_shows_sqlite_boundary()
    - test_agent_control_has_no_sql_matching_the_diagrams_persistence_boundary_claim()
"""

import ast
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DIAGRAM_FILE = REPO_ROOT / "docs" / "diagrams" / "control-plane-architecture.mermaid"
PORTS_FILE = SCRIPTS_DIR / "control_plane" / "ports.py"
ADAPTERS_FILE = SCRIPTS_DIR / "control_plane" / "adapters.py"
AGENT_CONTROL_FILE = SCRIPTS_DIR / "agent_control.py"


def _class_names(source_path: Path) -> set:
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def test_diagram_names_every_port_class():
    """Every *Port class currently declared in ports.py must be named in the diagram."""
    diagram = DIAGRAM_FILE.read_text(encoding="utf-8")
    port_classes = {c for c in _class_names(PORTS_FILE) if c.endswith("Port")}
    assert port_classes, "sanity check: ports.py should declare at least one *Port class"
    missing = {c for c in port_classes if c not in diagram}
    assert not missing, f"Diagram is missing port class(es): {missing}"


def test_diagram_names_every_adapter_class():
    """Every *Adapter class currently declared in adapters.py must be named in the diagram."""
    diagram = DIAGRAM_FILE.read_text(encoding="utf-8")
    adapter_classes = {c for c in _class_names(ADAPTERS_FILE) if c.endswith("Adapter")}
    assert adapter_classes, "sanity check: adapters.py should declare at least one *Adapter class"
    missing = {c for c in adapter_classes if c not in diagram}
    assert not missing, f"Diagram is missing adapter class(es): {missing}"


def test_diagram_names_facade_and_policy_module():
    """The diagram must name the ControlPlane facade and reference the policy engine."""
    diagram = DIAGRAM_FILE.read_text(encoding="utf-8")
    assert "ControlPlane" in diagram
    assert "policy" in diagram.lower()


def test_diagram_shows_sqlite_boundary():
    """The diagram must show the SQLite database as the terminal node behind
    SqlitePersistenceAdapter, using Mermaid's cylinder shape `[( )]`."""
    diagram = DIAGRAM_FILE.read_text(encoding="utf-8")
    assert "control_plane.db" in diagram
    assert "[(" in diagram, "diagram should use Mermaid cylinder syntax [( )] for the database node"


def test_agent_control_has_no_sql_matching_the_diagrams_persistence_boundary_claim():
    """The diagram claims ControlPlane never executes SQL directly — this test is the
    executable half of that contract (the diagram is the documented half). Duplicates the
    check in test_control_plane_facade_composition.py deliberately: that file protects the
    facade-composition claim; this one protects the diagram-accuracy claim specifically, so
    the two can fail independently with distinct, specific messages."""
    source = AGENT_CONTROL_FILE.read_text(encoding="utf-8")
    for banned in ("sqlite3.connect(", "conn.execute(", "SELECT ", "INSERT INTO", "UPDATE tasks"):
        assert banned not in source, (
            f"agent_control.py contains {banned!r} — this contradicts the architecture diagram's "
            "claim that ControlPlane delegates all persistence to SqlitePersistenceAdapter"
        )
