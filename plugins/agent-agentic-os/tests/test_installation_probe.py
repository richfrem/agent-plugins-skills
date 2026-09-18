import sqlite3
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.installation_probe import classify_target
from control_plane.adapters import CURRENT_SCHEMA_VERSION


def _scaffold(target: Path, *, version: int = CURRENT_SCHEMA_VERSION, transitions: bool = True,
              authorized_actor_parity: bool = True) -> None:
    for rel in (".claude/hooks/hooks.json", ".git/hooks/pre-commit-evolution-guard",
                ".github/workflows/verify-evolution-integrity.yml"):
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("managed", encoding="utf-8")
    db_path = target / "context/control_plane.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE schema_version (version INTEGER NOT NULL)")
    conn.execute("INSERT INTO schema_version VALUES (?)", (version,))
    conn.execute("CREATE TABLE valid_transitions (from_state TEXT, to_state TEXT, authorized_actor TEXT)")
    if transitions:
        from control_plane.adapters import LEGAL_INITIAL_STATES
        from control_plane.registry import TransitionRegistry
        registry = TransitionRegistry.load_default()
        edges_with_actor = registry.get_all_edges_with_actor()
        if not authorized_actor_parity:
            edges_with_actor = [(f, t, "agent_or_human") for (f, t, _a) in edges_with_actor]
        valid_rows = list(edges_with_actor) + [(None, s, "agent_or_human") for s in LEGAL_INITIAL_STATES]
        conn.executemany("INSERT INTO valid_transitions VALUES (?, ?, ?)", valid_rows)
    conn.execute("CREATE TRIGGER enforce_valid_transition AFTER INSERT ON schema_version BEGIN SELECT 1; END")
    conn.commit()
    conn.close()


def test_fresh_target_is_classified_without_writes(tmp_path):
    result = classify_target(tmp_path)
    assert result.state == "FRESH"


def test_complete_target_requires_schema_and_transition_parity(tmp_path):
    _scaffold(tmp_path)
    result = classify_target(tmp_path)
    assert result.state == "COMPLETE"
    assert result.missing == ()


def test_stale_schema_or_transition_rows_are_drifted(tmp_path):
    _scaffold(tmp_path, version=CURRENT_SCHEMA_VERSION - 1, transitions=False)
    result = classify_target(tmp_path)
    assert result.state == "PARTIAL_OR_DRIFTED"
    assert any("schema" in item or "transition" in item for item in result.missing)


def test_authorized_actor_column_drift_is_reported(tmp_path):
    """T5: an installed database whose valid_transitions.authorized_actor values
    disagree with the registry's own authorized_actor derivation (e.g. from an
    unsynced or manually-edited row) must be reported as drift, not silently
    ignored -- authorized_actor is security-relevant, not cosmetic."""
    _scaffold(tmp_path, authorized_actor_parity=False)
    result = classify_target(tmp_path)
    assert result.state == "PARTIAL_OR_DRIFTED"
    assert any("authorized_actor" in item for item in result.missing)
