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

# File-level exclusions: known-intentional test fixtures that must stay
# out of conventions compliance to serve their own regression tests.
EXCLUDE_FILES = {
    # Deliberately broken security-scanner fixture — see
    # plugins/agent-scaffolders/tests/flawed-plugin/README.md. Must keep
    # its violations (missing docstrings, hardcoded creds, network calls)
    # so inventory_plugin.py's scanner can be verified to detect them.
    "plugins/agent-scaffolders/tests/flawed-plugin/scripts/bad_script.py",
}

# File extensions to scan
SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js"}


# Extract the 'Key Functions:' block from a module docstring, if present
def _extract_key_functions_section(docstring: str) -> str:
    """Return the text of the docstring block whose first line mentions 'Key Functions'."""
    blocks = re.split(r"\n\s*\n", docstring)
    for block in blocks:
        stripped = block.strip()
        if stripped and "key functions" in stripped.splitlines()[0].lower():
            return block
    return ""


# Collect every function/method name and class name actually defined in the parsed file
def _collect_defined_names(tree: ast.AST) -> tuple:
    """Return (defined_names, defined_classes).

    defined_names includes plain function names and 'ClassName.method_name' pairs.
    defined_classes is the set of locally-defined class names, used to distinguish
    genuine local method references from external module calls (e.g. os.walk()).
    """
    defined = set()
    classes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.add(node.name)
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defined.add(f"{node.name}.{item.name}")
    return defined, classes


# Flag 'Key Functions' entries that reference a function no longer in the file
def _check_key_functions_freshness(docstring: str, tree: ast.AST) -> List[str]:
    """Detect stale 'Key Functions' references (renamed/removed functions).

    Dotted references (e.g. 'os.walk()') are only checked when the prefix is a
    locally-defined class — otherwise they're treated as external module calls
    mentioned in prose, not a promise about this file's own function set.
    """
    section = _extract_key_functions_section(docstring)
    if not section:
        return []
    defined_names, defined_classes = _collect_defined_names(tree)
    errors = []
    for name in re.findall(r"([A-Za-z_][A-Za-z0-9_.]*)\(\)", section):
        if "." in name:
            prefix = name.rpartition(".")[0]
            if prefix not in defined_classes:
                continue
        if name not in defined_names:
            errors.append(f"Header 'Key Functions' references '{name}()', which no longer exists in this file.")
    return errors


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
        errors.extend(_check_key_functions_freshness(docstring, tree))

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


def _audit_file(
    file_path: Path,
    results: Dict[str, List[Dict[str, Any]]],
    scanned_plugins: set[str],
    failed_plugins: set[str],
    unique_scanned_files: set[str],
    unique_failed_files: set[str]
) -> tuple[int, int]:
    """Audit a single file for compliance conventions, updating statistics collections."""
    if is_pointer_file(file_path):
        return 0, 0

    suffix = file_path.suffix.lower()
    ext_key = suffix[1:]
    is_symlink = file_path.is_symlink()
    resolved = file_path.resolve()
    unique_scanned_files.add(str(resolved))

    # Check if it belongs to a plugin
    rel_path = file_path.relative_to(WORKSPACE_ROOT)
    if len(rel_path.parts) > 1 and rel_path.parts[0] == "plugins":
        plugin_name = rel_path.parts[1]
        scanned_plugins.add(plugin_name)
    else:
        plugin_name = None

    if suffix == ".py":
        errors = scan_python_file(resolved)
    else:
        errors = scan_js_ts_file(resolved)

    if errors:
        unique_failed_files.add(str(resolved))
        if plugin_name:
            failed_plugins.add(plugin_name)
        results[ext_key].append({
            "file": str(rel_path),
            "is_symlink": is_symlink,
            "canonical": str(resolved.relative_to(WORKSPACE_ROOT)) if is_symlink else None,
            "errors": errors
        })
        return 1, 1
    return 1, 0


# External comment: Scans files recursively in the workspace directory
def run_audit() -> tuple[Dict[str, List[Dict[str, Any]]], set[str], set[str], int, int, set[str], set[str]]:
    """Scans all eligible files in the workspace, ignoring excluded paths."""
    results = {"py": [], "ts": [], "tsx": [], "js": []}
    scanned_plugins = set()
    failed_plugins = set()
    total_files_checked = 0
    total_files_failed = 0
    unique_scanned_files = set()
    unique_failed_files = set()
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        
        for file in files:
            file_path = Path(root) / file
            suffix = file_path.suffix.lower()

            if suffix in SUPPORTED_EXTENSIONS:
                if file_path.relative_to(WORKSPACE_ROOT).as_posix() in EXCLUDE_FILES:
                    continue
                checked, failed = _audit_file(
                    file_path, results, scanned_plugins, failed_plugins,
                    unique_scanned_files, unique_failed_files
                )
                total_files_checked += checked
                total_files_failed += failed
                    
    return results, scanned_plugins, failed_plugins, total_files_checked, total_files_failed, unique_scanned_files, unique_failed_files


# External comment: Persists audit output to temporary markdown report
def write_report(results: Dict[str, List[Dict[str, Any]]], scanned_plugins: set[str], failed_plugins: set[str]) -> Path:
    """Writes the structured conventions violations report to the temp folder."""
    report_path = WORKSPACE_ROOT / "temp/workspace_conventions_report.md"
    os.makedirs(report_path.parent, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Workspace Coding Conventions Audit Report\n\n")
        f.write("This report lists all source files violating the standards defined in `coding-conventions.md`.\n\n")
        
        total_violations = sum(len(items) for items in results.values())
        passed_count = len(scanned_plugins) - len(failed_plugins)
        f.write(f"### Summary: Found {total_violations} files with compliance violations across {len(scanned_plugins)} checked plugins ({passed_count} passed, {len(failed_plugins)} failed).\n\n")
        
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
    audit_results, scanned_p, failed_p, files_chk, files_fail, unique_chk, unique_fail = run_audit()
    out_file = write_report(audit_results, scanned_p, failed_p)
    passed_p_count = len(scanned_p) - len(failed_p)
    print(f"Plugins checked: {len(scanned_p)}")
    print(f"Plugins passed:  {passed_p_count}")
    print(f"Plugins failed:  {len(failed_p)}")
    if failed_p:
        print(f"Failing plugins: {', '.join(sorted(failed_p))}")
    print(f"Unique canonical files checked: {len(unique_chk)}")
    print(f"Unique canonical files passed:  {len(unique_chk) - len(unique_fail)}")
    print(f"Unique canonical files failed:  {len(unique_fail)}")
    print(f"Total script references checked: {files_chk}")
    print(f"Total script references passed:  {files_chk - files_fail}")
    print(f"Total script references failed:  {files_fail}")
    print(f"Audit completed. Report saved to: {out_file}")
