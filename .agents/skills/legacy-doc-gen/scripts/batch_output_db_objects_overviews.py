#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/batch_output_db_objects_overviews.py (CLI)
=====================================

Purpose:
    Batch generates overview documentation for DB objects.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/batch_output_db_objects_overviews.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --type          : Object type to process
    --limit         : Limit number of files per type
    --dry-run       : Show what would be done

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - parse_sql_file(): Parse SQL file to extract basic metadata.
    - generate_overview(): Generate overview markdown from metadata.
    - process_type(): Process all files of a given type.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()

# Add scripts path for miner imports (co-located in same folder)
sys.path.insert(0, str(SCRIPT_DIR))

# Object type configurations - FULL COVERAGE (9 types)
DB_OBJECT_TYPES = {
    # Structural - Core Data Model
    'db_table': {
        'source_dir': 'legacy-system/oracle-database/Tables',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/tables',
        'naming': '{name}-Table-Overview.md',
        'display_name': 'Table',
        'category': 'structural',
        'template': 'assets/templates/db-table-template.md' # Relative to skill root
    },
    'db_view': {
        'source_dir': 'legacy-system/oracle-database/Views',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/views',
        'naming': '{name}-View-Overview.md',
        'display_name': 'View',
        'category': 'structural',
        'template': 'assets/templates/db-view-template.md' # Relative to skill root
    },
    'db_constraint': {
        'source_dir': 'legacy-system/oracle-database/Constraints',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/constraints',
        'naming': '{name}-Constraint-Overview.md',
        'display_name': 'Constraint',
        'category': 'structural',
        'template': 'assets/templates/db-constraint-template.md' # Relative to skill root
    },
    'db_index': {
        'source_dir': 'legacy-system/oracle-database/Indexes',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/indexes',
        'naming': '{name}-Index-Overview.md',
        'display_name': 'Index',
        'category': 'structural',
        'template': 'assets/templates/db-index-template.md' # Relative to skill root
    },
    'db_sequence': {
        'source_dir': 'legacy-system/oracle-database/Sequences',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/sequences',
        'naming': '{name}-Sequence-Overview.md',
        'display_name': 'Sequence',
        'category': 'structural',
        'template': 'assets/templates/db-sequence-template.md' # Relative to skill root
    },
    'db_type': {
        'source_dir': 'legacy-system/oracle-database/Types',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/types',
        'naming': '{name}-Type-Overview.md',
        'display_name': 'Type',
        'category': 'structural',
        'template': 'assets/templates/db-type-template.md' # Relative to skill root
    },
    # Logic - Contains Business Rules
    'db_procedure': {
        'source_dir': 'legacy-system/oracle-database/Procedures',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/procedures',
        'naming': '{name}-Procedure-Overview.md',
        'display_name': 'Procedure',
        'category': 'logic',
        'template': 'assets/templates/db-procedure-template.md' # Relative to skill root
    },
    'db_function': {
        'source_dir': 'legacy-system/oracle-database/Functions',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/functions',
        'naming': '{name}-Function-Overview.md',
        'display_name': 'Function',
        'category': 'logic',
        'template': 'assets/templates/db-function-template.md' # Relative to skill root
    },
    'db_package': {
        'source_dir': 'legacy-system/oracle-database/Packages',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/packages',
        'naming': '{name}-Package-Overview.md',
        'display_name': 'Package',
        'category': 'logic',
        'template': 'assets/templates/db-package-template.md' # Relative to skill root
    },
    'db_trigger': {
        'source_dir': 'legacy-system/oracle-database/Triggers',
        'pattern': '*.sql',
        'output_dir': 'legacy-system/oracle-database-overviews/triggers',
        'naming': '{name}-Trigger-Overview.md',
        'display_name': 'Trigger',
        'category': 'logic',
        'template': 'assets/templates/db-trigger-template.md' # Relative to skill root
    }
}


def load_template(obj_type: str) -> str:
    """Load external template file."""
    config = DB_OBJECT_TYPES.get(obj_type)
    if not config or 'template' not in config:
        return ""
    
    # Template paths are relative to the skill root (SCRIPT_DIR.parent)
    template_path = SCRIPT_DIR.parent / config['template']
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    return ""


