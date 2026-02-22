#!/usr/bin/env python3
"""
Proof Check (CLI)
=====================================

Purpose:
    Scans spec.md, plan.md, and tasks.md for file references and verifies
    each referenced file has been modified compared to origin/main.
    
    This tool prevents "checkbox fraud" where an LLM marks tasks complete
    without actually making changes. It provides deterministic verification
    that work was done.

Usage Examples:
    python plugins/spec-kitty/scripts/proof_check.py --spec-dir specs/0005-human-gate-protocols
    python plugins/spec-kitty/scripts/proof_check.py --spec-dir specs/0005-foo --json

Layer: Orchestrator / Verification

Supported Object Types:
    - Spec artifacts (spec.md, plan.md, tasks.md)
    - Any file reference in backticks (`.md`, `.py`, `.sh`, `.json`, etc.)

CLI Arguments:
    --spec-dir      : Path to spec directory (required)
    --project-root  : Project root directory (default: current)
    --json          : Output in JSON format (optional)

Input Files:
    - specs/[ID]/spec.md
    - specs/[ID]/plan.md
    - specs/[ID]/tasks.md

Output:
    - Summary report of modified/unchanged files
    - Exit code 1 if any referenced files have no changes (fail)
    - Exit code 0 if all referenced files have changes (pass)

Key Functions:
    - extract_file_refs(): Regex extraction of file paths from markdown
    - check_file_modified(): Git diff check against origin/main
    - run_proof_check(): Main orchestration function

Consumed by:
    - tools/cli.py workflow retrospective (via workflow_manager.py)
    - /workflow-retrospective workflow

Script Dependencies:
    - Git (must be in a git repository)
"""
import re
import subprocess
import sys
from pathlib import Path


def extract_file_refs(content: str) -> set:
    """
    Extract file paths from markdown content.
    
    Looks for:
        - Backticked paths: `path/to/file.py`
        - Markdown links: [text](file:///path/to/file)
        - Common patterns: .md, .py, .sh, .json files
    
    Args:
        content: Markdown file content to scan.
    
    Returns:
        Set of file path strings found in the content.
    """
    refs = set()
    
    # Backticked paths (e.g., `tools/cli.py`)
    backtick_pattern = r'`([^`]+\.(md|py|sh|json|js|ts|yaml|yml))`'
    for match in re.findall(backtick_pattern, content):
        refs.add(match[0])
    
    # File links (e.g., [text](file:///path) or [text](../../path))
    link_pattern = r'\[.*?\]\((?:file:///)?([^)]+\.(md|py|sh|json))\)'
    for match in re.findall(link_pattern, content):
        refs.add(match[0])
    
    return refs


def check_file_modified(file_path: str, project_root: Path) -> dict:
    """
    Check if a file has been modified compared to origin/main.
    
    Args:
        file_path: Relative path to the file from project root.
        project_root: Absolute path to the project root.
    
    Returns:
        Dict with status ('modified', 'unchanged', 'new', 'not_found', 'error')
        and details.
    """
    full_path = project_root / file_path
    
    # Check if file exists
    if not full_path.exists():
        return {"status": "not_found", "path": file_path, "details": "File does not exist"}
    
    # Check if file is NEW (not tracked in origin/main)
    try:
        result = subprocess.run(
            ["git", "ls-tree", "origin/main", "--", str(full_path)],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        if not result.stdout.strip():
            # File exists locally but not in origin/main = NEW file
            return {"status": "new", "path": file_path, "details": "New file (not in origin/main)"}
    except Exception:
        pass  # Fall through to diff check
    
    # Check git diff
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "origin/main", "--", str(full_path)],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.stdout.strip():
            return {"status": "modified", "path": file_path, "details": result.stdout.strip()}
        else:
            return {"status": "unchanged", "path": file_path, "details": "No changes detected"}
            
    except Exception as e:
        return {"status": "error", "path": file_path, "details": str(e)}


def run_proof_check(spec_dir: Path, project_root: Path) -> dict:
    """
    Main proof check function.
    
    Scans spec artifacts for file references and verifies each
    has been modified.
    
    Args:
        spec_dir: Path to the spec directory (e.g., specs/0005-foo).
        project_root: Absolute path to the project root.
    
    Returns:
        Dict with lists of 'modified', 'new', 'unchanged', 'not_found', 'errors'.
    """
    results = {
        "modified": [],
        "new": [],
        "unchanged": [],
        "not_found": [],
        "errors": []
    }
    
    all_refs = set()
    
    # Scan spec artifacts
    for artifact in ["spec.md", "plan.md", "tasks.md"]:
        artifact_path = spec_dir / artifact
        if artifact_path.exists():
            content = artifact_path.read_text()
            refs = extract_file_refs(content)
            all_refs.update(refs)
    
    print(f"\n📋 Found {len(all_refs)} file references in spec artifacts")
    print("="*50)
    
    # Check each file
    for ref in sorted(all_refs):
        # Normalize path
        if ref.startswith("/"):
            ref = ref[1:]
        
        result = check_file_modified(ref, project_root)
        
        if result["status"] == "modified":
            print(f"✅ {ref} (modified)")
            results["modified"].append(result)
        elif result["status"] == "new":
            print(f"🆕 {ref} (new file)")
            results["new"].append(result)
        elif result["status"] == "unchanged":
            print(f"⚠️  {ref} - NO CHANGES")
            results["unchanged"].append(result)
        elif result["status"] == "not_found":
            print(f"❓ {ref} - Not found (bad path or bare filename)")
            results["not_found"].append(result)
        else:
            print(f"❌ {ref} - Error: {result['details']}")
            results["errors"].append(result)
    
    print("="*50)
    print(f"\n📊 Summary:")
    print(f"   Modified: {len(results['modified'])}")
    print(f"   New:      {len(results['new'])}")
    print(f"   Unchanged: {len(results['unchanged'])}")
    print(f"   Not Found: {len(results['not_found'])}")
    
    # LLM-friendly error message
    if results["unchanged"]:
        print("\n" + "="*60)
        print("🛑 PROOF CHECK FAILED - VERIFICATION REQUIRED")
        print("="*60)
        print("")
        print("🤖 LLM: STOP AND READ THIS CAREFULLY.")
        print("")
        print("You checked boxes claiming work was done, but these files")
        print("have NO CHANGES compared to origin/main:")
        print("")
        for item in results["unchanged"]:
            print(f"   ❌ {item['path']}")
        print("")
        print("QUESTION: Did you actually do this work, or did you just")
        print("          check the box without making real changes?")
        print("")
        print("REQUIRED ACTIONS:")
        print("   1. Go back and VERIFY each file was actually modified")
        print("   2. If you skipped a step, DO THE WORK NOW")
        print("   3. If the file reference is wrong, FIX the spec/plan/tasks")
        print("   4. Re-run this check until it passes")
        print("")
        print("DO NOT PROCEED until this check passes.")
        print("="*60)
    
    return results


def main():
    """CLI entry point."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="Verify file references in spec artifacts have been modified"
    )
    parser.add_argument("--spec-dir", required=True, help="Path to spec directory")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    spec_dir = Path(args.spec_dir)
    project_root = Path(args.project_root).resolve()
    
    if not spec_dir.exists():
        print(f"❌ Spec directory not found: {spec_dir}")
        sys.exit(1)
    
    results = run_proof_check(spec_dir, project_root)
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit with error if there are unchanged files
    if results["unchanged"]:
        sys.exit(1)
    
    print("\n✅ All referenced files have changes.")


if __name__ == "__main__":
    main()
