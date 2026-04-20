#!/usr/bin/env python
"""
inventory_plugin.py (CLI)
=====================================

Purpose:
    Deterministically inventories all files in a plugin or plugin collection,
    classifying each by type, counting lines, and detecting compliance issues.

Layer: Meta-Execution

Usage Examples:
    pythonentory_plugin.py --path <plugin-dir> --format json
    pythonentory_plugin.py --path <plugin-dir> --format markdown
    pythonentory_plugin.py --path <plugin-dir> --format checklist

CLI Arguments:
    --path: The path to the plugin or plugin collection directory.
    --format: Output format (json, markdown, checklist). Default: markdown.
    --recursive: If set, treat path as a collection and inventory each subdirectory.
    --no-security: Disable deterministic security scans (enabled by default).

Output:
    Structured inventory to stdout in the requested format.

Script Dependencies:
    None (standard library only)

Consumed by:
    - analyze-plugin (Agent Skill)
    - mine-plugins (Command)
"""
import argparse
import json
import os
import re
import sys


# ── File Type Classification ──────────────────────────────────────────

FILE_TYPE_MAP = {
    "SKILL.md": "skill",
    "README.md": "readme",
    "CONNECTORS.md": "connectors",
    "QUICKREF.md": "quickref",
    "CLAUDE.md": "claude-config",
    "plugin.json": "manifest",
    "marketplace.json": "marketplace",
    ".mcp.json": "mcp-config",
    "mcp.json": "mcp-config",
    "hooks.json": "hooks-config",
    "lsp.json": "lsp-config",
    "requirements.txt": "dependencies",
    "requirements.in": "dependencies",
}

EXT_TYPE_MAP = {
    ".md": "document",
    ".py": "script",
    ".json": "config",
    ".yaml": "config",
    ".yml": "config",
    ".html": "artifact-template",
    ".mmd": "diagram",
    ".png": "image",
    ".jpg": "image",
    ".txt": "text",
    ".jinja": "template",
}

COMMANDS_DIR = "commands"
REFERENCES_DIR = "references"
REFERENCE_DIR = "reference"
SCRIPTS_DIR = "scripts"
EXAMPLES_DIR = "examples"
TEMPLATES_DIR = "templates"
AGENTS_DIR = "agents"
SETTINGS_DIR = "settings"


def classify_file(filepath: str, relpath: str) -> str:
    """Classify a file by its type based on name, extension, and location."""
    basename = os.path.basename(filepath)
    _, ext = os.path.splitext(basename)
    parts = relpath.split(os.sep)

    # Check exact filename matches first
    if basename in FILE_TYPE_MAP:
        return FILE_TYPE_MAP[basename]

    # Check location-based classification
    if COMMANDS_DIR in parts:
        return "command"
    if AGENTS_DIR in parts:
        return "agent"
    if REFERENCES_DIR in parts or REFERENCE_DIR in parts:
        return "reference"
    if SCRIPTS_DIR in parts:
        return "script"
    if EXAMPLES_DIR in parts:
        return "example"
    if TEMPLATES_DIR in parts:
        return "template"
    if SETTINGS_DIR in parts:
        return "settings"

    # Fall back to extension
    if ext in EXT_TYPE_MAP:
        return EXT_TYPE_MAP[ext]

    return "other"


