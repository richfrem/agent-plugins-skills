#!/usr/bin/env python
"""
fix_plugin_load_errors.py
=========================

Purpose:
    Auto-fixes common Claude Code plugin load errors discovered in production.
    Run this before pushing a plugin to GitHub to prevent cache-level errors.

Fixes applied:
    1. plugin.json: removes banned fields (skills, agents, hooks, commands)
       Claude Code's validator rejects these -- auto-discovery handles them.
    2. hooks.json: fixes literal \\n chars (not real newlines) -> real newlines
       Occurs when Python json.dumps writes to a file without proper encoding.
    3. hooks.json: fixes empty {} -> { "hooks": {} }
       Plain {} parses but Claude Code expects a "hooks" wrapper key.
    4. hooks.json: fixes array [] -> { "hooks": {} }
       Claude Code expects an object, not an array.
    5. hooks.json: fixes old flat format { "EventName": [...] }
       -> correct nested { "hooks": { "EventName": [...] } }
    6. lsp.json / .mcp.json: fixes literal \\n chars -> real newlines
    7. SKILL.md: removes comment lines before opening --- frontmatter
       Claude Code fails to parse frontmatter if any non-frontmatter content precedes it.

NOTE: Claude Code scans ALL cached plugin versions under ~/.claude/plugins/cache/,
      not just the active installPath. Fix source files, then reinstall to repopulate cache.

Usage:
    python fix_plugin_load_errors.py <plugin_root>
    python fix_plugin_load_errors.py .
"""
import sys
import json
from pathlib import Path

BANNED_PLUGIN_JSON_FIELDS = {"skills", "agents", "hooks", "commands"}

VALID_EVENTS = {
    "PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop",
    "SubagentStop", "SessionStart", "SessionEnd", "PreCompact", "Notification",
}


def fix_literal_newlines(content: str) -> tuple[str, bool]:
    """Replace literal \\n sequences with real newlines, but only if the file
    appears to be a single-line JSON blob (no real newlines present)."""
    if r"\n" in content and "\n" not in content:
        return content.replace(r"\n", "\n"), True
    return content, False


def fix_plugin_json(path: Path) -> list[str]:
    fixes = []
    try:
        text = path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (json.JSONDecodeError, OSError) as e:
        return [f"ERROR reading {path}: {e}"]

    removed = []
    for field in sorted(BANNED_PLUGIN_JSON_FIELDS):
        if field in data:
            del data[field]
            removed.append(field)

    if removed:
        path.write_text(json.dumps(data, indent=4) + "\n", encoding="utf-8")
        fixes.append(f"plugin.json: removed banned field(s): {', '.join(removed)}")
    return fixes


def fix_hooks_json(path: Path) -> list[str]:
    fixes = []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"ERROR reading {path}: {e}"]

    # Fix 1: literal \n chars (write back immediately so JSON parse can proceed)
    fixed_raw, changed = fix_literal_newlines(raw)
    if changed:
        raw = fixed_raw
        fixes.append(f"{path.name}: fixed literal \\n chars -> real newlines")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        if fixes:
            path.write_text(raw, encoding="utf-8")
        return fixes + [f"ERROR: {path.name} still invalid JSON after newline fix: {e}"]

    modified = False

    # Fix 2: array [] -> { "hooks": {} }
    if isinstance(data, list):
        data = {"hooks": {}}
        fixes.append(f"{path.name}: fixed array [] -> {{\"hooks\": {{}}}}")
        modified = True

    elif isinstance(data, dict):
        # Fix 3: empty {} -> { "hooks": {} }
        if len(data) == 0:
            data = {"hooks": {}}
            fixes.append(f'{path.name}: fixed empty {{}} -> {{"hooks": {{}}}}')
            modified = True

        # Fix 4: old flat format { "EventName": [...] } missing "hooks" wrapper
        elif "hooks" not in data:
            has_event_keys = any(k in VALID_EVENTS for k in data)
            if has_event_keys:
                data = {"hooks": data}
                fixes.append(
                    f"{path.name}: wrapped flat event map in {{\"hooks\": {{...}}}}"
                )
                modified = True
            else:
                # Unrecognised root keys that are also not event names -- flag it
                unknown = [k for k in data if k not in VALID_EVENTS]
                if unknown:
                    fixes.append(
                        f"WARNING {path.name}: unrecognised root keys {unknown} "
                        "-- expected \"hooks\" wrapper or event name keys"
                    )

    if modified or (fixes and "literal" in fixes[-1]):
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return fixes


def fix_json_newlines(path: Path) -> list[str]:
    """Fix literal \\n in lsp.json, .mcp.json, or any JSON file."""
    fixes = []
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"ERROR reading {path}: {e}"]

    fixed, changed = fix_literal_newlines(raw)
    if changed:
        path.write_text(fixed, encoding="utf-8")
        fixes.append(f"{path.name}: fixed literal \\n chars -> real newlines")
    return fixes


def fix_skill_md(path: Path) -> list[str]:
    """Remove comment or blank lines before the opening --- frontmatter fence."""
    fixes = []
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        return [f"ERROR reading {path}: {e}"]

    lines = content.splitlines(keepends=True)
    first_fence = next((i for i, l in enumerate(lines) if l.strip() == "---"), None)

    if first_fence is None or first_fence == 0:
        return fixes  # Already starts with --- or has no frontmatter

    before = lines[:first_fence]
    comment_or_blank = all(
        l.strip().startswith("#") or l.strip() == "" for l in before
    )
    if comment_or_blank:
        path.write_text("".join(lines[first_fence:]), encoding="utf-8")
        fixes.append(
            f"{path.name}: removed {first_fence} comment/blank line(s) before frontmatter"
        )
    return fixes


def scan_and_fix(plugin_root: Path) -> int:
    all_fixes = []

    # 1. plugin.json
    plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
    if plugin_json.exists():
        all_fixes.extend(fix_plugin_json(plugin_json))

    # 2. hooks.json (anywhere in the plugin tree)
    for hooks_json in plugin_root.rglob("hooks.json"):
        all_fixes.extend(fix_hooks_json(hooks_json))

    # 3. lsp.json and .mcp.json
    for name in ("lsp.json", ".mcp.json"):
        for p in plugin_root.rglob(name):
            all_fixes.extend(fix_json_newlines(p))

    # 4. SKILL.md files
    for skill_md in plugin_root.rglob("SKILL.md"):
        all_fixes.extend(fix_skill_md(skill_md))

    errors = [f for f in all_fixes if f.startswith("ERROR")]
    fixes = [f for f in all_fixes if not f.startswith("ERROR")]
    warnings = [f for f in fixes if f.startswith("WARNING")]
    applied = [f for f in fixes if not f.startswith("WARNING")]

    if applied:
        print(f"Applied {len(applied)} fix(es):")
        for f in applied:
            print(f"  \u2705 {f}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  \u26a0\ufe0f  {w}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  \u274c {e}")
    if not all_fixes:
        print("\u2705 No load-error issues found.")

    return 1 if errors else 0


def main() -> None:
    plugin_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    if not plugin_root.is_dir():
        print(f"\u274c Not a directory: {plugin_root}")
        sys.exit(1)

    print(f"\U0001f50d Scanning for load errors in: {plugin_root.resolve()}\n")
    rc = scan_and_fix(plugin_root)
    sys.exit(rc)


if __name__ == "__main__":
    main()
