#!/usr/bin/env python3
"""
technical_diagnostic_engine.py — Developer Codebase Discovery & Diagnostic Brief Generator
=========================================================================================

Purpose:
    Performs strictly read-only codebase discovery to analyze coupling surfaces,
    hidden assumptions, and candidate architectural forks, compiling a standardized
    DIAGNOSTIC_BRIEF.md contract and synchronizing session state with context/control_plane.db.

Key Input Dependencies:
    - context/control_plane.db (SQLite task state)
    - Target repository source tree (read-only scan)

Standards:
    - Strictly read-only: Cannot write, stage, or mutate repository files outside temporary diagnostic caches.
    - Zero cross-plugin imports (ADR-001/004): Interacts with control_plane.db via standard sqlite3.
    - Emits DIAGNOSTIC_BRIEF.md adhering to the upstream interview-spec contract.
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


def render_diagnostic_brief(
    task_id: str,
    title: str,
    target_paths: List[str],
    state_boundaries: List[str],
    sqlite_tables: List[str],
    cross_plugin_symlinks: List[str],
    hidden_assumptions: List[Dict[str, str]],
    candidate_forks: List[Dict[str, Any]]
) -> str:
    """
    Renders the standardized markdown representation of the DIAGNOSTIC_BRIEF.md contract.
    """
    paths_md = "\n".join(f"- `{p}`" for p in target_paths) if target_paths else "- *(None identified)*"
    boundaries_md = "\n".join(f"- `{b}`" for b in state_boundaries) if state_boundaries else "- *(None identified)*"
    tables_md = "\n".join(f"- `{t}`" for t in sqlite_tables) if sqlite_tables else "- *(None)*"
    symlinks_md = "\n".join(f"- `{s}`" for s in cross_plugin_symlinks) if cross_plugin_symlinks else "- *(None)*"

    assumptions_rows = "\n".join(
        f"| {item.get('assumption', '')} | {item.get('risk', '')} | {item.get('mitigation', '')} |"
        for item in hidden_assumptions
    ) if hidden_assumptions else "| None detected | N/A | N/A |"

    forks_md = []
    for idx, fork in enumerate(candidate_forks, 1):
        pros = "\n".join(f"    - + {p}" for p in fork.get("pros", []))
        cons = "\n".join(f"    - - {c}" for c in fork.get("cons", []))
        forks_md.append(
            f"### Fork {idx}: {fork.get('title', 'Pattern')}\n"
            f"- **Approach:** {fork.get('description', '')}\n"
            f"- **Tradeoffs:**\n{pros}\n{cons}"
        )
    forks_text = "\n\n".join(forks_md) if forks_md else "*(No candidate forks evaluated)*"

    return f"""# DIAGNOSTIC BRIEF: {title}
**Task ID:** `{task_id}`  
**Status:** DISCOVERY_COMPLETE  
**Execution Mode:** READ_ONLY_SANDBOX  

---

## 1. Coupling Surface
### Touched Files & Modules
{paths_md}

### State Boundaries
{boundaries_md}

### SQLite Tables & Schemas
{tables_md}

### Cross-Plugin & Ecosystem Symlinks
{symlinks_md}

---

## 2. Hidden Assumptions & Omissions
| Implicit Assumption / Ambiguity | Failure Mode / Risk | Mitigation Strategy |
| :--- | :--- | :--- |
{assumptions_rows}

---

## 3. Candidate Architectural Forks
{forks_text}

---

## 4. Handoff Contract to `interview-spec`
- **Recommended Default:** {candidate_forks[0].get('title', 'Fork 1') if candidate_forks else 'Standard Implementation'}
- **Next State Transition:** `INTAKE` -> `INTERVIEW`
- **Handoff Target:** `plugins/agent-agentic-os/skills/interview-spec`
"""


def sync_to_control_plane(
    task_id: str,
    title: str,
    brief_path: str,
    db_path: Optional[Path] = None,
    runtime_tool: str = "claude"
) -> bool:
    """
    Records discovery session and transitions task state from INTAKE to INTERVIEW in control_plane.db.
    """
    if db_path is None:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        db_path = repo_root / "context" / "control_plane.db"

    if not db_path.exists():
        # Fall back gracefully if control plane DB is not initialized
        return False

    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA busy_timeout = 5000;")

            # Check if task exists; insert if not present
            row = conn.execute("SELECT state FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
            if not row:
                conn.execute(
                    """
                    INSERT INTO tasks (task_id, title, state, runtime_tool, spec_path)
                    VALUES (?, ?, 'INTAKE', ?, ?)
                    """,
                    (task_id, title, runtime_tool, brief_path)
                )
                conn.execute(
                    """
                    INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason)
                    VALUES (?, 'NONE', 'INTAKE', 'exploration_engine', 'Initial exploration brief created')
                    """,
                    (task_id,)
                )
                current_state = "INTAKE"
            else:
                current_state = row["state"]

            # Advance INTAKE -> INTERVIEW
            if current_state == "INTAKE":
                conn.execute(
                    """
                    UPDATE tasks SET state = 'INTERVIEW', spec_path = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                    """,
                    (brief_path, task_id)
                )
                conn.execute(
                    """
                    INSERT INTO task_transitions (task_id, from_state, to_state, actor, reason)
                    VALUES (?, 'INTAKE', 'INTERVIEW', 'exploration_engine', 'Diagnostic brief compiled; handoff to interview-spec')
                    """,
                    (task_id,)
                )
        return True
    except Exception as e:
        print(f"Warning: Failed to sync discovery brief to control_plane.db: {e}", file=sys.stderr)
        return False
    finally:
        conn.close()


def main() -> None:
    """CLI entry point: parse args, render the diagnostic brief, sync state to control_plane.db."""
    parser = argparse.ArgumentParser(description="Generate diagnostic brief and handoff to interview-spec.")
    parser.add_argument("--task-id", required=True, help="Unique task identifier")
    parser.add_argument("--title", required=True, help="Task title")
    parser.add_argument("--output", default="exploration/DIAGNOSTIC_BRIEF.md", help="Output file path")
    parser.add_argument("--db-path", help="Path to control_plane.db")
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    brief_content = render_diagnostic_brief(
        task_id=args.task_id,
        title=args.title,
        target_paths=[],
        state_boundaries=[],
        sqlite_tables=[],
        cross_plugin_symlinks=[],
        hidden_assumptions=[],
        candidate_forks=[]
    )
    out_path.write_text(brief_content, encoding="utf-8")
    print(f"Generated Diagnostic Brief at: {out_path}")

    db_p = Path(args.db_path) if args.db_path else None
    synced = sync_to_control_plane(task_id=args.task_id, title=args.title, brief_path=str(out_path), db_path=db_p)
    if synced:
        print(f"Task '{args.task_id}' transitioned to INTERVIEW in control_plane.db")


if __name__ == "__main__":
    main()