def parse_sql_file(file_path: Path, obj_type: str) -> dict:
    """Parse SQL file to extract basic metadata."""
    content = file_path.read_text(encoding='utf-8', errors='ignore')
    name = file_path.stem.upper()
    
    metadata = {
        'name': name,
        'source_file': str(file_path.relative_to(PROJECT_ROOT)),
        'type': obj_type,
        'columns': [],
        'parameters': [],
        'dependencies': [],
        'signature': ''
    }
    
    # Extract based on type
    if obj_type in ('db_table', 'db_view'):
        # Extract column definitions (simplified)
        import re
        col_matches = re.findall(r'"(\w+)"\s+(\w+)', content)
        for col_name, col_type in col_matches[:20]:  # Limit to first 20
            metadata['columns'].append({'name': col_name, 'type': col_type})
            
        # Extract table references in views
        if obj_type == 'db_view':
            table_refs = re.findall(r'FROM\s+"?\w+"?\.?"?(\w+)"?', content, re.IGNORECASE)
            metadata['dependencies'] = list(set(table_refs))[:10]
    
    elif obj_type in ('db_procedure', 'db_function'):
        import re
        # Extract signature (first CREATE line)
        sig_match = re.search(r'(CREATE\s+OR\s+REPLACE\s+(?:EDITIONABLE\s+)?(?:FUNCTION|PROCEDURE)\s+[^\n]+)', content, re.IGNORECASE)
        if sig_match:
            metadata['signature'] = sig_match.group(1).strip()
        
        # Extract parameters
        param_matches = re.findall(r'(\w+)\s+(IN|OUT|IN\s+OUT)\s+(\w+)', content, re.IGNORECASE)
        for name, direction, ptype in param_matches[:10]:
            metadata['parameters'].append({'name': name, 'direction': direction, 'type': ptype})

    elif obj_type == 'db_trigger':
        import re
        metadata['trigger_info'] = {
            'target_table': None,
            'timing': None,
            'events': [],
            'row_level': False,
            'calls_packages': [],
            'is_audit': False,
            'is_journal': False
        }
        
        # Extract timing (BEFORE/AFTER)
        timing_match = re.search(r'\b(BEFORE|AFTER)\s+(INSERT|UPDATE|DELETE)', content, re.IGNORECASE)
        if timing_match:
            metadata['trigger_info']['timing'] = timing_match.group(1).upper()
        
        # Extract events
        if re.search(r'\bINSERT\b', content, re.IGNORECASE):
            metadata['trigger_info']['events'].append('INSERT')
        if re.search(r'\bUPDATE\b', content, re.IGNORECASE):
            metadata['trigger_info']['events'].append('UPDATE')
        if re.search(r'\bDELETE\b', content, re.IGNORECASE):
            metadata['trigger_info']['events'].append('DELETE')
        
        # Extract target table
        table_match = re.search(r'\bON\s+(?:Project\.)?(?:PROJECT_)?(\w+)', content, re.IGNORECASE)
        if table_match:
            metadata['trigger_info']['target_table'] = table_match.group(1).upper()
        
        # Check FOR EACH ROW
        if re.search(r'FOR\s+EACH\s+ROW', content, re.IGNORECASE):
            metadata['trigger_info']['row_level'] = True
        
        # Detect package calls
        pkg_matches = re.findall(r'(\w+)\.(\w+)\s*\(', content)
        for pkg, proc in pkg_matches:
            if pkg.upper() not in ['NEW', 'OLD', 'DBMS_OUTPUT', 'STANDARD']:
                metadata['trigger_info']['calls_packages'].append(f"{pkg}.{proc}".upper())
        metadata['trigger_info']['calls_packages'] = list(set(metadata['trigger_info']['calls_packages']))[:5]
        
        # Detect patterns
        if 'SetAuditFields' in content or 'appl_audit' in content.lower():
            metadata['trigger_info']['is_audit'] = True
        if '_JN_TRG' in content or 'Project_Audit_Triggers' in content:
            metadata['trigger_info']['is_journal'] = True
    
    return metadata


