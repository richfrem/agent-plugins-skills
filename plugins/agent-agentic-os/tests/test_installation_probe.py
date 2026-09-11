import sqlite3
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from control_plane.installation_probe import classify_target


def _scaffold(target: Path, *, version: int = 8, transitions: bool = True) -> None:
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
    conn.execute("CREATE TABLE valid_transitions (from_state TEXT, to_state TEXT)")
    if transitions:
        from control_plane.state_machine import ALLOWED_TRANSITIONS
        conn.executemany("INSERT INTO valid_transitions VALUES (?, ?)",
                         [(source, target_state) for source, targets in ALLOWED_TRANSITIONS.items()
                          for target_state in targets])
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
    _scaffold(tmp_path, version=7, transitions=False)
    result = classify_target(tmp_path)
    assert result.state == "PARTIAL_OR_DRIFTED"
    assert any("schema" in item or "transition" in item for item in result.missing)
