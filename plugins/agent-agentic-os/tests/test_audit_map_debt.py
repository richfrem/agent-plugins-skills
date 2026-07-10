import sys
import tempfile
from pathlib import Path

# Bootstrap path to include scripts
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "plugins/agent-agentic-os/scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# Import the functions we built
from audit_map_debt import parse_debt_entries, evaluate_debt

def test_parse_debt_entries_with_valid_file():
    content = """
# Map Debt

- Logged: 2026-07-01
- Artifact: test_file.py
- Friction: Test friction
- Why not fixed: Deferred
- Recommended fix: Fix it
- Evidence: None
- Severity: M
- Repeat: NO
- Status: OPEN

---

- Logged: 2026-06-15
- Artifact: another_file.py
- Friction: Old friction
- Why not fixed: Deferred
- Recommended fix: Fix it
- Evidence: None
- Severity: L
- Repeat: YES
- Status: RESOLVED
"""
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        entries = parse_debt_entries(Path(temp_path))
        assert len(entries) == 2
        
        # Verify first entry parsing
        assert entries[0]["Logged"] == "2026-07-01"
        assert entries[0]["Artifact"] == "test_file.py"
        assert entries[0]["Repeat"] == "NO"
        assert entries[0]["Status"] == "OPEN"
        
        # Verify second entry parsing
        assert entries[1]["Logged"] == "2026-06-15"
        assert entries[1]["Repeat"] == "YES"
        assert entries[1]["Status"] == "RESOLVED"
    finally:
        Path(temp_path).unlink()

def test_evaluate_debt_passes_with_fresh_open_entries():
    entries = [
        {
            "Logged": "2026-07-02",
            "Artifact": "file.py",
            "Repeat": "NO",
            "Status": "OPEN",
            "Friction": "Minor issue"
        }
    ]
    errors = evaluate_debt(entries, today_str="2026-07-04")
    assert len(errors) == 0

def test_evaluate_debt_fails_with_expired_open_entry():
    entries = [
        {
            "Logged": "2026-06-15",
            "Artifact": "file.py",
            "Repeat": "NO",
            "Status": "OPEN",
            "Friction": "Stale issue"
        }
    ]
    errors = evaluate_debt(entries, today_str="2026-07-04")
    assert len(errors) == 1
    assert "EXPIRED" in errors[0]
    assert "file.py" in errors[0]

def test_evaluate_debt_fails_with_repeat_open_entry():
    entries = [
        {
            "Logged": "2026-07-03",
            "Artifact": "file.py",
            "Repeat": "YES",
            "Status": "OPEN",
            "Friction": "Repeated issue"
        }
    ]
    errors = evaluate_debt(entries, today_str="2026-07-04")
    assert len(errors) == 1
    assert "REPEAT" in errors[0]
    assert "file.py" in errors[0]

def test_evaluate_debt_passes_with_resolved_expired_or_repeat_entries():
    entries = [
        {
            "Logged": "2026-06-15",
            "Artifact": "file.py",
            "Repeat": "YES",
            "Status": "RESOLVED",
            "Friction": "Old issue"
        }
    ]
    errors = evaluate_debt(entries, today_str="2026-07-04")
    assert len(errors) == 0