def generate_overview(metadata: dict, config: dict) -> str:
    """Generate overview markdown from metadata."""
    obj_type = metadata['type']
    today = datetime.now().strftime('%Y-%m-%d')
    template = load_template(obj_type)
    
    if not template:
        # Fallback to minimal if template missing
        return f"# {metadata['name']} - {config['display_name']} Overview\n\nTemplate missing."

    # Common replacements
    name = metadata['name']
    content = template.replace('{TABLE_NAME}', name)
    content = content.replace('{TRIGGER_NAME}', name)
    content = content.replace('{PACKAGE_NAME}', name)
    content = content.replace('{FUNCTION_NAME}', name)
    content = content.replace('{PROCEDURE_NAME}', name)
    content = content.replace('{INDEX_NAME}', name)
    content = content.replace('{SEQUENCE_NAME}', name)
    content = content.replace('{TYPE_NAME}', name)
    content = content.replace('{CONSTRAINT_NAME}', name)
    content = content.replace('{SCHEMA_NAME}', os.getenv('APP_SCHEMA', 'FIS'))
    content = content.replace('{APPLICATION}', os.getenv('APP_ACRONYM', 'FIS'))
    content = content.replace('{DATE}', today)
    content = content.replace('{filename}', Path(metadata['source_file']).name)

    # SQL definitions
    raw_sql = metadata.get('raw_sql', '*(See source)*')
    content = content.replace('{VIEW_SQL}', raw_sql)
    content = content.replace('{CONSTRAINT_DEFINITION}', raw_sql)
    content = content.replace('{INDEX_DEFINITION}', raw_sql)
    content = content.replace('{SEQUENCE_DEFINITION}', raw_sql)
    content = content.replace('{TYPE_DEFINITION}', raw_sql)
    content = content.replace('{PROCEDURE_SIGNATURE}', metadata.get('signature', raw_sql))

    if obj_type in ('db_table', 'db_view'):
        columns_rows = ""
        for col in metadata.get('columns', []):
            columns_rows += f"| {col['name']} | {col['type']} | - | - | - |\n"
        if not columns_rows:
            columns_rows = "| *(Analyze source)* | | | | |\n"
        content = content.replace('| {COLUMN_NAME} | {DATA_TYPE} | Yes/No | {DEFAULT} | {DESCRIPTION} |', columns_rows)
    
    elif obj_type == 'db_trigger':
        tinfo = metadata.get('trigger_info', {})
        timing = tinfo.get('timing') or 'BEFORE/AFTER'
        events_list = tinfo.get('events', [])
        events = '/'.join(events_list) or 'INSERT/UPDATE/DELETE'
        content = content.replace('{BEFORE/AFTER} {INSERT/UPDATE/DELETE}', f"{timing} {events}")
        content = content.replace('{TABLE_NAME}', tinfo.get('target_table') or '{TABLE}')
        
        ins = 'Yes' if 'INSERT' in events_list else 'No'
        upd = 'Yes' if 'UPDATE' in events_list else 'No'
        bel = 'Yes' if 'DELETE' in events_list else 'No'
        content = content.replace('INSERT | Yes/No', f"INSERT | {ins}")
        content = content.replace('UPDATE | Yes/No', f"UPDATE | {upd}")
        content = content.replace('DELETE | Yes/No', f"DELETE | {bel}")

    return content


def process_type(obj_type: str, limit: int = None, dry_run: bool = False, force: bool = False) -> dict:
    """Process all files of a given type."""
    config = DB_OBJECT_TYPES[obj_type]
    source_path = PROJECT_ROOT / config['source_dir']
    output_dir = PROJECT_ROOT / config['output_dir'] # Renamed to output_dir for clarity
    
    # Ensure output directory exists
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all source files
    files = list(source_path.glob(config['pattern']))
    if limit:
        files = files[:limit]
    
    stats = {'total': len(files), 'created': 0, 'skipped': 0, 'errors': 0}
    
    print(f"\nProcessing {config['display_name']}s: {len(files)} files")
    print(f"  Source: {source_path}")
    print(f"  Output: {output_dir}")
    
    for i, file in enumerate(files):
        name = file.stem.upper()
        out_file = output_dir / config['naming'].format(name=name)
        
        # Skip if exists (unless force)
        if out_file.exists() and not force:
            stats['skipped'] += 1
            continue
        
        try:
            metadata = parse_sql_file(file, obj_type)
            content = generate_overview(metadata, config)
            
            if dry_run:
                print(f"  [DRY] Would create: {out_file.name}")
            else:
                out_file.write_text(content, encoding='utf-8')
                stats['created'] += 1
                
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(files)}...")
                
        except Exception as e:
            stats['errors'] += 1
            print(f"  ERROR: {file.name}: {e}")
    
    print(f"  Done: {stats['created']} created, {stats['skipped']} skipped, {stats['errors']} errors")
    return stats


def main():
    parser = argparse.ArgumentParser(description='Batch process database objects')
    parser.add_argument('--type', choices=list(DB_OBJECT_TYPES.keys()) + ['all'], 
                        default='all', help='Object type to process')
    parser.add_argument('--limit', type=int, help='Limit number of files per type')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Database Object Documentation Generator")
    print("=" * 60)
    
    types_to_process = list(DB_OBJECT_TYPES.keys()) if args.type == 'all' else [args.type]
    
    all_stats = {}
    for obj_type in types_to_process:
        all_stats[obj_type] = process_type(obj_type, args.limit, args.dry_run, args.force)
    
    print("\n" + "=" * 60)
    print("Summary:")
    total_created = sum(s['created'] for s in all_stats.values())
    total_skipped = sum(s['skipped'] for s in all_stats.values())
    print(f"  Total Created: {total_created}")
    print(f"  Total Skipped: {total_skipped}")
    print("=" * 60)
    
    if not args.dry_run and total_created > 0:
        print("\nNext steps:")
        print("  1. Run enrich_links_v2.py to create smart links")
        print("  2. Update master_object_collection.json with new artifacts")


if __name__ == "__main__":
    main()
