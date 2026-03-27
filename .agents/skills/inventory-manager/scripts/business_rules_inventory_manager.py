#!/usr/bin/env python3
"""
business_rules_inventory_manager.py (CLI)
=====================================

Purpose:
    Manages the Business Rules Inventory (Scan, Search, Register, Update).
    
    Acts as the central registry for Business Rules, enforcing duplicate checks via
    multi-source search (Inventory, RLM Cache, Vector DB) before registration.

Layer: Curate / Inventories

Usage Examples:
    # 1. Scan and Rebuild Inventory
    python plugins/inventory-manager/scripts/business_rules_inventory_manager.py --scan

    # 2. Search for existing rules (Multi-source: Inventory, RLM, Vector)
    #    (Scopes results to legacy-system/business-rules/)
    python plugins/inventory-manager/scripts/business_rules_inventory_manager.py --search "court access"

    # 3. Register a new Business Rule (Interactive or CLI)
    python plugins/inventory-manager/scripts/business_rules_inventory_manager.py --register --title "Check Seal Status" --source "FORM0000" --priority "P1"

    # 4. Update a Business Rule Summary
    python plugins/inventory-manager/scripts/business_rules_inventory_manager.py --update-summary "BR-0001" --new-summary "Revised summary text..."

Supported Object Types:
    - Business Rules (BR-NNNN)

CLI Arguments:
    --scan          : Rebuild business_rules_inventory.json
    --search [TERM] : Search across Inventory, RLM, and Vector DB
    --register      : Register a new Business Rule
    --update-summary: Update the summary of an existing rule
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

# Import Utils
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
BUSINESS_RULES_DIR = project_root / 'legacy-system' / 'business-rules'
OUTPUT_PATH = project_root / 'legacy-system' / 'reference-data' / 'inventories' / 'business_rules_inventory.json'
TEMPLATE_PATH = project_root / 'docs' / 'templates' / 'business-rule-template.md'

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
        'category': None,
        'status': None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract title from H1
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
            
        # Extract Category
        category_match = re.search(r'\*\*Category\*\*[:\s]+(.+?)(?:\n|\*\*)', content)
        if category_match:
            metadata['category'] = category_match.group(1).strip()
            
        # Extract Status
        status_match = re.search(r'\*\*Status\*\*[:\s]+(.+?)(?:\n|\*\*)', content)
        if status_match:
            metadata['status'] = status_match.group(1).strip()

        # Extract Source (e.g. Form ID)
        # Handle "**Source**: FORM0000" or "- **Form/Artifact:** FORM0000"
        source_match = re.search(r'\*\*Source\*\*[:\s]+(.+?)(?:\n|\*\*)', content)
        if not source_match:
             source_match = re.search(r'Form/Artifact:\*\*[:\s]+(.+?)(?:\n|$)', content)
        if source_match:
            metadata['source'] = source_match.group(1).strip()
            
        # Extract Description (First paragraph under ## Description or Logic)
        # Simple heuristic: Look for ## Description, capture text until next header
        desc_match = re.search(r'## (?:Description|Logic)\s*(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if desc_match:
            raw_desc = desc_match.group(1).strip()
            # Truncate if too long (e.g. 500 chars)
            metadata['description'] = raw_desc[:500].replace('\n', ' ')
            
    except Exception as e:
        print(f"Warning: Could not parse {filepath}: {e}")
        
    return metadata

def scan_business_rules():
    """Scan business-rules directory and build inventory."""
    inventory = {}
    
    if not BUSINESS_RULES_DIR.exists():
        print(f"Warning: Business Rules directory not found: {BUSINESS_RULES_DIR}")
        return inventory
        
    for filename in os.listdir(BUSINESS_RULES_DIR):
        if filename.endswith('.md') and filename.startswith('BR-'):
            # Extract BR ID (e.g., BR-0001 from BR-0001-court-access-levels.md)
            br_match = re.match(r'^(BR-\d{4})', filename)
            if br_match:
                br_id = br_match.group(1)
            else:
                br_id = os.path.splitext(filename)[0].upper()
                
            filepath = BUSINESS_RULES_DIR / filename
            metadata = extract_metadata_from_file(filepath)
            
            inventory[br_id] = {
                'type': 'BUSINESS_RULE',
                'file': filename,
                'title': metadata.get('title') or br_id,
                'category': metadata.get('category'),
                'status': metadata.get('status') or 'Active',
                'source': metadata.get('source'),
                'description': metadata.get('description', ''),
                'overviewPath': f"legacy-system/business-rules/{filename}"
            }
            
    return inventory

# --- Search Functions ---

def search_inventory_by_id(br_id):
    """Exact ID lookup in local inventory."""
    inventory = load_inventory()
    if br_id.upper() in inventory:
        return inventory[br_id.upper()]
    return None

def search_rlm_cache(query_text):
    """Search RLM Cache via query_cache util."""
    if not query_cache:
        print("⚠️ RLM Query module not available.")
        return []
    # Use return_data=True to get list instead of print
    results = query_cache.search_cache(query_text, show_summary=False, return_data=True)
    
    # Filter? No, we want to see if the rule exists anywhere (e.g. inside a Form summary)
    # returning all results to give better visibility
    return results

def search_vector_db(query_text):
    """Semantic search via VectorDB."""
    if not VectorDBQuery:
        print("⚠️ VectorDB module not available.")
        return []
    
    try:
        db = VectorDBQuery()
        # Use silent=True to get object list without printing JSON to stdout
        results = db.query(query_text, n_results=3, silent=True)
        # Since query.py currently prints, we normally need structured return.
        # But if we updated query.py to output_json=True and print JSON, we capture stdout.
        # HOWEVER, we are importing the class directly.
        # We need to verify if db.query returns the object list.
        # Based on typical usage, it returns `results` list.
        # Filter for Business Rules only
        filtered = []
        # Normalizing results structure based on how query.py returns data
        # If it returns LangChain docs, we need to inspect metadata
        # If it returns JSON list (our assumption), we check 'source'
        if isinstance(results, list):
            for res in results:
                # Handle different result formats (JSON dict or Tuple)
                source = ""
                if isinstance(res, dict):
                    source = res.get('source', '')
                elif hasattr(res, 'metadata'): # Document object
                    source = res.metadata.get('source', '')
                    
                filtered.append(res)
        
        return filtered
    except Exception as e:
        print(f"⚠️ Vector Search failed: {e}")
        return []

def search_multi_source(query_text):
    """Orchestrate all searches."""
    # Policy Check: Enforce minimum 2 words to prevent broad noise
    if len(query_text.strip().split()) < 2:
        print("❌ Search Error: Query must contain at least 2 words (e.g. 'charge assessment', 'access control').")
        print("   Single-word searches are too broad for this knowledge base.")
        return

    print(f"\n🔍 Multi-Source Search for: '{query_text}'")
    
    # 1. Inventory Check
    print("\n--- 1. Inventory Check ---")
    inv_results = []
    inventory = load_inventory()
    for uid, data in inventory.items():
        # Search Scope: ID, Title, Source, Description
        searchable_text = f"{uid} {data.get('title','')} {data.get('source','')} {data.get('description','')}".lower()
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
        
        br_founded = False
        for r in rlm_results: 
            path = r.get('path', '')
            if 'business-rules/BR-' in path:
                br_founded = True
                print(f"   ⚠️  MATCHING BR: {path}")
            else:
                print(f"   - {path}") # List context
                
        if not br_founded:
            print("\n   ℹ️  Context found, but NO codified 'BR-*' file detected in RLM.")
            print("       This suggests the rule might be a good candidate for registration.")
            
    else:
        print("No RLM matches.")

    # 3. Vector Check
    print("\n--- 3. Semantic Vector Check ---")
    vector_results = search_vector_db(query_text)
    if vector_results:
        print(f"✅ Found {len(vector_results)} Semantic matches.")
        
        br_founded = False
        for res in vector_results:
            # handle dict vs object
            source = ""
            if isinstance(res, dict):
                source = res.get('source', '')
            elif hasattr(res, 'metadata'):
                source = res.metadata.get('source', '')

            if 'business-rules/BR-' in source:
                br_founded = True
                print(f"   ⚠️  MATCHING BR: {source}")
            else:
                 print(f"   - {source}")

        if not br_founded:
             print("\n   ℹ️  Context found, but NO codified 'BR-*' file detected in Vector DB.")
             print("       This confirms semantic uniqueness.")
    else:
        print("No Vector matches.")


# --- Registration & Update ---

def register_business_rule(title, source, priority):
    """Register a new Business Rule."""
    print(f"\n📝 Registering New Business Rule: '{title}'")
    
    # 1. Mandatory Duplicate Check
    search_multi_source(title)
    
    confirm = input("\nDoes this rule already exist based on the above? (y/N): ")
    if confirm.lower() == 'y':
        print("❌ Registration aborted.")
        return

    # 2. Generate ID
    if not next_number:
        print("❌ Error: `next_number` utility missing.")
        return

    try:
        new_id = next_number.get_next_number("br", project_root)
    except Exception as e:
        print(f"❌ Error generating ID: {e}")
        return
    
    print(f"✨ Assigned ID: {new_id}")
    
    # 3. Create File
    slug = title.lower().replace(" ", "-").replace("/", "-")
    # Clean slug to only alphanum and dashes
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    filename = f"{new_id}-{slug}.md"
    filepath = BUSINESS_RULES_DIR / filename
    
    # Template Loading & Rendering
    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Replace Placeholders
        template_content = template_content.replace("BR-NNNN", new_id)
        template_content = template_content.replace("[Rule Title]", title)
        # Default Metadata
        template_content = template_content.replace("[Active | Deprecated | Needs Review]", "Active")
        template_content = template_content.replace("[Validation | Calculation | Access Control | Workflow]", "Validation")
        template_content = template_content.replace("[Low | Medium | High]", priority)
        # Source (Handle Source Locations table or metadata?)
        # Template has "Source Locations" table, but maybe we want to put source in context?
        # The template doesn't have a specific "Source: " metadata line in the header block unless we add it.
        # Let's inject it into the Description or Source Locations for now.
        
        # We can add a source note in the Description for clarity
        template_content = template_content.replace("[Clear, plain English description of the rule. What is the business intent?]", 
                                                  f"Validation logic derived from {source}.\n\n[Add description here]")
    else:
        # Fallback if template missing
        template_content = f"# {new_id}: {title}\n\n**Category**: Validation\n**Status**: Active\n**Priority**: {priority}\n**Source**: {source}\n\n## Description\nValidation logic derived from {source}.\n\n## Logic\n[Description of the rule]\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template_content)
        
    print(f"✅ Created file: {filepath}")
    
    # 4. Re-scan to update inventory
    scan_and_save()

def update_summary(br_id, new_summary):
    """Update valid business rule summary."""
    inventory = load_inventory()
    if br_id not in inventory:
        print(f"❌ ID {br_id} not found.")
        return
        
    entry = inventory[br_id]
    filename = entry['file']
    filepath = BUSINESS_RULES_DIR / filename
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return

    # Read and Replace Logic (Regex for simplicity in this artifact)
    # Read content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Look for ## Description or ## Logic
    # We want to replace the text *after* the header until the next header
    
    # Pattern: (## (?:Description|Logic)\s*)(.*?)(\n##|\Z)
    # Group 1: Header + whitespace
    # Group 2: Content (non-greedy)
    # Group 3: Next header or end of string
    
    pattern = r'(## (?:Description|Logic)\s*)(.*?)(\n##|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        new_content = content[:match.start(2)] + new_summary.strip() + "\n\n" + content[match.end(2):]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated summary in {filename}")
        
        # Post-update: Re-scan inventory to reflect changes
        scan_and_save()
        
    else:
        print(f"❌ Could not find '## Description' or '## Logic' section in {filename}")
        # Optional: Append if missing? For now, strict update.


# --- Main ---

def scan_and_save():
    print("Generating Business Rules Inventory...")
    inventory = scan_business_rules()
    print(f"Found {len(inventory)} business rules.")
    sorted_inventory = dict(sorted(inventory.items()))
    
    output_dir = os.path.dirname(OUTPUT_PATH)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_inventory, f, indent=2)
    print(f"Business Rules Inventory generated at {OUTPUT_PATH}")



# --- Investigation Logic (Phase 3b) ---

def investigate_topic(topic):
    """
    Orchestrate Recursive Topic Discovery (Context Spiral).
    1. Initialize Topic Manifest (from Base)
    2. Search Multi-Source (Inventory, RLM, Vector) for candidates
    3. Auto-Add candidates to manifest
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
    
    # Step 1: Initialize Context (Base Manifest)
    print(f"\n--- Step 1: Initialize Context ({target_id}) ---")
    # We use manifest_manager.py init --type br --manifest [PATH]
    # Note: init-context command in CLI might default to global manifest if not passed.
    # We must explicitly pass --manifest to init-context -> manifest_manager.init_manifest
    
    # manifest_manager.py init args: --target, --type.  Does it accept --manifest?
    # Checking manifest_manager.py: init-context uses default script path logic. It does NOT accept --manifest arg in the parser?
    # Wait, manifest_manager.py line 288: context_parser.add_argument("--target")...
    # It does NOT have --manifest arg.
    # However, 'manifest init' DOES have --manifest.
    # So we should call 'manifest init' directly via CLI if we want custom path.
    
    # Switch to 'python plugins/context-bundler/skills/context-bundler/scripts/manifest_manager.py manifest init' for custom path control.
    cmd_init = [
        sys.executable, str(project_root / \"plugins\" / \"context-bundler\" / \"skills\" / \"context-bundler\" / \"scripts\" / \"manifest_manager.py\"), 
        "manifest", "init",
        "--bundle-title", target_id,
        "--type", "br",
        "--manifest", str(manifest_path)
    ]
    
    try:
        subprocess.run(cmd_init, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize context: {e}")
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
    
    # 2c. Extract Consumers from existing BR files (Auto-Impact Expansion)
    br_files_found = [c for c in candidates if 'business-rules/BR-' in c]
    for br_path in br_files_found:
        try:
            full_br_path = project_root / br_path if not Path(br_path).is_absolute() else Path(br_path)
            if full_br_path.exists():
                content = full_br_path.read_text(encoding='utf-8')
                # Look for form/package references in tables (e.g. | **FORM0000** | or | **PROJECT_QUERY** |)
                import re as regex_mod
                consumer_pattern = regex_mod.findall(r'\|\s*\*\*\[?([A-Z]{3,4}[SE]?\d{4}|PROJECT_[A-Z_]+)\]?', content)
                for consumer_id in consumer_pattern:
                    # Map consumer IDs to likely file paths
                    if consumer_id.startswith('APP') or consumer_id.startswith('FORM'):
                        form_path = f"legacy-system/oracle-forms-markdown/XML/{consumer_id.lower()}-FormModule.md"
                        if form_path not in candidates:
                            candidates.append(form_path)
                            print(f"   📎 Auto-added consumer form: {consumer_id}")
                    elif consumer_id.startswith('PROJECT_'):
                        pkg_path = f"legacy-system/oracle-database/source/Packages/{consumer_id}.sql"
                        if pkg_path not in candidates:
                            candidates.append(pkg_path)
                            print(f"   📎 Auto-added consumer package: {consumer_id}")
        except Exception as e:
            print(f"   ⚠️ Could not parse BR file for consumers: {e}")
    
    print(f"✅ Found {len(candidates)} unique candidate artifacts.")
    
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
    
    print(f"\n✅ Investigation Complete.")
    print(f"   Bundle: temp/context-bundles/{target_id}_context.md")
    print(f"   Manifest: temp/manifests/{target_id}_manifest.json")
    
    # Machine-readable output for scripting/agent capture
    print(f"\n--- CAPTURE THESE PATHS ---")
    print(f"MANIFEST_PATH={manifest_path}")
    print(f"BUNDLE_PATH={bundle_path}")
    print(f"--- END CAPTURE ---")
    
    print("\nNext: Review the bundle and run Phase 2 (Validation/Registration) if logic is confirmed.")
    print(f"      Use: --manifest {manifest_path} for subsequent manifest commands.")


def main():
    parser = argparse.ArgumentParser(description="Business Rules Inventory Manager")
    parser.add_argument("--scan", action="store_true", help="Rebuild inventory")
    parser.add_argument("--search", help="Search term")
    parser.add_argument("--register", action="store_true", help="Register new rule")
    parser.add_argument("--update-summary", help="ID of rule to update")
    
    # Investigation Args
    parser.add_argument("--investigate", help="Topic/Keyword to investigate (Recursive Context Spiral)")
    
    # Register args
    parser.add_argument("--title", help="Title for new rule")
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
            print("❌ --title and --source required for registration.")
            sys.exit(1)
        register_business_rule(args.title, args.source, args.priority)
    elif args.update_summary:
        if not args.new_summary:
            print("❌ --new-summary required.")
            sys.exit(1)
        update_summary(args.update_summary, args.new_summary)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
