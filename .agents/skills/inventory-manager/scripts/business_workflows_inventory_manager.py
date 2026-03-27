#!/usr/bin/env python3
"""
business_workflows_inventory_manager.py (CLI)
=====================================

Purpose:
    Manages the Business Workflows Inventory (Scan, Search, Register, Update).
    
    Acts as the central registry for Business Workflows (BW), enforcing duplicate checks via
    multi-source search (Inventory, RLM Cache, Vector DB) before registration.

Layer: Curate / Inventories

Usage Examples:
    # 1. Scan and Rebuild Inventory
    python plugins/inventory-manager/scripts/business_workflows_inventory_manager.py --scan

    # 2. Search for existing workflows (Multi-source: Inventory, RLM, Vector)
    python plugins/inventory-manager/scripts/business_workflows_inventory_manager.py --search "intake process"

    # 3. Register a new Business Workflow (Interactive or CLI)
    python plugins/inventory-manager/scripts/business_workflows_inventory_manager.py --register --title "Case Intake" --source "FORM0000" --priority "P2"

    # 4. Update a Business Workflow Summary
    python plugins/inventory-manager/scripts/business_workflows_inventory_manager.py --update-summary "BW-0001" --new-summary "Revised summary text..."

Supported Object Types:
    - Business Workflows (BW-NNNN)

CLI Arguments:
    --scan          : Rebuild business_workflows_inventory.json
    --search [TERM] : Search across Inventory, RLM, and Vector DB
    --register      : Register a new Business Workflow
    --update-summary: Update the summary of an existing workflow
    --title         : Title for registration
    --source        : Source object for registration
    --priority      : Priority (P1/P2/P3)
    --new-summary   : Content for update-summary

Script Dependencies:
    - tools.retrieve.rlm.query_cache
    - tools.retrieve.vector.query
    - tools.investigate.utils.next_number

"""
import os
import json
import re
import argparse
import sys
from pathlib import Path

# Add project root to path to allow imports
current_dir = Path(__file__).resolve().parent

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in current_dir.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

project_root = _find_project_root()
sys.path.append(str(project_root))

try:
    from tools.retrieve.rlm import query_cache
except ImportError:
    query_cache = None

try:
    from tools.retrieve.vector.query import VectorDBQuery
except ImportError:
    VectorDBQuery = None

try:
    from tools.investigate.utils import next_number
except ImportError:
    next_number = None


# Paths
WORKFLOWS_DIR = project_root / 'legacy-system' / 'business-workflows'
OUTPUT_PATH = project_root / 'legacy-system' / 'reference-data' / 'inventories' / 'business_workflows_inventory.json'
TEMPLATE_PATH = project_root / 'docs' / 'templates' / 'BUSINESS_workflow-definition-template.md'

# --- Helper Functions ---

