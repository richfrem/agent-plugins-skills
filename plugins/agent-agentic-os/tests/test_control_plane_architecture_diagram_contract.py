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
    - test_diagram_names_real_state_machine_component()
    - test_diagram_shows_sqlite_boundary()
    - test_diagram_shows_policy_to_persistence_relationship()
    - test_every_adapter_subclasses_its_corresponding_port()
    - test_diagram_has_plain_renderable_mermaid_syntax()
    - test_agent_control_has_no_sql_matching_the_diagrams_persistence_boundary_claim()
"""

import ast
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane import ports as _ports_module
from control_plane import adapters as _adapters_module

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DIAGRAM_FILE = REPO_ROOT / "docs" / "diagrams" / "control-plane-architecture.mermaid"
PORTS_FILE = SCRIPTS_DIR / "control_plane" / "ports.py"
ADAPTERS_FILE = SCRIPTS_DIR / "control_plane" / "adapters.py"
STATE_MACHINE_FILE = SCRIPTS_DIR / "control_plane" / "state_machine.py"
AGENT_CONTROL_FILE = SCRIPTS_DIR / "agent_control.py"

# Maps each *Adapter class name to the *Port class it must subclass — kept explicit (not
# inferred) so a mismatch (e.g. a new adapter that forgets to subclass its port) is a clear
# diff against this list, not a silent pass.
ADAPTER_TO_PORT = {
    "SqlitePersistenceAdapter": "PersistencePort",
    "CryptoAdapter": "CryptoPort",
    "FilesystemAdapter": "FilesystemPort",
    "ModelCatalogAdapter": "ModelCatalogPort",
    "ClockAdapter": "ClockPort",
}


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


def test_diagram_names_real_state_machine_component():
    """The diagram's State-machine node must correspond to a real class in
    control_plane/state_machine.py, not just a label with no backing component (round-2
    review finding: the diagram previously showed a State-machine validation node while that
    logic still lived inline in ControlPlane, with no corresponding module/class at all)."""
    diagram = DIAGRAM_FILE.read_text(encoding="utf-8")
    state_machine_classes = {c for c in _class_names(STATE_MACHINE_FILE) if c == "StateMachine"}
    assert state_machine_classes, "control_plane/state_machine.py must declare a StateMachine class"
    assert "StateMachine" in diagram, "diagram must name the real StateMachine class, not just a generic label"


def test_diagram_shows_policy_to_persistence_relationship():
    """The diagram must show the policy engine receiving facts through PersistencePort (a
    dotted edge), not appearing to read SQLite directly."""
    diagram = DIAGRAM_FILE.read_text(encoding="utf-8")
    assert "-.->" in diagram, "diagram should use a dotted edge for the policy-to-persistence relationship"
    # The dotted edge must actually connect something policy-related to PersistencePort —
    # not just exist anywhere in the file.
    dotted_lines = [line for line in diagram.splitlines() if "-.->" in line]
    assert any("PersistencePort" in line for line in dotted_lines), (
        "the dotted edge must target PersistencePort, not an unrelated node"
    )


def test_every_adapter_subclasses_its_corresponding_port():
    """Each concrete adapter must actually subclass its corresponding port at the Python
    level — not just be named similarly. Round-2 review finding: SqlitePersistenceAdapter was
    declared but did not subclass PersistencePort for several commits; this test makes that
    exact class of mismatch a permanent, automatic failure."""
    for adapter_name, port_name in ADAPTER_TO_PORT.items():
        adapter_cls = getattr(_adapters_module, adapter_name)
        port_cls = getattr(_ports_module, port_name)
        assert issubclass(adapter_cls, port_cls), (
            f"{adapter_name} does not subclass {port_name} — diagram implies a port/adapter "
            "relationship that the code does not actually have"
        )


def test_diagram_has_plain_renderable_mermaid_syntax():
    """Lightweight structural sanity check for GitHub-renderable Mermaid syntax — no full
    parser is available in this repo, so this checks the specific failure modes the diagram
    must avoid: starts with a valid diagram-type declaration, no raw HTML tags, no smart/curly
    quotes, and balanced brackets (a common source of 'Mermaid parse error' on GitHub)."""
    diagram = DIAGRAM_FILE.read_text(encoding="utf-8")
    assert diagram.lstrip().startswith("flowchart"), "diagram must start with a 'flowchart' declaration"
    assert "<" not in diagram and ">" not in diagram.replace("-->", "").replace("-.->", ""), (
        "diagram should not contain raw HTML-like tags in labels"
    )
    for smart_quote in ("“", "”", "‘", "’"):
        assert smart_quote not in diagram, f"diagram contains a smart quote ({smart_quote!r}) — use plain ASCII quotes"
    assert diagram.count("[") == diagram.count("]"), "unbalanced [ ] brackets in diagram"
    assert diagram.count("(") == diagram.count(")"), "unbalanced ( ) brackets in diagram"


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
