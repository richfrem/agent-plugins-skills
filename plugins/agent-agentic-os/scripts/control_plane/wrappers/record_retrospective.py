#!/usr/bin/env python3
"""Fixed-identity wrapper for recording a task retrospective draft or completion."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_scripts_dir = str(Path(__file__).resolve().parent.parent.parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from agent_control import ControlPlane, PhaseCapabilityDenied


ACTION_IDENTITY = "retrospective_capture"


def record_retrospective(
    task_id: str,
    entry: Dict[str, Any],
    follow_ups: Optional[List[Dict[str, Any]]] = None,
    control_plane: Optional[ControlPlane] = None,
) -> Dict[str, Any]:
    """Persist one retrospective record after verifying RETROSPECTIVE occupancy."""
    cp = control_plane or ControlPlane()
    cap = cp.verify_phase_capability(task_id, ACTION_IDENTITY)
    if cap.current_state != "RETROSPECTIVE":
        raise PhaseCapabilityDenied("Retrospective capture is only authorized in RETROSPECTIVE state.")
    cp.save_retrospective(task_id, entry, follow_ups or [])
    return {
        "status": "RECORDED",
        "task_id": task_id,
        "transition_id": cap.transition_id,
        "action_identity": ACTION_IDENTITY,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Fixed-identity retrospective capture wrapper")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--entry", required=True, help="JSON object containing retrospective fields")
    parser.add_argument("--follow-ups", default="[]", help="JSON array of follow-up objects")
    args = parser.parse_args()
    try:
        entry = json.loads(args.entry)
        follow_ups = json.loads(args.follow_ups)
        if not isinstance(entry, dict) or not isinstance(follow_ups, list):
            raise ValueError("--entry must be a JSON object and --follow-ups must be a JSON array")
        print(json.dumps(record_retrospective(args.task_id, entry, follow_ups), indent=2))
    except PhaseCapabilityDenied as exc:
        print(f"CAPABILITY DENIED: {exc}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