def load_inventory():
    if not OUTPUT_PATH.exists():
        return {}
    try:
        with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def extract_metadata_from_file(filepath):
    """Extract metadata from the markdown file content."""
    metadata = {
        'title': None,
        'status': None,
        'actors': None,
        'applications': None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract title from H1
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
            
        # Extract Status
        status_match = re.search(r'\*\*Status\*\*[:\s]+(.+?)(?:\n|\*\*)', content)
        if status_match:
            metadata['status'] = status_match.group(1).strip()
            
        # Extract Actors
        actors_match = re.search(r'\*\*Actors\*\*[:\s]+(.+?)(?:\n|\*\*)', content)
        if actors_match:
            metadata['actors'] = actors_match.group(1).strip()
            
        # Extract Applications
        apps_match = re.search(r'\*\*Applications\*\*[:\s]+(.+?)(?:\n|\*\*)', content)
        if apps_match:
            metadata['applications'] = apps_match.group(1).strip()
            
        # Extract Description (First paragraph under ## Description or ## Overview)
        desc_match = re.search(r'## (?:Description|Overview)\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if desc_match:
            raw_desc = desc_match.group(1).strip()
            metadata['description'] = raw_desc[:500].replace('\n', ' ')
            
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}")
        
    return metadata

def scan_workflows():
    """Scan business-workflows directory and build inventory."""
    inventory = {}
    
    if not WORKFLOWS_DIR.exists():
        print(f"Warning: Workflows directory not found: {WORKFLOWS_DIR}")
        return inventory
        
    for filename in os.listdir(WORKFLOWS_DIR):
        if filename.endswith('.md') and filename.startswith('BW-'):
            # Extract BW ID (e.g., BW-0001 from BW-0001-report-request-workflow.md)
            bw_match = re.match(r'^(BW-\d{4})', filename)
            if bw_match:
                bw_id = bw_match.group(1)
            else:
                bw_id = os.path.splitext(filename)[0].upper()
                
            filepath = WORKFLOWS_DIR / filename
            metadata = extract_metadata_from_file(filepath)
            
            inventory[bw_id] = {
                'type': 'WORKFLOW',
                'file': filename,
                'title': metadata.get('title') or bw_id,
                'status': metadata.get('status') or 'Active',
                'actors': metadata.get('actors'),
                'applications': metadata.get('applications'),
                'description': metadata.get('description', ''),
                'overviewPath': f"legacy-system/business-workflows/{filename}"
            }
            
    return inventory

# --- Search Functions ---

def search_inventory_by_id(bw_id):
    """Exact ID lookup in local inventory."""
    inventory = load_inventory()
    if bw_id.upper() in inventory:
        return inventory[bw_id.upper()]
    return None

def search_rlm_cache(query_text):
    """Search RLM Cache via query_cache util."""
    if not query_cache:
        print("⚠️ RLM Query module not available.")
        return []
    results = query_cache.search_cache(query_text, show_summary=False, return_data=True)
    return results

def search_vector_db(query_text):
    """Semantic search via VectorDB."""
    if not VectorDBQuery:
        print("⚠️ VectorDB module not available.")
        return []
    
    try:
        db = VectorDBQuery()
        results = db.query(query_text, n_results=3, silent=True)
        filtered = []
        if isinstance(results, list):
            for res in results:
                filtered.append(res)
        return filtered
    except Exception as e:
        print(f"⚠️ Vector Search failed: {e}")
        return []

def search_multi_source(query_text):
    """Orchestrate all searches."""
    # Policy Check: Enforce minimum 2 words
    if len(query_text.strip().split()) < 2:
        print("❌ Search Error: Query must contain at least 2 words.")
        return

    print(f"\n🔍 Multi-Source Search for: '{query_text}'")
    
    # 1. Inventory Check
    print("\n--- 1. Inventory Check ---")
    inv_results = []
    inventory = load_inventory()
    for uid, data in inventory.items():
        searchable_text = f"{uid} {data.get('title','')} {data.get('actors','')} {data.get('description','')}".lower()
        if query_text.lower() in searchable_text:
            inv_results.append(data)
    
    if inv_results:
        for res in inv_results:
            print(f"✅ Found in Inventory: {res.get('file', 'Unknown')}")
    else:
        print("No direct inventory matches.")

    # 2. RLM Check
    print("\n--- 2. RLM Intelligence Check ---")
    rlm_results = search_rlm_cache(query_text)
    if rlm_results:
        print(f"✅ Found {len(rlm_results)} RLM Context matches.")
        
        bw_found = False
        for r in rlm_results: 
            path = r.get('path', '')
            if 'business-workflows/BW-' in path:
                bw_found = True
                print(f"   ⚠️  MATCHING BW: {path}")
            else:
                print(f"   - {path}")
                
        if not bw_found:
            print("\n   ℹ️  Context found, but NO codified 'BW-*' file detected in RLM.")
            
    else:
        print("No RLM matches.")

    # 3. Vector Check
    print("\n--- 3. Semantic Vector Check ---")
    vector_results = search_vector_db(query_text)
    if vector_results:
        print(f"✅ Found {len(vector_results)} Semantic matches.")
        
        bw_found = False
        for res in vector_results:
            source = ""
            if isinstance(res, dict):
                source = res.get('source', '')
            elif hasattr(res, 'metadata'):
                source = res.metadata.get('source', '')

            if 'business-workflows/BW-' in source:
                bw_found = True
                print(f"   ⚠️  MATCHING BW: {source}")
            else:
                 print(f"   - {source}")

        if not bw_found:
             print("\n   ℹ️  Context found, but NO codified 'BW-*' file detected in Vector DB.")
    else:
        print("No Vector matches.")


# --- Registration & Update ---

def register_business_workflow(title, source, priority):
    """Register a new Business Workflow."""
    print(f"\n📝 Registering New Business Workflow: '{title}'")
    
    # 1. Mandatory Duplicate Check
    search_multi_source(title)
    
    confirm = input("\nDoes this workflow already exist based on the above? (y/N): ")
    if confirm.lower() == 'y':
        print("❌ Registration aborted.")
        return

    # 2. Generate ID
    if not next_number:
        print("❌ Error: `next_number` utility missing.")
        return

    try:
        new_id = next_number.get_next_number("bw", project_root)
    except Exception as e:
        print(f"❌ Error generating ID: {e}")
        return
    
    print(f"✨ Assigned ID: {new_id}")
    
    # 3. Create File
    slug = title.lower().replace(" ", "-").replace("/", "-")
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    filename = f"{new_id}-{slug}.md"
    filepath = WORKFLOWS_DIR / filename
    
    # Template Loading & Rendering
    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        template_content = template_content.replace("BW-NNNN", new_id)
        template_content = template_content.replace("[Workflow Title]", title)
        template_content = template_content.replace("[Active | Draft | Deprecated]", "Active")
    else:
        # Fallback if template missing
        template_content = f"# {new_id}: {title}\n\n**Status**: Active\n**Priority**: {priority}\n**Source**: {source}\n\n## Overview\nWorkflow derived from {source}.\n\n## Steps\n1. [Step 1]\n2. [Step 2]\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template_content)
        
    print(f"✅ Created file: {filepath}")
    
    # 4. Re-scan to update inventory
    scan_and_save()

def update_summary(bw_id, new_summary):
    """Update workflow summary."""
    inventory = load_inventory()
    if bw_id not in inventory:
        print(f"❌ ID {bw_id} not found.")
        return
        
    entry = inventory[bw_id]
    filename = entry['file']
    filepath = WORKFLOWS_DIR / filename
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = r'(## (?:Description|Overview)\s*)(.*?)(\n##|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        new_content = content[:match.start(2)] + new_summary.strip() + "\n\n" + content[match.end(2):]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated summary in {filename}")
        
        scan_and_save()
        
    else:
        print(f"❌ Could not find '## Description' or '## Overview' section in {filename}")

# --- Investigation Logic (Recursive Topic Discovery) ---

def investigate_topic(topic):
    """
    Orchestrate Recursive Topic Discovery (Context Spiral).
    1. Initialize Topic Manifest (from Base)
    2. Search Multi-Source (Inventory, RLM, Vector) for candidates
    3. Auto-Add candidates to manifest (including consumer expansion)
    4. Trigger Bundle generation
    """
    import subprocess
    
    print(f"\n🕵️‍♂️ Starting Recursive Topic Investigation for: '{topic}'")
    slug = re.sub(r'[^a-z0-9\-]', '', topic.lower().replace(" ", "-"))
    target_id = f"topic_{slug}"
    
    # Define explicit paths
    temp_dir = project_root / "temp"
    manifest_dir = temp_dir / "manifests"
    bundle_dir = temp_dir / "context-bundles"
    
    # Ensure dirs exist
    manifest_dir.mkdir(parents=True, exist_ok=True)
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    manifest_path = manifest_dir / f"{target_id}_manifest.json"
    bundle_path = bundle_dir / f"{target_id}_context.md"
    
    # Step 1: Initialize Context (Base Manifest - using BW type)
    print(f"\n--- Step 1: Initialize Context ({target_id}) ---")
    cmd_init = [
        sys.executable, str(project_root / \"plugins\" / \"context-bundler\" / \"skills\" / \"context-bundler\" / \"scripts\" / \"manifest_manager.py\"), 
        "manifest", "init",
        "--bundle-title", target_id,
        "--type", "generic",  # BW uses generic base (no specific base manifest)
        "--manifest", str(manifest_path)
    ]
    
    try:
        subprocess.run(cmd_init, check=True)
    except subprocess.CalledProcessError as e:
        print(f"X Failed to initialize context: {e}")
        return

    # Step 2: Search Candidates
    print(f"\n--- Step 2: Identifying Candidate Artifacts ---")
    candidates = []
    
    # 2a. RLM Search
    rlm_results = search_rlm_cache(topic)
    for res in rlm_results:
        path = res.get('path', '')
        if path and path not in candidates:
            candidates.append(path)
            
    # 2b. Vector Search
    vector_results = search_vector_db(topic)
    for res in vector_results:
        source = ""
        if isinstance(res, dict):
            source = res.get('source', '')
        elif hasattr(res, 'metadata'):
            source = res.metadata.get('source', '')
            
        if source and source not in candidates:
             candidates.append(source)
    
    # 2c. Extract Consumers from existing BW files (Auto-Impact Expansion)
    bw_files_found = [c for c in candidates if 'business-workflows/BW-' in c]
    for bw_path in bw_files_found:
        try:
            full_bw_path = project_root / bw_path if not Path(bw_path).is_absolute() else Path(bw_path)
            if full_bw_path.exists():
                content = full_bw_path.read_text(encoding='utf-8')
                # Look for form/package references in tables (e.g. | **FORM0000** | or | **PROJECT_QUERY** |)
                consumer_pattern = re.findall(r'\|\s*\*\*\[?([A-Z]{3,4}[SE]?\d{4}|PROJECT_[A-Z_]+)\]?', content)
                for consumer_id in consumer_pattern:
                    # Map consumer IDs to likely file paths
                    if consumer_id.startswith('APP') or consumer_id.startswith('FORM'):
                        form_path = f"legacy-system/oracle-forms-markdown/XML/{consumer_id.lower()}-FormModule.md"
                        if form_path not in candidates:
                            candidates.append(form_path)
                            print(f"   [+] Auto-added consumer form: {consumer_id}")
                    elif consumer_id.startswith('PROJECT_'):
                        pkg_path = f"legacy-system/oracle-database/source/Packages/{consumer_id}.sql"
                        if pkg_path not in candidates:
                            candidates.append(pkg_path)
                            print(f"   [+] Auto-added consumer package: {consumer_id}")
        except Exception as e:
            print(f"   [!] Could not parse BW file for consumers: {e}")
    
    print(f"Found {len(candidates)} unique candidate artifacts.")
    
    # Step 3: Add Candidates to Manifest
    if candidates:
        print(f"\n--- Step 3: Adding Candidates to Manifest ---")
        for cand in candidates:
            # Filter: Only add relevant code artifacts
            if "legacy-system" in cand or "tools/" in cand:
                print(f"   + Adding: {cand}")
                cmd_add = [
                    sys.executable, str(project_root / \"plugins\" / \"context-bundler\" / \"skills\" / \"context-bundler\" / \"scripts\" / \"manifest_manager.py\"),
                    "manifest", "add",
                    "--manifest", str(manifest_path),
                    "--path", cand,
                    "--note", f"Detected via search: {topic}"
                ]
                subprocess.run(cmd_add)
    
    # Step 4: Bundle
    print(f"\n--- Step 4: Generating Topic Bundle ---")
    cmd_bundle = [
        sys.executable, str(project_root / \"plugins\" / \"context-bundler\" / \"skills\" / \"context-bundler\" / \"scripts\" / \"manifest_manager.py\"),
        "manifest", "bundle",
        "--manifest", str(manifest_path),
        "--output", str(bundle_path)
    ]
    subprocess.run(cmd_bundle)
    
    print(f"\n[OK] Investigation Complete.")
    print(f"   Bundle: temp/context-bundles/{target_id}_context.md")
    print(f"   Manifest: temp/manifests/{target_id}_manifest.json")
    
    # Machine-readable output for scripting/agent capture
    print(f"\n--- CAPTURE THESE PATHS ---")
    print(f"MANIFEST_PATH={manifest_path}")
    print(f"BUNDLE_PATH={bundle_path}")
    print(f"--- END CAPTURE ---")
    
    print("\nNext: Review the bundle and run Phase 2 (Validation/Registration) if logic is confirmed.")
    print(f"      Use: --manifest {manifest_path} for subsequent manifest commands.")


# --- Main ---

def scan_and_save():
    print("Generating Business Workflows Inventory...")
    inventory = scan_workflows()
    print(f"Found {len(inventory)} business workflows.")
    sorted_inventory = dict(sorted(inventory.items()))
    
    output_dir = os.path.dirname(OUTPUT_PATH)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_inventory, f, indent=2)
    print(f"Business Workflows Inventory generated at {OUTPUT_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Business Workflows Inventory Manager")
    parser.add_argument("--scan", action="store_true", help="Rebuild inventory")
    parser.add_argument("--search", help="Search term")
    parser.add_argument("--register", action="store_true", help="Register new workflow")
    parser.add_argument("--update-summary", help="ID of workflow to update")
    parser.add_argument("--investigate", help="Recursive topic investigation (Context Spiral)")
    
    # Register args
    parser.add_argument("--title", help="Title for new workflow")
    parser.add_argument("--source", help="Source ID")
    parser.add_argument("--priority", default="P2", help="Priority")
    
    # Update args
    parser.add_argument("--new-summary", help="New summary text")

    args = parser.parse_args()

    if args.scan:
        scan_and_save()
    elif args.search:
        search_multi_source(args.search)
    elif args.investigate:
        investigate_topic(args.investigate)
    elif args.register:
        if not args.title or not args.source:
            print("X --title and --source required for registration.")
            sys.exit(1)
        register_business_workflow(args.title, args.source, args.priority)
    elif args.update_summary:
        if not args.new_summary:
            print("X --new-summary required.")
            sys.exit(1)
        update_summary(args.update_summary, args.new_summary)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