def count_lines(filepath: str) -> int:
    """Count lines in a text file. Returns -1 for binary files."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="strict") as f:
            return sum(1 for _ in f)
    except (UnicodeDecodeError, ValueError):
        return -1


def detect_issues(filepath: str, relpath: str, file_type: str, line_count: int) -> list[str]:
    """Detect Open Standards compliance issues."""
    issues = []
    basename = os.path.basename(filepath)

    # SKILL.md over 500 lines
    if basename == "SKILL.md" and line_count > 500:
        issues.append(f"SKILL.md exceeds 500 lines ({line_count} lines)")

    # Bash or PowerShell scripts
    if basename.endswith(".sh"):
        issues.append("Bash script detected — only Python (.py) is allowed")
    if basename.endswith(".ps1"):
        issues.append("PowerShell script detected — only Python (.py) is allowed")

    return issues


# ── Security Scanning ─────────────────────────────────────────────────

CREDENTIAL_PATTERNS = [
    (r"\b(sk-ant-[a-zA-Z0-9\-_]{40,}|sk-proj-[a-zA-Z0-9\-_]{40,}|sk-[a-zA-Z0-9]{40,})\b", "OpenAI/Anthropic API key"),
    (r"ghp_[a-zA-Z0-9]{20,}", "GitHub personal access token"),
    (r"gho_[a-zA-Z0-9]{20,}", "GitHub OAuth token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key ID"),
    (r"xox[bprs]-[a-zA-Z0-9\-]{10,}", "Slack token"),
    (r"glpat-[a-zA-Z0-9\-_]{20,}", "GitLab personal access token"),
    (r"""(?:api[_-]?key|api[_-]?secret|password|secret[_-]?key)\s*[=:]\s*['"][^'"]{8,}['"]""", "Generic hardcoded secret"),
    (r"Bearer\s+[a-zA-Z0-9\-\._~+/]{15,}", "Bearer token"),
]

def run_security_scan(filepath: str, file_type: str, relpath: str) -> list[str]:
    """Run deterministic security checks on files."""
    findings = []
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
            # 1. Hardcoded Credentials (all files)
            for pattern, label in CREDENTIAL_PATTERNS:
                if re.search(pattern, content):
                    findings.append(f"[CRITICAL] Hardcoded credential ({label}) detected in {relpath}")
                    
            # 2. Network Calls & Subprocess (scripts)
            if file_type == "script":
                network_indicators = ["import requests", "urllib", "requests.get", "requests.post", "curl ", "fetch("]
                for ind in network_indicators:
                    if ind in content:
                        findings.append(f"[CRITICAL] Unauthorized network call indicator '{ind}' in {relpath}")
                
                if "import subprocess" in content or "subprocess.call" in content or "subprocess.run" in content:
                    findings.append(f"[ERROR] Subprocess execution detected in {relpath}")
                    
                if "os.environ" in content:
                    findings.append(f"[WARNING] Access to raw environment variables in {relpath}")
                    
            # 3. Hidden LLM Instructions (markdown files)
            if file_type in ["skill", "reference", "readme"]:
                # Only flag HTML comments containing injection-pattern keywords
                html_comments = re.findall(r"<!--(.*?)-->", content, re.DOTALL)
                injection_keywords = ["ignore", "instruction", "system:", "override", "you are", "you must", "disregard", "forget"]
                for comment in html_comments:
                    comment_lower = comment.lower()
                    if any(kw in comment_lower for kw in injection_keywords):
                        findings.append(f"[CRITICAL] Potential instruction injection via HTML comment in {relpath}")
                        break
                    
    except Exception:
        pass
        
    return findings


# ── Plugin Inventory ──────────────────────────────────────────────────

def inventory_directory(path: str, run_security: bool = True) -> tuple[list[dict], list[str], list[str]]:
    """Walk a directory and inventory all files."""
    files = []
    all_issues = []

    for root, dirs, filenames in os.walk(path):
        # Skip hidden directories (like .git)
        dirs[:] = [d for d in dirs if not d.startswith(".") or d == ".claude-plugin"]

        for filename in sorted(filenames):
            # Skip hidden files (except .mcp.json)
            if filename.startswith(".") and filename != ".mcp.json":
                continue

            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, path)
            file_size = os.path.getsize(filepath)
            line_count = count_lines(filepath)
            file_type = classify_file(filepath, relpath)
            issues = detect_issues(filepath, relpath, file_type, line_count)
            security_findings = run_security_scan(filepath, file_type, relpath) if run_security else []

            entry = {
                "path": relpath,
                "type": file_type,
                "lines": line_count,
                "bytes": file_size,
                "issues": issues,
                "security_flags": security_findings,
            }
            files.append(entry)
            all_issues.extend(issues)

    all_security = [flag for f in files for flag in f.get("security_flags", [])]
    return files, all_issues, all_security


def detect_missing_components(path: str, files: list[dict]) -> list[str]:
    """Check for commonly expected components that are missing."""
    warnings = []
    paths = {f["path"] for f in files}
    types = {f["type"] for f in files}

    # Check for plugin manifest
    has_manifest = any(
        f["path"].endswith("plugin.json") and ".claude-plugin" in f["path"]
        for f in files
    )

    # Check for README
    has_readme = "README.md" in {os.path.basename(f["path"]) for f in files}

    # Check for acceptance criteria in skills
    skill_dirs = set()
    for f in files:
        if f["type"] == "skill":
            skill_dir = os.path.dirname(f["path"])
            skill_dirs.add(skill_dir)

    for skill_dir in skill_dirs:
        ac_path = os.path.join(skill_dir, "references", "acceptance-criteria.md")
        if ac_path not in paths:
            skill_name = os.path.basename(skill_dir)
            warnings.append(f"Skill '{skill_name}' missing acceptance-criteria.md")

        refs_dir = os.path.join(skill_dir, "references")
        has_refs = any(p.startswith(refs_dir) for p in paths)
        if not has_refs:
            skill_name = os.path.basename(skill_dir)
            warnings.append(f"Skill '{skill_name}' missing references/ directory")

    if not has_readme:
        warnings.append("Missing README.md")

    return warnings


# ── Output Formatters ─────────────────────────────────────────────────

def format_json(files: list[dict], issues: list[str], warnings: list[str], path: str, security_findings: list[str] | None = None) -> str:
    """Output as structured JSON."""
    summary = {
        "plugin_path": path,
        "total_files": len(files),
        "total_lines": sum(f["lines"] for f in files if f["lines"] >= 0),
        "total_bytes": sum(f["bytes"] for f in files),
        "by_type": {},
        "issues": issues,
        "warnings": warnings,
        "security_flags": security_findings or [],
        "files": files,
    }

    for f in files:
        t = f["type"]
        summary["by_type"][t] = summary["by_type"].get(t, 0) + 1

    return json.dumps(summary, indent=2)


def format_markdown(files: list[dict], issues: list[str], warnings: list[str], path: str, security_findings: list[str] | None = None) -> str:
    """Output as readable markdown."""
    lines = [f"# Plugin Inventory: {os.path.basename(path)}\n"]

    # Summary
    type_counts = {}
    for f in files:
        t = f["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    lines.append(f"**Total files:** {len(files)}")
    lines.append(f"**Total lines:** {sum(f['lines'] for f in files if f['lines'] >= 0):,}")
    lines.append(f"**Total bytes:** {sum(f['bytes'] for f in files):,}\n")

    lines.append("## Files by Type\n")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {c} |")

    lines.append("\n## File Details\n")
    lines.append("| Path | Type | Lines | Size |")
    lines.append("|------|------|-------|------|")
    for f in files:
        size_str = f"{f['bytes']:,}B"
        line_str = str(f["lines"]) if f["lines"] >= 0 else "binary"
        lines.append(f"| `{f['path']}` | {f['type']} | {line_str} | {size_str} |")

    if issues:
        lines.append("\n## ❌ Issues\n")
        for issue in issues:
            lines.append(f"- {issue}")

    if warnings:
        lines.append("\n## ⚠️ Warnings\n")
        for warning in warnings:
            lines.append(f"- {warning}")

    all_security = [flag for f in files for flag in f.get("security_flags", [])]
    if all_security:
        lines.append("\n## 🔴 Security Findings\n")
        for flag in all_security:
            lines.append(f"- {flag}")

    return "\n".join(lines)


def format_checklist(files: list[dict], issues: list[str], warnings: list[str], path: str, security_findings: list[str] | None = None) -> str:
    """Output as markdown checklist with one checkbox per file, grouped by parent directory."""
    lines = [f"# Plugin Review Checklist: {os.path.basename(path)}\n"]

    # Group files by their first directory component
    groups = {}
    for f in files:
        parts = f["path"].split(os.sep)
        if len(parts) > 1:
            group = parts[0]
            # For skills, use skill name as sub-group
            if group == "skills" and len(parts) > 2:
                group = f"skills/{parts[1]}"
        else:
            group = "(root)"
        groups.setdefault(group, []).append(f)

    for group in sorted(groups.keys()):
        group_files = groups[group]
        lines.append(f"\n### {group}\n")
        for f in group_files:
            issue_marker = " ⚠️" if f["issues"] else ""
            line_str = f" ({f['lines']} lines)" if f["lines"] >= 0 else " (binary)"
            lines.append(f"- [ ] `{f['path']}`{line_str}{issue_marker}")

    if warnings:
        lines.append("\n### Compliance Warnings\n")
        for w in warnings:
            lines.append(f"- ⚠️ {w}")

    if issues:
        lines.append("\n### Compliance Errors\n")
        for i in issues:
            lines.append(f"- ❌ {i}")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inventory plugin files with classification and compliance checks."
    )
    parser.add_argument(
        "--path", required=True,
        help="Path to the plugin directory to inventory"
    )
    parser.add_argument(
        "--format", choices=["json", "markdown", "checklist"], default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--recursive", action="store_true",
        help="Treat path as a collection — inventory each subdirectory separately"
    )
    parser.add_argument(
        "--no-security", action="store_true",
        help="Disable deterministic security scans (enabled by default)"
    )

    args = parser.parse_args()
    args.security = not args.no_security

    if not os.path.isdir(args.path):
        print(f"Error: Path '{args.path}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    if args.recursive:
        # Inventory each subdirectory as a separate plugin
        subdirs = sorted([
            d for d in os.listdir(args.path)
            if os.path.isdir(os.path.join(args.path, d)) and not d.startswith(".")
        ])

        all_results = []
        for subdir in subdirs:
            subdir_path = os.path.join(args.path, subdir)
            files, issues, security_findings = inventory_directory(subdir_path, run_security=args.security)
            warnings = detect_missing_components(subdir_path, files)
            all_results.append((subdir, files, issues, warnings, subdir_path, security_findings))

        if args.format == "json":
            combined = []
            for name, files, issues, warnings, p, sf in all_results:
                combined.append({
                    "name": name,
                    "path": p,
                    "total_files": len(files),
                    "issues": issues,
                    "warnings": warnings,
                    "security_flags": sf,
                    "files": files,
                })
            print(json.dumps(combined, indent=2))
        else:
            for name, files, issues, warnings, p, sf in all_results:
                formatter = format_checklist if args.format == "checklist" else format_markdown
                print(formatter(files, issues, warnings, p))
                print("\n---\n")
    else:
        files, issues, security_findings = inventory_directory(args.path, run_security=args.security)
        warnings = detect_missing_components(args.path, files)

        formatters = {
            "json": format_json,
            "markdown": format_markdown,
            "checklist": format_checklist,
        }
        print(formatters[args.format](files, issues, warnings, args.path, security_findings))


if __name__ == "__main__":
    main()
