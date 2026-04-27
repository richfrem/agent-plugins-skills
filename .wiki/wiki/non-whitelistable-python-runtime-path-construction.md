---
concept: non-whitelistable-python-runtime-path-construction
source: plugin-code
source_file: agent-scaffolders/scripts/audit_plugin_paths.py
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.239376+00:00
cluster: return
content_hash: 625fa8b519b215ff
---

# Non-whitelistable: Python runtime path construction.

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

<!-- Source: plugin-code/agent-scaffolders/scripts/audit_plugin_paths.py -->
#!/usr/bin/env python
import sys
import re
import json
from pathlib import Path

def load_whitelist(whitelist_path: Path):
    if not whitelist_path.exists():
        return [], {}
    try:
        with open(whitelist_path, 'r') as f:
            data = json.load(f)
        return data.get("global_patterns", []), data.get("file_specific_patterns", {})
    except Exception as e:
        print(f"Error loading whitelist: {e}")
        return [], {}

def is_whitelisted(line, file_path_str, global_patterns, file_specific_patterns):
    for pattern in global_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True
            
    for specific_path, patterns in file_specific_patterns.items():
        if specific_path in file_path_str:
            for pattern in patterns:
                if re.search(pattern, line):
                    return True
    return False

# Non-whitelistable: Python runtime path construction.
# Catches lines in .py files where a variable is assigned a Path() that reaches into
# plugins/<name>. These are always portability violations — a whitelist entry cannot
# excuse them because they indicate actual code referencing the source repo layout at
# runtime (e.g. BRIDGE_INSTALLER = PROJECT_ROOT / "plugins/plugin-manager/scripts/...").
_RUNTIME_PATH_PATTERN = re.compile(
    r'(?:PROJECT_ROOT|\bROOT\b|SCRIPT_DIR|Path\s*\(\s*__file__\s*\)'
    r'|path\.parents?\[\d+\])'
    r'[^\n#]*?["\']plugins/[a-zA-Z0-9_-]'
)

def _is_comment_or_docstring(line: str) -> bool:
    """Rough heuristic: skip pure-comment lines and lines that are part of a docstring."""
    stripped = line.strip()
    return stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''")

def audit_runtime_paths(target_dir: Path):
    """Secondary non-whitelistable pass: Python runtime Path() constructions.
    
    Returns (issues_dict, count) where issues are CRITICAL portability violations
    that bypass the whitelist entirely.
    """
    issues = {}
    count = 0

    for path in target_dir.rglob("*.py"):
        if not path.is_file():
            continue
        if any(ignore in path.parts for ignore in (
            ".agents", ".agent", ".git", "__pycache__", "node_modules",
            ".claude", ".claude-plugin", ".windsurf", ".kittify",
            "plugin-research", "temp", "ADRs", "agent-rules-to-add-when-needed"
        )):
            continue
        if path.name in ("bootstrap.py", "audit_plugin_paths.py"):
            continue

        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            continue

        file_issues = []
        for i, line in enumerate(lines, 1):
            if _is_comment_or_docstring(line):
                continue
            if _RUNTIME_PATH_PATTERN.search(line):
                file_issues.append({
                    "line_num": i,
                    "content": line.strip()[:200],
                    "severity": "CRITICAL"
                })
                count += 1

        if file_issues:
            try:
                display_path = str(path.relative_to(Path.cwd()))
            except ValueError:
                display_path = str(path)
            issues[display_path] = file_issues

    return issues, count


def audit_directory(target_dir: Path, global_patterns, file_specific_patterns):
    issues = {}
    issue_count = 0
    
    plugins_pattern = re.compile(r'plugins/[a-zA-Z0-9_-]+')
    users_pattern = re.compile(r'/Users/[a-zA-Z0-9_-]+')
    exts = {".md", ".py"}
    
    for path in target_dir.rglob("*"):
        if not path.is_file() or path.suffix not in exts:
            continue
            
        # Ignore known framework caches, user experiments, and metadata registries
        if any(ignore in path.parts for ignore in (
            ".agents", ".agent", ".git", "__pycache__", "node_modules", 
            ".claude", ".claude-plugin", ".windsur

*(content truncated)*

<!-- Source: plugin-code/spec-kitty-plugin/.agents/skills/fix-plugin-paths/scripts/audit_plugin_paths.py -->
#!/usr/bin/env python3
import sys
import re
import json
from pathlib import Path

def load_whitelist(whitelist_path: Path):
    if not whitelist_path.exists():
        return [], {}
    try:
        with open(whitelist_path, 'r') as f:
            data = json.load(f)
        return data.get("global_patterns", []), data.get("file_specific_patterns", {})
    except Exception as e:
        print(f"Error loading whitelist: {e}")
        return [], {}

def is_whitelisted(line, file_path_str, global_patterns, file_specific_patterns):
    for pattern in global_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True
            
    for specific_path, patterns in file_specific_patterns.items():
        if specific_path in file_path_str:
            for patt

*(combined content truncated)*

## See Also

- [[absolute-path-prefixes-that-should-never-be-written-to]]
- [[add-script-dir-to-path-to-import-plugin-inventory]]
- [[atomically-replace-an-existing-path-with-a-new-symlink-pointing-to-src]]
- [[broken-path-string]]
- [[path-bootstrap]]
- [[path-reference-auditor]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-scaffolders/scripts/audit_plugin_paths.py`
- **Indexed:** 2026-04-27T05:21:04.239376+00:00
