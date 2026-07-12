#!/usr/bin/env python3
"""
workspace_conventions_auditor.py — Workspace conventions compliance auditor.
===========================================================================

Purpose:
    Audits the workspace (excluding build and temp paths) for compliance with
    coding-conventions.md standards (file headers, docstrings, function lengths).

Layer:
    Plugins / Dev-Utils / Scripts

Key Input Dependencies:
    - .agent/rules/coding-conventions.md (Source of standards definition)

Usage:
    python3 plugins/dev-utils/scripts/workspace_conventions_auditor.py
"""

import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Any

WORKSPACE_ROOT = Path(os.getcwd())

# Directories to exclude from the scan
EXCLUDE_DIRS = {
    "node_modules", "dist", "build", ".git", ".next", "venv", 
    "__pycache__", "out", "coverage", ".agents", "temp", "apm_modules"
}

# File extensions to scan
SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js"}


# External comment: Audit a Python file for standard formatting structure
def scan_python_file(file_path: Path) -> List[str]:
    """Audits a Python file for standards using AST parsing."""
    errors = []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
    except SyntaxError as e:
        return [f"Syntax Error: {e}"]

    # 1. Header checks
    if not docstring:
        errors.append("Missing module-level docstring header.")
    else:
        doc_lower = docstring.lower()
        if "purpose:" not in doc_lower:
            errors.append("Header is missing 'Purpose:' section.")
        if "key input dependencies:" not in doc_lower and "dependencies:" not in doc_lower:
            errors.append("Header is missing 'Key Input Dependencies:' section.")

    # 2. Function checks
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            
            # Check docstring
            func_doc = ast.get_docstring(node)
            if not func_doc:
                errors.append(f"Function '{func_name}' is missing a docstring.")
            
            # Check function length
            if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
                length = node.end_lineno - node.lineno
                if length > 50:
                    errors.append(f"Function '{func_name}' exceeds 50 lines ({length} lines). Needs refactoring.")

    return errors


# External comment: Audit JS/TS header comment structure
def _audit_js_ts_header(file_path: Path, content: str) -> List[str]:
    """Helper to check block headers on JS/TS files."""
    errors = []
    header_match = re.match(r"^(?:#!.*\n)?\s*/\*\*([\s\S]*?)\*/", content)
    if not header_match:
        errors.append("Missing block comment header (/** ... */) at the top of the file.")
    else:
        header_text = header_match.group(1).lower()
        if "purpose:" not in header_text:
            errors.append("Header is missing 'Purpose:' section.")
        if "key functions:" not in header_text and "props:" not in header_text:
            errors.append("Header is missing 'Key Functions:' or 'Props:' index.")
        
        # Check dependencies only for pages/services/routes/scripts
        needs_deps = any(kw in str(file_path).lower() for kw in ["routes", "services", "scripts", "pages"])
        if needs_deps and "key input dependencies:" not in header_text and "dependencies:" not in header_text:
            errors.append("Header is missing 'Key Input Dependencies:' section (required for routing/data-access files).")
    return errors


# External comment: Audit JS/TS function brace blocks and lengths
def _audit_js_ts_functions(content: str) -> List[str]:
    """Helper to analyze functions and verify length compliance."""
    errors = []
    func_pattern = re.compile(
        r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:\([^)]*\)|[^=]*)\s*=>)", 
        re.MULTILINE
    )
    
    lines = content.splitlines()
    for match in func_pattern.finditer(content):
        func_name = match.group(1) or match.group(2)
        if not func_name or func_name in {"useEffect", "useState", "useMemo", "useCallback"}:
            continue
        
        start_pos = match.start()
        start_line = content[:start_pos].count("\n")
        
        brace_count = 0
        end_line = start_line
        found_braces = False
        
        for l_idx in range(start_line, len(lines)):
            line = lines[l_idx]
            brace_count += line.count("{") - line.count("}")
            if "{" in line:
                found_braces = True
            if found_braces and brace_count <= 0:
                end_line = l_idx
                break
        
        length = end_line - start_line + 1
        if length > 50:
            errors.append(f"Function/Component '{func_name}' exceeds 50 lines ({length} lines). Needs refactoring.")
            
    return errors


# External comment: Audit JS/TS files for block headers and function sizes
def scan_js_ts_file(file_path: Path) -> List[str]:
    """Audits a JavaScript/TypeScript/TSX file using regex checks."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    errors = _audit_js_ts_header(file_path, content)
    errors.extend(_audit_js_ts_functions(content))
    return errors


# External comment: Check if a file is a relative pointer file
def is_pointer_file(path: Path) -> bool:
    """Check if the file is a relative pointer file (single line starting with ../)."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore").strip()
        return "\n" not in content and content.startswith("../")
    except Exception:
        return False


# External comment: Scans files recursively in the workspace directory
def run_audit() -> Dict[str, List[Dict[str, Any]]]:
    """Scans all eligible files in the workspace, ignoring excluded paths."""
    results = {"py": [], "ts": [], "tsx": [], "js": []}
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        
        for file in files:
            file_path = Path(root) / file
            suffix = file_path.suffix.lower()
            
            if suffix in SUPPORTED_EXTENSIONS:
                if is_pointer_file(file_path):
                    continue
                    
                ext_key = suffix[1:]
                
                is_symlink = file_path.is_symlink()
                resolved = file_path.resolve()
                
                if suffix == ".py":
                    errors = scan_python_file(resolved)
                else:
                    errors = scan_js_ts_file(resolved)
                
                if errors:
                    rel_path = file_path.relative_to(WORKSPACE_ROOT)
                    results[ext_key].append({
                        "file": str(rel_path),
                        "is_symlink": is_symlink,
                        "canonical": str(resolved.relative_to(WORKSPACE_ROOT)) if is_symlink else None,
                        "errors": errors
                    })
                    
    return results


# External comment: Persists audit output to temporary markdown report
def write_report(results: Dict[str, List[Dict[str, Any]]]) -> Path:
    """Writes the structured conventions violations report to the temp folder."""
    report_path = WORKSPACE_ROOT / "temp/workspace_conventions_report.md"
    os.makedirs(report_path.parent, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Workspace Coding Conventions Audit Report\n\n")
        f.write("This report lists all source files violating the standards defined in `coding-conventions.md`.\n\n")
        
        total_violations = sum(len(items) for items in results.values())
        f.write(f"### Summary: Found {total_violations} files with compliance violations.\n\n")
        
        for ext, files in results.items():
            if not files:
                continue
            f.write(f"## {ext.upper()} Files ({len(files)} items)\n\n")
            for item in files:
                sym_str = f" *(Symlink -> {repr(item['canonical'])})*" if item['is_symlink'] else ""
                f.write(f"### 📄 {repr(item['file'])}{sym_str}\n")
                for err in item['errors']:
                    f.write(f"- {err}\n")
                f.write("\n")
                
    return report_path


if __name__ == "__main__":
    print("Scanning workspace files...")
    audit_results = run_audit()
    out_file = write_report(audit_results)
    print(f"Audit completed. Report saved to: {out_file}")
