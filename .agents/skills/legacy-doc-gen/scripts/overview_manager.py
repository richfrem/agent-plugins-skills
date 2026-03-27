#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/overview_manager.py (CLI)
=====================================

Purpose:
    Lifecycle manager for Overview documentation. Detects missing docs, generates files from templates (Forms, Reports, Libs), runs batch audits, and triggers RLM/Vector post-processing.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/overview_manager.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --source        : Path to source artifact (relative to project root)
    --id            : Artifact ID/Name (e.g., FORM0000)
    --type          : Artifact type (form, report, library, menu, db_procedure, db_table, db_view)
    --check-all     : Check all artifacts of --type for missing docs
    --create        : Create doc if missing (default: check only)
    --sync          : Run post-processing (RLM + Vector DB) after create/update
    --json          : Output as JSON

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_config(): Load the discovery output map configuration.
    - detect_type_from_source(): Detect artifact type from source path using config patterns.
    - get_mapping_by_type(): Get mapping configuration by artifact type.
    - extract_name_from_source(): Extract the artifact name from source path based on type conventions.
    - build_doc_path(): Build the expected documentation path for an artifact.
    - check_doc_exists(): Check if documentation exists for an artifact.
    - create_doc_from_template(): Create a new documentation file from template.
    - run_post_processing(): Run post-processing hooks (RLM cache update, Vector DB ingest).
    - find_sources_by_type(): Find all source files matching a given type's pattern.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import argparse
import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
CONFIG_PATH = SCRIPT_DIR / "discovery_output_map.json"


def load_config():
    """Load the discovery output map configuration."""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def detect_type_from_source(source_path: str, config: dict) -> dict | None:
    """Detect artifact type from source path using config patterns."""
    from fnmatch import fnmatch
    
    for mapping in config.get("mappings", []):
        pattern = mapping.get("source_pattern", "")
        if pattern == "NA":
            continue
        # Convert glob pattern to something we can match
        # Simple check: does the source path match the pattern's directory structure?
        if fnmatch(source_path, pattern):
            return mapping
    return None


def get_mapping_by_type(artifact_type: str, config: dict) -> dict | None:
    """Get mapping configuration by artifact type."""
    for mapping in config.get("mappings", []):
        if mapping.get("type") == artifact_type:
            return mapping
    return None


def extract_name_from_source(source_path: str, mapping: dict) -> str:
    """Extract the artifact name from source path based on type conventions."""
    filename = Path(source_path).stem  # Remove extension
    
    # Remove common suffixes based on type
    suffix_map = {
        "form": "_fmb",
        "menu": "_mmb",
        "report": "",  # Reports don't have consistent suffix
        "library": "",
        "db_procedure": "",
        "db_function": "",
        "db_table": "",
        "db_view": "",
    }
    
    artifact_type = mapping.get("type", "")
    suffix = suffix_map.get(artifact_type, "")
    
    if suffix and filename.endswith(suffix):
        name = filename[:-len(suffix)]
    else:
        name = filename
    
    return name.upper()


def build_doc_path(name: str, mapping: dict) -> Path:
    """Build the expected documentation path for an artifact."""
    target_dir = mapping.get("doc_target_dir", "")
    naming_convention = mapping.get("doc_naming_convention", "{name}-Overview.md")
    
    doc_name = naming_convention.replace("{name}", name)
    return PROJECT_ROOT / target_dir / doc_name


def check_doc_exists(name: str, mapping: dict) -> tuple[bool, Path]:
    """Check if documentation exists for an artifact."""
    doc_path = build_doc_path(name, mapping)
    return doc_path.exists(), doc_path


def create_doc_from_template(name: str, mapping: dict, source_path: str = None) -> Path:
    """Create a new documentation file from template."""
    template_path = PROJECT_ROOT / mapping.get("template_path", "")
    doc_path = build_doc_path(name, mapping)
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    # Ensure target directory exists
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read template and substitute placeholders
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Common substitutions
    replacements = {
        "{name}": name,
        "{NAME}": name,
        "{FORM_NAME}": name,
        "{REPORT_NAME}": name,
        "{LIBRARY_NAME}": name,
        "{MENU_NAME}": name,
        "{PROCEDURE_NAME}": name,
        "{TABLE_NAME}": name,
        "{OBJECT_NAME}": name,
        "{DATE}": datetime.now().strftime("%Y-%m-%d"),
        "{filename}": Path(source_path).stem if source_path else name.lower(),
    }
    
    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)
    
    # Write new doc
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return doc_path


