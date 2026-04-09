#!/usr/bin/env python3
# Thin wrapper — delegates to the canonical implementation in scripts/
import sys
import os
from pathlib import Path

# Resolve CLAUDE_PLUGIN_ROOT or fall back to two levels up from this file
plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).parent.parent.parent))
target = plugin_root / "scripts" / "post_run_metrics.py"

if not target.exists():
    print(f"ERROR: post_run_metrics.py not found at {target}", file=sys.stderr)
    sys.exit(1)

# Re-exec the real script so it runs in its own context
os.execv(sys.executable, [sys.executable, str(target)] + sys.argv[1:])
