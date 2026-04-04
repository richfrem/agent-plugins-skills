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
            for pattern in patterns:
                if re.search(pattern, line):
                    return True
    return False

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
            ".claude", ".claude-plugin", ".windsurf", ".kittify", 
            "plugin-research", "temp", "ADRs", "agent-rules-to-add-when-needed"
        )):
            continue
            
        if path.name in (
            "portability-audit-report.md", "tuning_metrics.md", "files_with_issues.txt",
            "CLAUDE.md", "INSTALL.md", "README.md", "bootstrap.py", 
            "broken_symlinks_repair_report.md"
        ):
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            continue

        file_issues = []
        for i, line in enumerate(lines, 1):
            if "plugins/" in line or "/Users/" in line:
                if plugins_pattern.search(line) or users_pattern.search(line):
                    if not is_whitelisted(line, str(path), global_patterns, file_specific_patterns):
                        file_issues.append({
                            "line_num": i,
                            "content": line.strip()[:200]  # Cap length for report readability
                        })
                        issue_count += 1
                        
        if file_issues:
            # Try to get relative path if possible
            try:
                display_path = str(path.relative_to(Path.cwd()))
            except ValueError:
                display_path = str(path)
            issues[display_path] = file_issues
            
    return issues, issue_count

def write_report(issues, report_path: Path):
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Portability Audit Report\n\n")
        
        if not issues:
            f.write("✅ **All files strictly adhere to the Zero Reference Policy.**\n")
            return
            
        f.write("> ⚠️ **Action Required**: The following files contain hardcoded `plugins/` references or absolute machine paths.\n")
        f.write("> The `fix-plugin-paths` skill must run until this report returns zero violations by either neutralizing the path or updating `plugin_paths_whitelist.json`.\n\n")
        
        for file_path in sorted(issues.keys()):
            f.write(f"### [ ] {file_path}\n")
            for issue in issues[file_path]:
                f.write(f"- Line `{issue['line_num']}`: `{issue['content']}`\n")
            f.write("\n")

def main():
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    whitelist_path = Path(__file__).resolve().parent / "plugin_paths_whitelist.json"
    report_path = Path(__file__).resolve().parent / "portability-audit-report.md"
    
    global_patterns, file_specific_patterns = load_whitelist(whitelist_path)
    
    issues, count = audit_directory(target_dir, global_patterns, file_specific_patterns)
    write_report(issues, report_path)
    
    if count == 0:
        print(f"✅ Clean! 0 violations found.")
    else:
        print(f"❌ Found {count} issues across {len(issues)} files.")
        print(f"Report generated at: {report_path.absolute()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
