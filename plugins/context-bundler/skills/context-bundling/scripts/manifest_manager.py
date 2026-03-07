#!/usr/bin/env python3
"""
manifest_manager.py (CLI)
=====================================

Purpose:
    Handles initialization and modification of the context-manager manifest. Acts as the primary CLI for the Context Bundler.

Layer: Curate / Bundler

Usage Examples:
    # 1. Initialize a custom manifest in a temp folder
    python plugins/context-bundler/scripts/manifest_manager.py --manifest temp/my_manifest.json init --type generic --bundle-title "My Project"

    # 2. Add files to that custom manifest
    python plugins/context-bundler/scripts/manifest_manager.py --manifest temp/my_manifest.json add --path "docs/example.md" --note "Reference doc"

    # 3. Bundle using that custom manifest
    python plugins/context-bundler/scripts/manifest_manager.py --manifest temp/my_manifest.json bundle --output temp/my_bundle.md

    # NOTE: Global flags like --manifest and --base MUST come BEFORE the subcommand (init, add, bundle, etc.)

Supported Object Types:
    - Generic

CLI Arguments:
    Global Flags (Must come BEFORE subcommand):
        --manifest          : Custom path to manifest JSON file (optional)
        --base [type]       : Target a Base Manifest Template (e.g. form, lib)

    Subcommands:
        init                : Bootstrap a new manifest
            --bundle-title  : Human-readable title for the bundle
            --type [type]   : Artifact type template to use
        add                 : Add file to manifest
            --path [path]   : Path to the target file
            --note [text]   : Contextual note about the file
        remove              : Remove file by path
            --path [path]   : Exact path to remove
        update              : Modify an existing entry
            --path [path]   : Target file path
            --note [text]   : New note
            --new-path [p]  : New path for relocation
        search [pattern]    : Find files in the manifest
        list                : Show all files in manifest
        bundle              : Compile manifest into Markdown
            --output [path] : Custom path for the resulting .md file

Input Files:
    - plugins/standalone/context-bundler/base-manifests/*.json (Templates)
    - plugins/standalone/context-bundler/base-manifests-index.json (Template Registry)
    - [Manifest JSON] (Input for bundling/listing)

Output:
    - temp/context-bundles/[title].md (Default Bundle Location)
    - [Custom Manifest JSON] (On init/add/update)

Key Functions:
    - add_file(): Adds a file entry to the manifest if it doesn't already exist.
    - bundle(): Executes the bundling process using the current manifest.
    - get_base_manifest_path(): Resolves base manifest path using index or fallback.
    - init_manifest(): Bootstraps a new manifest file from a base template.
    - list_manifest(): Lists all files currently in the manifest.
    - load_manifest(): Loads the manifest JSON file.
    - remove_file(): Removes a file entry from the manifest.
    - save_manifest(): Saves the manifest dictionary to a JSON file.
    - search_files(): Searches for files in the manifest matching a pattern.
    - update_file(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# =====================================================
# Plugin-aware path resolution
# =====================================================
current_dir = Path(__file__).parent.resolve()
plugin_root = current_dir.parent.resolve()  # plugins/context-bundler/

# Detect project root: walk up from plugin looking for .git or .agent
def _find_project_root() -> str:
    """Find project root by traversing up from plugin location."""
    candidate = plugin_root
    for _ in range(10):  # Max 10 levels up
        if (candidate / ".git").exists() or (candidate / ".agent").exists():
            return str(candidate)
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    return os.getcwd()

project_root = Path(_find_project_root())

# Import strategy: local plugin scripts first, then project-level
sys.path.insert(0, str(current_dir))  # scripts/ dir for sibling imports
try:
    from bundle import bundle_files
    from path_resolver import resolve_root, resolve_path
except ImportError:
    # Fallback to project-level imports
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    try:
        from tools.investigate.utils.path_resolver import resolve_root, resolve_path
        from tools.retrieve.bundler.bundle import bundle_files
    except ImportError:
        from bundle import bundle_files
        resolve_root = lambda: str(project_root)
        resolve_path = lambda p: str(project_root / p)

# =====================================================
# Directory resolution (plugin-aware)
# =====================================================
# Check if resources/ exists in plugin dir (plugin mode)
_plugin_resources = plugin_root / "resources"
if _plugin_resources.exists():
    # Running as a Claude Plugin
    MANIFEST_DIR = plugin_root
    MANIFEST_PATH = plugin_root / "file-manifest.json"
    BASE_MANIFESTS_DIR = _plugin_resources / "base-manifests"
    MANIFEST_INDEX_PATH = _plugin_resources / "base-manifests-index.json"
else:
    # Running from legacy project location
    MANIFEST_DIR = Path(resolve_root()) / "tools" / "standalone" / "context-bundler"
    MANIFEST_PATH = MANIFEST_DIR / "file-manifest.json"
    BASE_MANIFESTS_DIR = MANIFEST_DIR / "base-manifests"
    MANIFEST_INDEX_PATH = MANIFEST_DIR / "base-manifests-index.json"

PROJECT_ROOT = Path(resolve_root()) if callable(resolve_root) else project_root

# =====================================================
# Function definitions
# =====================================================

def add_file(path: str, note: str, manifest_path: Optional[str] = None, base_type: Optional[str] = None) -> None:
    """
    Adds a file entry to the manifest if it doesn't already exist.

    Args:
        path: Relative or absolute path to the file.
        note: Description or note for the file.
        manifest_path: Optional custom path to the manifest.
        base_type: If provided, adds to a base manifest template.
    """
    manifest = load_manifest(manifest_path, base_type)
    if base_type:
        target_path = get_base_manifest_path(base_type)
    else:
        target_path = Path(manifest_path) if manifest_path else MANIFEST_PATH
    manifest_dir = target_path.parent
    
    # Standardize path: relative to manifest_dir and use forward slashes
    if os.path.isabs(path):
        try:
            path = os.path.relpath(path, manifest_dir)
        except ValueError:
            pass
    
    # Replace backslashes with forward slashes for cross-platform consistency in manifest
    path = path.replace('\\', '/')
    while "//" in path:
        path = path.replace("//", "/")

    # Check for duplicate
    for f in manifest["files"]:
        if "path" not in f: continue
        existing = f["path"].replace('\\', '/')
        if existing == path:
            print(f"⚠️  File already in manifest: {path}")
            return

    manifest["files"].append({"path": path, "note": note})
    save_manifest(manifest, manifest_path, base_type)
    print(f"✅ Added to manifest: {path}")

def bundle(output_file: Optional[str] = None, manifest_path: Optional[str] = None) -> None:
    """
    Executes the bundling process using the current manifest.
    
    Args:
        output_file (Optional[str]): Path to save the bundle. Defaults to temp/context-bundles/[title].md
        manifest_path (Optional[str]): Custom manifest path. Defaults to local file-manifest.json.
    """
    target_manifest = manifest_path if manifest_path else str(MANIFEST_PATH)
    
    if not output_file:
        # Load manifest to get title for default output
        # (This implies strictly loading valid JSON at target path)
        try:
             with open(target_manifest, "r") as f:
                data = json.load(f)
                title = data.get("title", "context").lower().replace(" ", "_")
        except Exception:
             title = "bundle"
             
        bundle_out_dir = PROJECT_ROOT / "temp" / "context-bundles"
        bundle_out_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(bundle_out_dir / f"{title}.md")

    print(f"🚀 Running bundle process to {output_file} using {target_manifest}...")
    try:
        # Direct Python Call
        bundle_files(target_manifest, str(output_file)) 
    except Exception as e:
        print(f"❌ Bundling failed: {e}")

def get_base_manifest_path(artifact_type):
    """Resolves base manifest path using index or fallback."""
    if MANIFEST_INDEX_PATH.exists():
        try:
            with open(MANIFEST_INDEX_PATH, "r", encoding="utf-8") as f:
                index = json.load(f)
            filename = index.get(artifact_type)
            if filename:
                return BASE_MANIFESTS_DIR / filename
        except Exception as e:
            print(f"⚠️ Error reading manifest index: {e}")
    
    # Fallback to standard naming convention
    return BASE_MANIFESTS_DIR / f"base-{artifact_type}-file-manifest.json"

def init_manifest(bundle_title: str, artifact_type: str, manifest_path: Optional[str] = None) -> None:
    """
    Bootstraps a new manifest file from a base template.

    Args:
        bundle_title: The title for the bundle (e.g., 'FORM0000').
        artifact_type: The type of artifact (e.g., 'form', 'lib').
        manifest_path: Optional custom path for the new manifest.
    """
    base_file = get_base_manifest_path(artifact_type)
    if not base_file.exists():
        print(f"❌ Error: Base manifest for type '{artifact_type}' not found at {base_file}")
        return

    with open(base_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest["title"] = f"{bundle_title} Context Bundle"
    manifest["description"] = f"Auto-generated context for {bundle_title} (Type: {artifact_type})"
    
    # Substitute [TARGET] placeholder in file paths
    target_lower = bundle_title.lower()
    target_upper = bundle_title.upper()
    if "files" in manifest:
        for file_entry in manifest["files"]:
            if "path" in file_entry:
                # Replace [TARGET] with actual target (case-preserving)
                file_entry["path"] = file_entry["path"].replace("[TARGET]", target_lower)
                file_entry["path"] = file_entry["path"].replace("[target]", target_lower)
            if "note" in file_entry:
                file_entry["note"] = file_entry["note"].replace("[TARGET]", target_upper)
                file_entry["note"] = file_entry["note"].replace("[target]", target_lower)
    
    save_manifest(manifest, manifest_path)
    print(f"✅ Manifest initialized for {bundle_title} ({artifact_type}) at {manifest_path if manifest_path else MANIFEST_PATH}")

def list_manifest(manifest_path: Optional[str] = None, base_type: Optional[str] = None) -> None:
    """
    Lists all files currently in the manifest.

    Args:
        manifest_path: Optional custom path to the manifest.
        base_type: If provided, lists files from a base manifest template.
    """
    manifest = load_manifest(manifest_path, base_type)
    print(f"📋 Current Manifest: {manifest['title']}")
    for i, f in enumerate(manifest["files"], 1):
        if "path" in f:
            print(f"  {i}. {f['path']} - {f.get('note', '')}")
        elif "topic" in f:
            print(f"  {i}. [TOPIC] {f['topic']} - {f.get('note', '')}")
        else:
            print(f"  {i}. [UNKNOWN] {f}")

def load_manifest(manifest_path: Optional[str] = None, base_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads the manifest JSON file.

    Args:
        manifest_path: Optional custom path to the manifest file. 
                       Defaults to plugins/standalone/context-bundler/file-manifest.json.
        base_type: If provided, loads a base manifest template instead of a specific manifest file.

    Returns:
        Dict[str, Any]: The manifest content as a dictionary. 
                        Returns a default empty structure if file not found.
    """
    if base_type:
        target_path = get_base_manifest_path(base_type)
    else:
        target_path = Path(manifest_path) if manifest_path else MANIFEST_PATH
        
    if not target_path.exists():
        return {"title": "Default Bundle", "description": "Auto-generated", "files": []}
    with open(target_path, "r", encoding="utf-8") as f:
        return json.load(f)

