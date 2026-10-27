#!/usr/bin/env python
"""
scaffold_hook.py
=====================================

Purpose:
    Adds an event-driven hook to an APM-native plugin: merges an entry into
    <plugin-root>/.apm/hooks/hooks.json (canonical {"hooks": {Event: [{matcher, hooks: [...]}]}}
    format) and writes an executable, harness-neutral command handler stub with a silent
    project-context guard (SF-11).

Layer: Meta-Execution

Usage:
    python scaffold_hook.py --event PreToolUse --name check-command --plugin-root plugins/<plugin>

Key Input Dependencies:
    - validate_hook_schema.py (VALID_EVENTS)
    - json, argparse, pathlib (standard library)
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_hook_schema import VALID_EVENTS  # noqa: E402

HANDLER_STUB = '''#!/usr/bin/env python3
"""
{name}.py - {event} hook handler.

Exits silently (0) when the repository is not initialised so the hook never blocks other work.
Follows SF-11: uses Path(__file__).resolve() for sibling files and harness-neutral context/ for state.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    """Run the hook; return 0 to allow, non-zero (2) to block (see hooks-spec.md for exit codes)."""
    root = Path.cwd()
    if not (root / "context").is_dir():
        return 0
    _payload = sys.stdin.read()
    # TODO: implement the check; keep it fast (synchronous hooks block the agent loop).
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def build_command(name: str, rel_hooks_dir: str = ".apm/hooks") -> str:
    """Cross-platform command anchored on CLAUDE_PLUGIN_ROOT (python3 first, python as fallback)."""
    script = f'"${{CLAUDE_PLUGIN_ROOT}}/{rel_hooks_dir}/{name}.py"'
    return f"python3 {script} || python {script}"


def scaffold(event: str, name: str, plugin_root: Path, matcher: str, action: str) -> Path:
    """Merge a hook entry into .apm/hooks/hooks.json and write the handler stub; return the hooks.json path."""
    legacy_hooks_dir = plugin_root / "hooks"
    apm_hooks_dir = plugin_root / ".apm" / "hooks"
    if legacy_hooks_dir.is_dir() and not (plugin_root / ".apm").is_dir():
        hooks_dir = legacy_hooks_dir
        rel_hooks_dir = "hooks"
    else:
        hooks_dir = apm_hooks_dir
        rel_hooks_dir = ".apm/hooks"

    hooks_dir.mkdir(parents=True, exist_ok=True)
    hooks_file = hooks_dir / "hooks.json"
    data = {"hooks": {}}
    if hooks_file.exists():
        loaded = json.loads(hooks_file.read_text(encoding="utf-8") or "{}")
        data = loaded if "hooks" in loaded else {"hooks": loaded}
    handler = (
        {"type": action, "command": build_command(name, rel_hooks_dir)}
        if action == "command"
        else {"type": action, "prompt": "Add prompt here"}
    )
    data["hooks"].setdefault(event, []).append({"matcher": matcher, "hooks": [handler]})
    hooks_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    script = hooks_dir / f"{name}.py"
    if action == "command" and not script.exists():
        script.write_text(HANDLER_STUB.format(name=name, event=event), encoding="utf-8")
        try:
            script.chmod(0o755)
        except OSError:
            pass
    return hooks_file


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Scaffold a plugin hook.")
    parser.add_argument("--event", required=True, help="Lifecycle event, e.g. PreToolUse")
    parser.add_argument("--name", required=True, help="Handler script name (kebab-case, no extension)")
    parser.add_argument("--plugin-root", default=".", help="Plugin root directory (default: current directory)")
    parser.add_argument("--matcher", default="", help="Tool matcher regex; empty matches every tool event")
    parser.add_argument("--action", default="command", choices=["command", "prompt"])
    args = parser.parse_args()
    if args.event not in VALID_EVENTS:
        print(f"Error: unknown event '{args.event}'. Valid: {', '.join(sorted(VALID_EVENTS))}", file=sys.stderr)
        return 2
    hooks_file = scaffold(args.event, args.name, Path(args.plugin_root), args.matcher, args.action)
    rel_script = hooks_file.parent / f"{args.name}.py"
    print(f"Success: hook '{args.name}' added for {args.event} in {hooks_file}")
    print(f"Next: implement {rel_script}, then run validate_hook_schema.py and hook_linter.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