def run_post_processing(doc_path: Path, config: dict, verbose: bool = True):
    """Run post-processing hooks (RLM cache update, Vector DB ingest)."""
    import subprocess
    
    post_processing = config.get("post_processing", {})
    rel_path = doc_path.relative_to(PROJECT_ROOT)
    
    results = {}
    
    # RLM Cache Update
    if "update_rlm_cache" in post_processing:
        cmd_template = post_processing["update_rlm_cache"].get("command", "")
        cmd = cmd_template.replace("{doc_path}", str(rel_path))
        if verbose:
            print(f"  [RLM] Running: {cmd}")
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=60
            )
            results["rlm"] = {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            results["rlm"] = {"success": False, "error": str(e)}
    
    # Vector DB Ingest
    if "update_vector_db" in post_processing:
        cmd_template = post_processing["update_vector_db"].get("command", "")
        cmd = cmd_template.replace("{doc_path}", str(rel_path))
        if verbose:
            print(f"  [Vector] Running: {cmd}")
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=120
            )
            results["vector"] = {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            results["vector"] = {"success": False, "error": str(e)}
    
    return results


def find_sources_by_type(artifact_type: str, config: dict) -> list[Path]:
    """Find all source files matching a given type's pattern."""
    from glob import glob
    
    mapping = get_mapping_by_type(artifact_type, config)
    if not mapping:
        return []
    
    pattern = mapping.get("source_pattern", "")
    if pattern == "NA":
        return []
    
    full_pattern = str(PROJECT_ROOT / pattern)
    return [Path(p) for p in glob(full_pattern, recursive=True)]


def main():
    parser = argparse.ArgumentParser(description="Manage overview documents for legacy artifacts")
    parser.add_argument("--source", help="Path to source artifact (relative to project root)")
    parser.add_argument("--id", help="Artifact ID/Name (e.g., FORM0000)")
    parser.add_argument("--type", help="Artifact type (form, report, library, menu, db_procedure, db_table, db_view)")
    parser.add_argument("--check-all", action="store_true", help="Check all artifacts of --type for missing docs")
    parser.add_argument("--create", action="store_true", help="Create doc if missing (default: check only)")
    parser.add_argument("--sync", action="store_true", help="Run post-processing (RLM + Vector DB) after create/update")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    config = load_config()
    results = []
    
    if args.check_all and args.type:
        # Batch mode: check all artifacts of a type
        sources = find_sources_by_type(args.type, config)
        mapping = get_mapping_by_type(args.type, config)
        
        if not mapping:
            print(f"Unknown type: {args.type}")
            return
        
        for source in sources:
            rel_path = source.relative_to(PROJECT_ROOT)
            name = extract_name_from_source(str(rel_path), mapping)
            exists, doc_path = check_doc_exists(name, mapping)
            
            result = {
                "name": name,
                "source": str(rel_path),
                "doc_path": str(doc_path.relative_to(PROJECT_ROOT)),
                "exists": exists
            }
            
            if not exists and args.create:
                created_path = create_doc_from_template(name, mapping, str(rel_path))
                result["created"] = True
                result["doc_path"] = str(created_path.relative_to(PROJECT_ROOT))
                if args.sync:
                    run_post_processing(created_path, config, verbose=not args.json)
            
            results.append(result)
        
        # Summary
        missing = [r for r in results if not r["exists"]]
        created = [r for r in results if r.get("created")]
        
        if args.json:
            print(json.dumps({"results": results, "total": len(results), "missing": len(missing), "created": len(created)}, indent=2))
        else:
            print(f"Total: {len(results)} | Missing: {len(missing)} | Created: {len(created)}")
            for r in missing:
                status = "CREATED" if r.get("created") else "MISSING"
                print(f"  [{status}] {r['name']} -> {r['doc_path']}")
    
    elif args.source:
        # Single source mode
        mapping = detect_type_from_source(args.source, config)
        if not mapping:
            print(f"Could not detect type for: {args.source}")
            return
        
        name = extract_name_from_source(args.source, mapping)
        exists, doc_path = check_doc_exists(name, mapping)
        
        if args.json:
            print(json.dumps({"name": name, "type": mapping["type"], "exists": exists, "doc_path": str(doc_path)}))
        else:
            status = "EXISTS" if exists else "MISSING"
            print(f"[{status}] {name} ({mapping['type']}) -> {doc_path}")
        
        if not exists and args.create:
            created_path = create_doc_from_template(name, mapping, args.source)
            print(f"Created: {created_path}")
            if args.sync:
                run_post_processing(created_path, config)
    
    elif args.id and args.type:
        # Direct ID mode
        mapping = get_mapping_by_type(args.type, config)
        if not mapping:
            print(f"Unknown type: {args.type}")
            return
        
        exists, doc_path = check_doc_exists(args.id.upper(), mapping)
        
        if args.json:
            print(json.dumps({"name": args.id.upper(), "type": args.type, "exists": exists, "doc_path": str(doc_path)}))
        else:
            status = "EXISTS" if exists else "MISSING"
            print(f"[{status}] {args.id.upper()} ({args.type}) -> {doc_path}")
        
        if not exists and args.create:
            created_path = create_doc_from_template(args.id.upper(), mapping)
            print(f"Created: {created_path}")
            if args.sync:
                run_post_processing(created_path, config)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
