#!/usr/bin/env python3
"""
smoke_test.py — Standalone end-to-end smoke test for state_engine.py.

No pytest required. Run directly:
    python3 plugins/exploration-cycle-plugin/tests/smoke_test.py

Complements the pytest suite (test_state_engine.py) with a human-readable
pass/fail walkthrough of the full session → task → dashboard → budget-gate flow.
Cleans up its DB after every run.
"""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from state_engine import (
    init_db, create_session, add_task, lease_task, project_dashboard,
    MAX_PARALLEL_AGENTS,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"
results: list[tuple[str, bool]] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    icon = PASS if condition else FAIL
    print(f"  {icon}  {label}" + (f" — {detail}" if detail else ""))
    results.append((label, condition))


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    db_path = Path(__file__).parent / "smoke_test.sqlite"
    db_path.unlink(missing_ok=True)

    conn = None
    try:
        print("── Setup ─────────────────────────────────────────────────────")

        conn = init_db(str(db_path))
        check("init_db", True)

        session_id = str(uuid.uuid4())
        create_session(conn, session_id, "Court Scheduling Domain")
        row = conn.execute(
            "SELECT session_name FROM sessions WHERE id=?", (session_id,)
        ).fetchone()
        check("create_session", row and row[0] == "Court Scheduling Domain")

        task_names = ["Interview Stakeholders", "Map Domain Terms", "Write Contract"]
        task_ids = []
        for name in task_names:
            tid = str(uuid.uuid4())
            task_ids.append(tid)
            add_task(conn, tid, session_id, 1, "Discovery", name)
        count = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE session_id=?", (session_id,)
        ).fetchone()[0]
        check("add_task × 3", count == 3, f"{count} rows")

        print("\n── Dashboard ─────────────────────────────────────────────────")
        dashboard = project_dashboard(conn, session_id)
        check("dashboard contains session name", "Court Scheduling Domain" in dashboard)
        check("dashboard has 3 pending checkboxes", dashboard.count("[ ]") == 3)
        print(dashboard)

        print("── Budget gate ───────────────────────────────────────────────")
        print(f"  MAX_PARALLEL_AGENTS = {MAX_PARALLEL_AGENTS}\n")

        lease_results = []
        for i, (tid, name) in enumerate(zip(task_ids, task_names)):
            try:
                ok = lease_task(conn, tid, f"agent-{i + 1}")
                lease_results.append("ok")
                check(f"lease #{i + 1} ({name})", ok, "SUCCESS")
            except RuntimeError as e:
                lease_results.append("blocked")
                check(f"lease #{i + 1} ({name})", True, f"BLOCKED — {e}")

        successes = lease_results.count("ok")
        blocked = lease_results.count("blocked")
        check(
            "gate allowed exactly MAX_PARALLEL_AGENTS",
            successes == MAX_PARALLEL_AGENTS,
            f"{successes} leased",
        )
        check(
            "gate blocked the rest",
            blocked == len(task_ids) - MAX_PARALLEL_AGENTS,
            f"{blocked} blocked",
        )

    except Exception as exc:
        print(f"\nUNEXPECTED ERROR: {exc}")
        results.append(("unexpected exception", False))
    finally:
        if conn:
            conn.close()
        db_path.unlink(missing_ok=True)

    print("\n── Summary ───────────────────────────────────────────────────")
    for label, ok in results:
        print(f"  {'✓' if ok else '✗'}  {label}")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n  {passed}/{total} checks passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
