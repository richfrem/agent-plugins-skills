#!/usr/bin/env python3
"""Compatibility shim: the guards moved to the cli-agent skill (the executor owns launch checks).

Resolves the sibling cli-agent installation; fails loudly if it is absent. No logic lives here.
"""
import importlib.util, sys
from pathlib import Path

_CANDIDATES = [Path(__file__).resolve().parents[2] / "cli-agent" / "scripts" / "dispatch_guard.py"]
for _root in (Path.home() / ".claude" / "skills", Path.home() / ".agents" / "skills", Path(".claude/skills"), Path(".agents/skills")):
    _CANDIDATES.append(_root / "cli-agent" / "scripts" / "dispatch_guard.py")
_found = next((c for c in _CANDIDATES if c.is_file()), None)
if _found is None:
    raise SystemExit("dispatch_guard moved to the cli-agent skill, which is not installed; install agent-orchestration")
_spec = importlib.util.spec_from_file_location("_cli_agent_dispatch_guard", _found)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
globals().update({k: v for k, v in vars(_mod).items() if not k.startswith("__")})

if __name__ == "__main__":
    sys.exit(_mod.main())
