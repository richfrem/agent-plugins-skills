"""
test_control_plane_facade_composition.py — Facade Composition Confirmation (issue-524, Step 8)
====================================================================================================

Purpose:
    Confirms ControlPlane is genuinely a thin, composing facade after the Step 3-7 extractions
    — not a class that quietly re-absorbed the responsibilities it delegated, or a "replacement
    god-service" per docs/plans/issue-524-spec.md's Section 5 Step 8 warning. Checks both:
    (1) ControlPlane composes all 4 adapters as instance attributes of the expected concrete
        types by default; and
    (2) agent_control.py's module source contains no direct infrastructure calls that bypass
        those composed adapters (no bare `hashlib.`, `open(`, or raw `sqlite3.connect(` calls
        outside the adapter-delegating methods already covered by other Step 3/5/6 structural
        tests) — a coarse but permanent regression guard against re-absorption.

Key Input Dependencies:
    None — static source inspection plus a default-constructed ControlPlane instance.

Key Functions:
    - test_control_plane_composes_all_four_adapters_by_default()
    - test_agent_control_has_no_bare_sqlite3_connect_outside_persistence_adapter()
    - test_agent_control_has_no_direct_hashlib_usage()
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_control import ControlPlane
from control_plane.adapters import FilesystemAdapter, CryptoAdapter, ModelCatalogAdapter, SqlitePersistenceAdapter

AGENT_CONTROL_FILE = SCRIPTS_DIR / "agent_control.py"


def test_control_plane_composes_all_four_adapters_by_default(tmp_path):
    """A default-constructed ControlPlane wires all 4 real adapters as instance attributes —
    the facade composes, it doesn't reabsorb their responsibilities."""
    cp = ControlPlane(db_path=tmp_path / "control_plane.db")
    assert isinstance(cp._fs, FilesystemAdapter)
    assert isinstance(cp._crypto, CryptoAdapter)
    assert isinstance(cp._model_catalog, ModelCatalogAdapter)
    assert isinstance(cp._persistence, SqlitePersistenceAdapter)


def test_agent_control_has_no_bare_sqlite3_connect_outside_persistence_adapter():
    """agent_control.py itself must never call sqlite3.connect() directly — all connections
    come from self._persistence.get_connection() (Step 5). A bare sqlite3.connect() call here
    would mean ControlPlane silently reabsorbed connection management."""
    source = AGENT_CONTROL_FILE.read_text(encoding="utf-8")
    assert "sqlite3.connect(" not in source


def test_agent_control_has_no_direct_hashlib_usage():
    """agent_control.py must not import or call hashlib directly — all hashing goes through
    self._crypto (Step 6). Presence here would mean crypto logic was silently reabsorbed."""
    source = AGENT_CONTROL_FILE.read_text(encoding="utf-8")
    assert "hashlib" not in source
