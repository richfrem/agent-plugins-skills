#!/usr/bin/env python3
"""Short CLI entry point: `python3 -m control_plane <verb> ...` (B18)."""

from __future__ import annotations

import sys
from pathlib import Path

_scripts_dir = str(Path(__file__).resolve().parent.parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

from agent_control import main

if __name__ == "__main__":
    main()