def remove_file(path: str, manifest_path: Optional[str] = None, base_type: Optional[str] = None) -> None:
    """
    Removes a file entry from the manifest.

    Args:
        path: The path to the file to remove.
        manifest_path: Optional custom path to the manifest.
        base_type: If provided, removes from a base manifest template.
    """
    manifest = load_manifest(manifest_path, base_type)
    
    # Determine manifest directory for relative path resolution
    if base_type:
        target_path = get_base_manifest_path(base_type)
    else:
        target_path = Path(manifest_path) if manifest_path else MANIFEST_PATH
    manifest_dir = target_path.parent

    # Standardize path: relative to manifest_dir and use forward slashes
    if os.path.isabs(path):
        try:
            path = os.path.relpath(path, manifest_dir)
        except ValueError:
            pass
    
    # Replace backslashes with forward slashes for cross-platform consistency
    path = path.replace('\\', '/')
    while "//" in path:
        path = path.replace("//", "/")

    # Filter out the file
    initial_count = len(manifest["files"])
    manifest["files"] = [f for f in manifest["files"] if f.get("path") != path]
    
    if len(manifest["files"]) < initial_count:
        save_manifest(manifest, manifest_path, base_type)
        print(f"✅ Removed from manifest: {path}")
    else:
        print(f"⚠️  File not found in manifest: {path}")

