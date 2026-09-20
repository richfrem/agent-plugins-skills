#!/usr/bin/env python3
"""
edge_matrix.py
==============

Purpose:
    Classify every transition edge in the live registry by WHO runs it, using the
    human's three classes (start-here-cleanup, ledger item 19):
      AGENT - the agent runs it once the human said "go" in chat (their words go in
              --human-confirmed: the pipeline blocks every unsigned edge without it); no question.
      SOFT  - the human approves in chat, then the AGENT runs it.
      HARD  - the agent cannot run it (cryptographic signature, or a human-only
              record that repo policy reserves to the human).
    The class is DERIVED from fields the registry already has (authorized_actor,
    requires_cryptographic_proof, human_questions); nothing is hand-maintained twice.

Key Input Dependencies:
    - control_plane/transition_templates.yaml (via TransitionRegistry)

Usage:
    python3 plugins/agent-agentic-os/scripts/control_plane/edge_matrix.py > edge-matrix.md

Index:
    - classify_edge(template) -- (run_by, basis, why) for one template
    - build_edge_matrix(registry) -- one row dict per registry template
    - render_markdown(rows) -- markdown table with plain-words instructions
    - main() -- CLI entry point, prints the markdown table
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_scripts_dir = str(Path(__file__).resolve().parent.parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from control_plane.registry import (
    TransitionRegistry,
    classify_edge,
    EXECUTION_CLASS_AGENT as AGENT,
    EXECUTION_CLASS_SOFT as SOFT,
    EXECUTION_CLASS_HARD as HARD,
    EXECUTION_CLASS_INSTRUCTIONS as INSTRUCTION,
)


def build_edge_matrix(registry: Optional[TransitionRegistry] = None) -> List[Dict[str, str]]:
    """Return one row per template in the registry (default: the live registry)."""
    registry = registry or TransitionRegistry.load_default()
    rows: List[Dict[str, str]] = []
    for template in registry.get_all_templates():
        run_by, basis, why = classify_edge(template)
        rows.append({
            "transition_id": template.transition_id,
            "from_state": template.from_state,
            "to_state": template.to_state,
            "run_by": run_by,
            "basis": basis,
            "why": why,
        })
    return rows


def render_markdown(rows: List[Dict[str, str]]) -> str:
    """Render the matrix as a markdown table plus the plain-words legend."""
    lines = ["# Edge matrix: who runs each transition", "", "Legend:"]
    lines.extend(f"- **{name}**: {text}" for name, text in INSTRUCTION.items())
    lines.extend(["", "| Transition | From | To | Who | Basis | Why |", "|---|---|---|---|---|---|"])
    for row in rows:
        lines.append(
            f"| {row['transition_id']} | {row['from_state']} | {row['to_state']} | "
            f"{row['run_by']} | {row['basis']} | {row['why']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    """Print the edge matrix for the live registry."""
    sys.stdout.write(render_markdown(build_edge_matrix()))


if __name__ == "__main__":
    main()
