---
concept: fix-1-literal-n-chars-write-back-immediately-so-json-parse-can-proceed
source: plugin-code
source_file: agent-scaffolders/scripts/fix_plugin_load_errors.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.829223+00:00
cluster: hooks
content_hash: 3b8f8c97459e520c
---

# Fix 1: literal \n chars (write back immediately so JSON parse can proceed)

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
            if ha

*(content truncated)*

## See Also

- [[1-parse-the-hook-payload]]
- [[1-test-magic-bytes-to-ensure-puppeteer-didnt-silently-write-a-text-error]]
- [[add-the-parent-directory-to-syspath-so-we-can-import-parserpy]]
- [[add-the-scripts-directory-so-we-can-import-rlm-config]]
- [[1-basic-summarize-all-documents]]
- [[1-check-env]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/fix_plugin_load_errors.py`
- **Indexed:** 2026-04-27T05:21:03.829223+00:00