def save_manifest(manifest: Dict[str, Any], manifest_path: Optional[str] = None, base_type: Optional[str] = None) -> None:
    """
    Saves the manifest dictionary to a JSON file.

    Args:
        manifest: The dictionary content to save.
        manifest_path: Optional custom destination path. 
                       Defaults to plugins/standalone/context-bundler/file-manifest.json.
        base_type: If provided, saves to a base manifest template path.
    """
    if base_type:
        target_path = get_base_manifest_path(base_type)
    else:
        target_path = Path(manifest_path) if manifest_path else MANIFEST_PATH
        
    manifest_dir = target_path.parent
    if not manifest_dir.exists():
        os.makedirs(manifest_dir, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def search_files(pattern: str, manifest_path: Optional[str] = None, base_type: Optional[str] = None) -> None:
    """
    Searches for files in the manifest matching a pattern.

    Args:
        pattern: The search string (case-insensitive substring match).
        manifest_path: Optional custom path to the manifest.
        base_type: If provided, searches within a base manifest template.
    """
    manifest = load_manifest(manifest_path, base_type)
    matches = [f for f in manifest["files"] if f.get("path") and (pattern.lower() in f["path"].lower() or pattern.lower() in f.get("note", "").lower())]
    
    if matches:
        print(f"🔍 Found {len(matches)} matches in manifest:")
        for m in matches:
            print(f"  - {m['path']} ({m.get('note', '')})")
    else:
        print(f"❓ No matches for '{pattern}' in manifest.")

def update_file(path, note=None, new_path=None, manifest_path=None, base_type=None):
    manifest = load_manifest(manifest_path, base_type)
    if base_type:
        target_path = get_base_manifest_path(base_type)
    else:
        target_path = Path(manifest_path) if manifest_path else MANIFEST_PATH
    manifest_dir = target_path.parent

    # Standardize lookup path
    if os.path.isabs(path):
        try:
             path = os.path.relpath(path, manifest_dir)
        except ValueError:
             pass
    path = path.replace('\\', '/')
    while "//" in path:
        path = path.replace("//", "/")

    found = False
    for f in manifest["files"]:
        if f.get("path") == path:
            found = True
            if note is not None:
                 f["note"] = note
            if new_path:
                 # Standardize new path
                 np = new_path
                 if os.path.isabs(np):
                     try:
                         np = os.path.relpath(np, manifest_dir)
                     except ValueError:
                         pass
                 np = np.replace('\\', '/')
                 while "//" in np:
                     np = np.replace("//", "/")
                 f["path"] = np
            break
    
    if found:
        save_manifest(manifest, manifest_path, base_type)
        print(f"✅ Updated in manifest: {path}")
    else:
        print(f"⚠️  File not found in manifest: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manifest Manager CLI")
    parser.add_argument("--manifest", help="Custom path to manifest file (optional)")
    parser.add_argument("--base", help="Target a Base Manifest Type (e.g. form, lib)")
    
    subparsers = parser.add_subparsers(dest="action")

    # init
    init_parser = subparsers.add_parser("init", help="Initialize manifest from base")
    init_parser.add_argument("--bundle-title", required=True, help="Title for the bundle (e.g., 'FORM0000')")
    init_parser.add_argument('--type', 
        choices=['constraint', 'context-bundler', 'form', 'function', 'generic', 'index', 'lib', 'menu', 'olb', 'package', 'procedure', 'report', 'sequence', 'table', 'trigger', 'type', 'view', 'br'], 
        help='Artifact Type (e.g. form, lib)'
    )
    # init uses --manifest but not --base for the *target* (source is arg type)

    # add
    add_parser = subparsers.add_parser("add", help="Add file to manifest")
    add_parser.add_argument("--path", required=True, help="Relative or absolute path")
    add_parser.add_argument("--note", default="", help="Note for the file")

    # remove
    remove_parser = subparsers.add_parser("remove", help="Remove file from manifest")
    remove_parser.add_argument("--path", required=True, help="Path to remove")

    # update
    update_parser = subparsers.add_parser("update", help="Update file in manifest")
    update_parser.add_argument("--path", required=True, help="Path to update")
    update_parser.add_argument("--note", help="New note")
    update_parser.add_argument("--new-path", help="New path")

    # search
    search_parser = subparsers.add_parser("search", help="Search files in manifest")
    search_parser.add_argument("pattern", help="Search pattern")

    # list
    list_parser = subparsers.add_parser("list", help="List files in manifest")

    # bundle
    bundle_parser = subparsers.add_parser("bundle", help="Execute bundle.py")
    bundle_parser.add_argument("--output", help="Output file path (optional)")

    args = parser.parse_args()

    if args.action == "init":
        init_manifest(args.bundle_title, args.type, args.manifest)
    elif args.action == "add":
        add_file(args.path, args.note, args.manifest, args.base)
    elif args.action == "remove":
        remove_file(args.path, args.manifest, args.base)
    elif args.action == "update":
        update_file(args.path, args.note, args.new_path, args.manifest, args.base)
    elif args.action == "search":
        search_files(args.pattern, args.manifest, args.base)
    elif args.action == "list":
        list_manifest(args.manifest, args.base)
    elif args.action == "bundle":
        # Bundle logic primarily processes instantiated manifests, not templates, 
        # but could technically bundle a base template.
        # bundle() signature doesn't take base_type yet, let's keep it simple for now or resolve path before calling it.
        target_manifest = args.manifest
        if args.base:
            target_manifest = str(get_base_manifest_path(args.base))
        bundle(args.output, target_manifest)
    else:
        parser.print_help()