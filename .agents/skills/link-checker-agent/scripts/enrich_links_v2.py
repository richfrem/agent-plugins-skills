#!/usr/bin/env python3
"""
enrich_links_v2.py (CLI)
=====================================

Purpose:
    Enriches markdown links using master object collection.

Layer: Curate / Utilities

Usage Examples:
    python plugins/link-checker/scripts/enrich_links_v2.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --file          : Specific file to enrich
    --all           : Process all documentation directories

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_master_collection(): Load and index the master object collection.
    - get_relative_path(): Calculate relative path from source file to target path.
    - create_link(): Create a markdown link for an object ID.
    - is_valid_role(): Check if a potential role name is valid (not a trigger/event).
    - enrich_content(): Enrich all links in content string.
    - enrich_file(): Enrich links in a single markdown file.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import re
import json
import argparse
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================
# REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CWD = REPO_ROOT # For backwards compatibility with rest of script using CWD variable
MASTER_COLLECTION_PATH = REPO_ROOT / 'legacy-system' / 'reference-data' / 'master_object_collection.json'
ORPHANED_ROLES_PATH = REPO_ROOT / 'legacy-system' / 'reference-data' / 'orphaned_roles.json'

# Object type to artifact priority mapping
# For each type, which artifact should be the primary link target?
ARTIFACT_PRIORITY = {
    'FORM': ['overview', 'xml-md', 'xml'],
    'REPORT': ['overview', 'xml-md', 'xml'],
    'PLL': ['overview', 'source'],
    'MENU': ['overview', 'xml-md', 'xml'],
    'OBJ_LIB': ['overview', 'source'],
    'DB_PACKAGE': ['overview', 'sql'],
    'DB_PROCEDURE': ['overview', 'sql'],
    'DB_FUNCTION': ['overview', 'sql'],
    'TABLE': ['overview', 'sql'],
    'VIEW': ['overview', 'sql'],
    'DB_TYPE': ['sql'],
    'CONSTRAINT': ['sql'],
    'INDEX': ['sql'],
    'SEQUENCE': ['sql'],
    'ROLE': ['definition'],
    'APPLICATION': ['overview'],
    'WORKFLOW': ['overview'],
    'BUSINESS_RULE': ['overview'],
}

# Valid role prefixes (to filter false positives)
VALID_ROLE_PREFIXES = ('APP5_', 'APP2_', 'APP3_', 'APP1_', 'OCJ_', 'POS_', 'APP4_', 'JUS_')

# Trigger/Event prefixes to EXCLUDE (false positives)
EXCLUDE_PREFIXES = ('WHEN_', 'ON_', 'PRE_', 'POST_', 'KEY_', 'BLOCK_', 'ITEM_', 'FORM_')

# =============================================================================
# LOAD MASTER COLLECTION
# =============================================================================
def load_master_collection():
    """Load and index the master object collection."""
    if not MASTER_COLLECTION_PATH.exists():
        print(f"ERROR: Master Collection not found at {MASTER_COLLECTION_PATH}")
        print("Run: python scripts/inventory/build_master_collection.py --full")
        return {}, {}
    
    with open(MASTER_COLLECTION_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    objects = data.get('objects', {})
    
    # Build a case-insensitive lookup (all keys uppercase)
    lookup = {k.upper(): v for k, v in objects.items()}
    
    return lookup, data.get('objectTypes', {})

OBJECTS, OBJECT_TYPES = load_master_collection()

# Track orphaned roles found during enrichment
ORPHANED_ROLES = {}

# =============================================================================
# LINK GENERATION
# =============================================================================
def get_relative_path(from_file: Path, to_path: str) -> str | None:
    """Calculate relative path from source file to target path."""
    abs_target = CWD / to_path
    if abs_target.exists():
        return os.path.relpath(abs_target, from_file.parent).replace('\\', '/')
    return None


def create_link(obj_id: str, from_file: Path, include_source_links: bool = False) -> str | None:
    """
    Create a markdown link for an object ID.
    
    Args:
        obj_id: The object identifier (e.g., 'FORM0000', 'APP1_CORR_ADMIN')
        from_file: Path to the file being enriched (for relative path calculation)
        include_source_links: If True, append [[xml-md]][[xml]] links for forms/reports
    
    Returns:
        Markdown link string or None if object not found
    """
    obj = OBJECTS.get(obj_id.upper())
    if not obj:
        return None
    
    obj_type = obj.get('type', '')
    artifacts = obj.get('artifacts', {})
    
    # Determine primary artifact based on type
    priority_list = ARTIFACT_PRIORITY.get(obj_type, ['overview', 'sql', 'source'])
    
    primary_path = None
    for artifact_key in priority_list:
        if artifact_key in artifacts:
            primary_path = artifacts[artifact_key]
            break
    
    if not primary_path:
        return None
    
    rel_path = get_relative_path(from_file, primary_path)
    if not rel_path:
        return None
    
    # Build the link
    link = f"[{obj_id.upper()}]({rel_path})"
    
    # Optionally append source links for Forms/Reports
    if include_source_links and obj_type in ('FORM', 'REPORT'):
        source_links = []
        if 'xml-md' in artifacts:
            xml_md_path = get_relative_path(from_file, artifacts['xml-md'])
            if xml_md_path:
                source_links.append(f"[[xml-md]]({xml_md_path})")
        if 'xml' in artifacts:
            xml_path = get_relative_path(from_file, artifacts['xml'])
            if xml_path:
                source_links.append(f"[[xml]]({xml_path})")
        if source_links:
            link += ' ' + ' '.join(source_links)
    
    return link


def is_valid_role(name: str) -> bool:
    """Check if a potential role name is valid (not a trigger/event)."""
    name_upper = name.upper()
    if any(name_upper.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
        return False
    if not any(name_upper.startswith(prefix) for prefix in VALID_ROLE_PREFIXES):
        return False
    return True

# =============================================================================
# ENRICHMENT LOGIC
# =============================================================================
def enrich_content(content: str, from_file: Path) -> str:
    """
    Enrich all links in content string.
    
    Strategy:
    1. Remove (Reference Missing: ...) placeholders
    2. Normalize [ID.ext] to [ID]
    3. Find [ID] not already linked -> link them
    4. Handle [[xml]] [[xml-md]] tags
    5. Find bare IDs matching known objects -> link them
    """
    
    # -------------------------------------------------------------------------
    # PHASE 1: Cleanup
    # -------------------------------------------------------------------------
    
    # Remove (Reference Missing: ...) tags
    content = re.sub(r'\s*\(Reference Missing:[^)]+\)', '', content)
    
    # Normalize file extensions in brackets: [FORM0000.fmb] -> [FORM0000]
    def strip_extension(m):
        name = m.group(1)
        ext = m.group(2)
        if ext.lower() in ('.fmb', '.rdf', '.pll', '.sql', '.md'):
            return f"[{name}]"
        return m.group(0)
    
    content = re.sub(r'\[([A-Z0-9_]+)(\.[a-z]{2,4})\]', strip_extension, content, flags=re.IGNORECASE)
    
    # -------------------------------------------------------------------------
    # PHASE 2: Link bracketed IDs [ID] that are not already linked
    # -------------------------------------------------------------------------
    
    def link_bracketed_id(m):
        """Replace [ID] with [ID](path) if ID is known."""
        full_match = m.group(0)
        obj_id = m.group(1)
        
        # Skip if already a link [ID](...)
        # The regex uses negative lookahead so this shouldn't happen, but be safe
        
        # Check if this is a known object
        link = create_link(obj_id, from_file)
        if link:
            return link
        
        # Check if it looks like a Form/Report ID pattern
        # Pattern: 3-4 letters + E/R/M/L + 4 digits + optional suffix
        if re.match(r'^[A-Z]{3,4}[ERML]\d{4}[A-Z]?$', obj_id.upper()):
            # Try stripping suffix (A, B, C, D, etc.) and link to base form
            base_id_match = re.match(r'^([A-Z]{3,4}[ERML]\d{4})[A-Z]$', obj_id.upper())
            if base_id_match:
                base_id = base_id_match.group(1)
                base_link = create_link(base_id, from_file)
                if base_link:
                    # Link to base, note the variant
                    return f"[{obj_id.upper()}]({base_link.split('](')[1].rstrip(')')}) *(variant)*"
            
            return f"{full_match} *(No Overview)*"
        
        # Check if it's a role (might be orphaned)
        if is_valid_role(obj_id):
            if obj_id.upper() not in ORPHANED_ROLES:
                ORPHANED_ROLES[obj_id.upper()] = {'files': [str(from_file.name)]}
        
        return full_match  # Keep original if not found
    
    # Match [ID] NOT followed by ( - i.e., not already a link
    # Allow uppercase, numbers, underscores, dots (for nested types)
    # Match [ID] NOT followed by ( - i.e., not already a link
    # Allow uppercase, numbers, underscores, dots, AND DASHES (for BW-xxxx, BR-xxxx)
    content = re.sub(r'\[([A-Z][A-Z0-9_\.\-]+)\](?!\()', link_bracketed_id, content)
    
    # -------------------------------------------------------------------------
    # PHASE 3: Handle [[xml]] and [[xml-md]] artifact tags
    # -------------------------------------------------------------------------
    
    def link_artifact_tag(m):
        """
        Find [ID](path) [[tag]] OR [[tag]] (using file ID) and replace.
        """
        preceding = m.group(1) if m.group(1) else ""
        tag = m.group(2)        # xml or xml-md
        
        obj_id = None
        
        # Try to extract ID from preceding link
        if preceding:
            id_match = re.search(r'\[([A-Z0-9_]+)\]', preceding)
            if id_match:
                obj_id = id_match.group(1).upper()
        
        # Fallback: Try to use ID from filename (e.g. FORM0016-Overview.md -> FORM0016)
        if not obj_id:
            file_match = re.search(r'^([A-Z]{3,4}[EMS]\d{4}\w?)', from_file.name, re.IGNORECASE)
            if file_match:
                obj_id = file_match.group(1).upper()
        
        if not obj_id:
            return preceding  # Remove orphan tag if valid ID not found
        
        obj = OBJECTS.get(obj_id)
        if not obj:
            return preceding
        
        artifacts = obj.get('artifacts', {})
        if tag not in artifacts:
            return preceding
            
        target_path = get_relative_path(from_file, artifacts[tag])
        if not target_path:
            return preceding
            
        return f"{preceding} [[{tag}]]({target_path})" if preceding else f"[[{tag}]]({target_path})"
    
    # Match: Optional preceding link, then [[xml]] or [[xml-md]]
    # We combine the "attached" and "standalone" logic here
    content = re.sub(
        r'(?:(\[[A-Z0-9_]+\]\([^)]+\))\s*)?\[\[(xml-md|xml)\]\](?!\()',
        link_artifact_tag,
        content
    )
    
    # Also clean up standalone [[xml]] or [[xml-md]] tags not preceded by a link
    # These are orphans that couldn't be resolved
    content = re.sub(r'\s*\[\[(xml-md|xml)\]\](?!\()', '', content)
    
    # -------------------------------------------------------------------------
    # PHASE 4: Link bare IDs (Specific Patterns)
    # -------------------------------------------------------------------------
    
    # Build patterns for different object types
    
    # Forms/Reports: XXXX0000 pattern (e.g., FORM0000, FORM0000)
    def link_form_report(m):
        obj_id = m.group(1).upper()
        if obj_id.upper() in OBJECTS:
            link = create_link(obj_id, from_file)
            if link:
                return link
        return m.group(0)
    
    # Guard pattern to avoid matching inside existing links
    # Negative lookbehind: not preceded by [ or ( or / or -
    # Negative lookahead: not followed by ] or [ or ( or .
    # Guard pattern: allow '(' before, but not '](', '[' or '/'.
    # e.g. Allow (FORM0016) but not [Link](FORM0016) or [FORM0016]
    form_pattern = r'(?<!\[)(?<!/)(?<!-)(?<!\]\()\b([A-Z]{3,4}[EMS]\d{4}[a-z]?)\b(?![\]\[(.\-])'
    content = re.sub(form_pattern, link_form_report, content)
    
    # Business Rules: BR-0001
    def link_br(m):
        obj_id = m.group(1).upper()
        link = create_link(obj_id, from_file)
        return link if link else m.group(0)
    
    content = re.sub(r'(?<!\[)(?<!/)(?<!-)(?<!\]\()\b(BR-\d{4})\b(?![\]\[(.\-])', link_br, content)

    # Workflows: BW-0001
    def link_bw(m):
        obj_id = m.group(1).upper()
        link = create_link(obj_id, from_file)
        return link if link else m.group(0)
    
    content = re.sub(r'(?<!\[)(?<!/)(?<!-)(?<!\]\()\b(BW-\d{4})\b(?![\]\[(.\-])', link_bw, content)
    
    # Roles: XXX_ROLE_NAME (only if in collection)
    def link_role(m):
        role_name = m.group(1).upper()
        if not is_valid_role(role_name):
            return m.group(0)
        link = create_link(role_name, from_file)
        if link:
            return link
        # Track orphaned
        if role_name not in ORPHANED_ROLES:
            ORPHANED_ROLES[role_name] = {'files': [str(from_file.name)]}
        return m.group(0)
    
    role_pattern = r'(?<![(\[/\-])\b([A-Z]{3,}_[A-Z0-9_]+)\b(?![\]\[(.\-])'
    content = re.sub(role_pattern, link_role, content)

    # -------------------------------------------------------------------------
    # PHASE 4.5: Catch-All Global Object Search
    # -------------------------------------------------------------------------
    # This phase scans for any remaining uppercase words that match known object IDs.
    # This catches items like EXAMPLE_LIB, WEBUTIL, etc. that don't match specific patterns.
    
    def link_generic_object(m):
        word = m.group(1).upper()
        # Skip if it looks like a file extension or hex
        if len(word) < 3: return m.group(0)
        
        if word in OBJECTS:
            # We found a known object! Link it.
            link = create_link(word, from_file)
            return link if link else m.group(0)
        return m.group(0)

    # Regex: Look for uppercase words of 3+ chars, allow numbers/underscores/dashes
    # Must NOT be inside a link.
    # Uses negative lookbehind to ensure we aren't in `](...` or `[...`
    # Strict bounds \b
    
    generic_pattern = r'(?<!\[)(?<!/)(?<!-)(?<!\]\()\b([A-Z][A-Z0-9_\-]{2,})\b(?![\]\[(.\-])'
    content = re.sub(generic_pattern, link_generic_object, content)

    # -------------------------------------------------------------------------
    # PHASE 5: Post-cleanup
    # -------------------------------------------------------------------------
    
    # Fix nested links: [[text](url)](url) -> [text](url)
    for _ in range(3):
        old = content
        content = re.sub(r'\[\[([^\]]+)\]\(([^)]+)\)\]\([^)]+\)', r'[\1](\2)', content)
        if content == old:
            break
    
    # Remove backticks around links: `[text](url)` -> [text](url)
    content = re.sub(r'`(\[[^\]]+\]\([^)]+\))`', r'\1', content)
    
    return content


def enrich_file(file_path: Path) -> bool:
    """
    Enrich links in a single markdown file.
    
    Returns True if file was modified.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        original = f.read()
    
    # Process content (skip code blocks)
    lines = original.split('\n')
    result_lines = []
    in_code_block = False
    
    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue
        
        if in_code_block:
            result_lines.append(line)
            continue
        
        # Skip certain line types
        stripped = line.strip()
        if stripped.startswith('![') or stripped.startswith('#'):
            result_lines.append(line)
            continue
        
        # Enrich this line
        enriched = enrich_content(line, file_path)
        result_lines.append(enriched)
    
    new_content = '\n'.join(result_lines)
    
    if new_content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description='Enrich documentation links using Master Object Collection.')
    parser.add_argument('--file', help='Specific file to enrich')
    parser.add_argument('--all', action='store_true', help='Process all documentation directories')
    args = parser.parse_args()
    
    if not OBJECTS:
        print("ERROR: Master Collection is empty.")
        return 1
    
    print(f"Loaded {len(OBJECTS)} objects from Master Collection")
    print(f"Object types: {', '.join(OBJECT_TYPES.keys())}")
    
    count = 0
    
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}")
            return 1
        
        print(f"Processing: {file_path}")
        if enrich_file(file_path):
            count += 1
            print(f"  Enriched: {file_path.name}")
        else:
            print(f"  No changes: {file_path.name}")
    
    else:
        # Process all documentation directories
        dirs = [
            CWD / 'legacy-system' / 'oracle-forms-overviews' / 'forms',
            CWD / 'legacy-system' / 'oracle-forms-overviews' / 'reports',
            CWD / 'legacy-system' / 'oracle-forms-overviews' / 'menus',
            CWD / 'legacy-system' / 'oracle-forms-overviews' / 'libraries',
            CWD / 'legacy-system' / 'business-workflows',
            CWD / 'legacy-system' / 'business-rules',
            CWD / 'legacy-system' / 'applications',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'tables',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'views',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'packages',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'procedures',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'functions',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'constraints',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'indexes',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'sequences',
            CWD / 'legacy-system' / 'oracle-database-overviews' / 'types',
        ]
        
        for d in dirs:
            if not d.exists():
                continue
            print(f"\nScanning: {d}")
            for f in d.glob('*.md'):
                if enrich_file(f):
                    count += 1
                    print(f"  Enriched: {f.name}")
    
    print(f"\n{'='*60}")
    print(f"Enrichment complete. Modified {count} files.")
    
    if ORPHANED_ROLES:
        print(f"\nFound {len(ORPHANED_ROLES)} orphaned roles (not in collection):")
        for role in sorted(ORPHANED_ROLES.keys())[:10]:
            print(f"  - {role}")
        if len(ORPHANED_ROLES) > 10:
            print(f"  ... and {len(ORPHANED_ROLES) - 10} more")
    
    return 0


if __name__ == "__main__":
    exit(main())
