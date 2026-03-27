#!/usr/bin/env python3
"""
[SKILL_ROOT]/scripts/batch_enrich_db_overviews.py (CLI)
=====================================

Purpose:
    Enriches DB object overviews with SQL and dependency info.

Layer: Curate / Documentation

Usage Examples:
    python [SKILL_ROOT]/scripts/batch_enrich_db_overviews.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --type          : N/A
    --limit         : N/A

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_dependency_map(): No description.
    - get_callers(): Find all objects that reference this object using dependency map.
    - get_table_constraints(): Find constraints for this table.
    - get_table_indexes(): Find indexes for this table.
    - parse_table_sql(): Parse CREATE TABLE statement.
    - parse_view_sql(): Extract full VIEW definition.
    - parse_procedure_sql(): Parse procedure/function signature.
    - load_master_collection(): No description.
    - get_context_description(): Get description from master object collection.
    - update_table_overview(): Update table overview with parsed SQL data.
    - get_downstream_dependencies(): Find objects this view depends on.
    - update_view_overview(): Update view overview with parsed SQL data.
    - update_generic_db_object(): Generic updater for Packages, Procedures, Functions, Types, etc.
    - update_package_overview(): No description.
    - update_procedure_overview(): No description.
    - update_function_overview(): No description.
    - update_type_overview(): No description.
    - update_constraint_overview(): No description.
    - update_index_overview(): No description.
    - update_sequence_overview(): No description.
    - process_type(): Process all overviews of a given type.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()

# Add scripts path for imports (co-located in same folder)
sys.path.insert(0, str(SCRIPT_DIR))

# Paths
BASE_DIR = PROJECT_ROOT / 'legacy-system'
DEPENDENCY_MAP = BASE_DIR / 'reference-data' / 'inventories' / 'dependency_map.json'
OVERVIEWS_DIR = BASE_DIR / 'oracle-database-overviews'
SOURCE_DIR = BASE_DIR / 'oracle-database'

# Load dependency map
def load_dependency_map():
    if DEPENDENCY_MAP.exists():
        with open(DEPENDENCY_MAP) as f:
            return json.load(f)
    return {}

DEPS = load_dependency_map()


def get_callers(obj_name: str, is_package: bool = False) -> dict:
    """Find all objects that reference this object using dependency map."""
    callers = {
        'Forms': [],
        'Libraries': [],
        'Packages': [],
        'Procedures': [],
        'Functions': [],
        'Views': []
    }
    obj_upper = obj_name.upper()
    obj_prefix = obj_upper + '.'
    
    # Identify parent package if applicable (e.g. PKG.PROC -> PKG)
    parent_obj = None
    if '.' in obj_upper and not is_package:
        parent_obj = obj_upper.split('.')[0]
    
    # Search through dependency map for objects that have this object in their dependencies
    for obj_id, obj_data in DEPS.items():
        if not isinstance(obj_data, dict):
            continue
        
        deps = obj_data.get('Dependencies', {})
        found = False
        
        # Check all dependency lists (Tables, Views, Packages, Procs, Funcs, ExternalCalls)
        for dep_list in deps.values():
            if not isinstance(dep_list, list):
                continue
                
            # 1. Direct match (Exact Object Name)
            if obj_upper in dep_list:
                found = True
                break
            
            # 2. Parent Package Match (if applicable)
            if parent_obj and parent_obj in dep_list:
                found = True
                break
                
            # 3. Package Member Match (if checking a Package)
            if is_package:
                for dep in dep_list:
                    if dep.startswith(obj_prefix):
                        found = True
                        break
                if found:
                    break
        
        if found:
            obj_type = obj_data.get('Type')
            if obj_type == 'FORM':
                callers['Forms'].append(obj_id)
            elif obj_type == 'PLL':
                callers['Libraries'].append(obj_id)
            elif obj_type == 'DB_PACKAGE':
                callers['Packages'].append(obj_id)
            elif obj_type == 'DB_PROCEDURE':
                callers['Procedures'].append(obj_id)
            elif obj_type == 'DB_FUNCTION':
                callers['Functions'].append(obj_id)
            elif obj_type == 'VIEW':
                callers['Views'].append(obj_id)
    
    # Sort all
    for k in callers:
        callers[k] = sorted(set(callers[k]))[:20]  # Limit to 20
    
    return callers


def get_table_constraints(table_name: str) -> list:
    """Find constraints for this table."""
    constraints_dir = SOURCE_DIR / 'Constraints'
    constraints = []
    
    if constraints_dir.exists():
        for f in constraints_dir.glob('*.sql'):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if table_name.upper() in content.upper():
                    constraints.append(f.stem)
            except:
                pass
    
    return constraints[:10]


def get_table_indexes(table_name: str) -> list:
    """Find indexes for this table."""
    indexes_dir = SOURCE_DIR / 'Indexes'
    indexes = []
    
    if indexes_dir.exists():
        for f in indexes_dir.glob('*.sql'):
            try:
                content = f.read_text(encoding='utf-8', errors='ignore')
                if table_name.upper() in content.upper():
                    indexes.append(f.stem)
            except:
                pass
    
    return indexes[:10]


def parse_table_sql(sql_path: Path) -> dict:
    """Parse CREATE TABLE statement."""
    content = sql_path.read_text(encoding='utf-8', errors='ignore')
    
    columns = []
    # Oracle format: ,COLUMN_NAME TYPE(size) [NOT NULL]
    # or (COLUMN_NAME TYPE(size) [NOT NULL] at start
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        # Skip empty, CREATE, TABLESPACE, etc
        if not line or line.startswith('CREATE') or line.startswith('TABLESPACE') or line.startswith('/') or line.startswith('PROMPT'):
            continue
        # Remove leading comma or paren
        line = line.lstrip(',()')
        # Match: COLUMN_NAME TYPE(size) [NOT NULL]
        match = re.match(r'(\w+)\s+(VARCHAR2|NUMBER|DATE|CLOB|BLOB|CHAR|TIMESTAMP|RAW|LONG|INTEGER|NVARCHAR2)(?:\(([^)]+)\))?\s*(NOT NULL)?', line, re.IGNORECASE)
        if match:
            col_name, col_type, col_size, not_null = match.groups()
            columns.append({
                'name': col_name,
                'type': f"{col_type}({col_size})" if col_size else col_type,
                'nullable': 'No' if not_null else 'Yes'
            })
    
    return {'columns': columns, 'raw_sql': content}


def parse_view_sql(sql_path: Path) -> str:
    """Extract full VIEW definition."""
    content = sql_path.read_text(encoding='utf-8', errors='ignore')
    # Return cleaned content
    return content.strip()


def parse_procedure_sql(sql_path: Path) -> dict:
    """Parse procedure/function signature."""
    content = sql_path.read_text(encoding='utf-8', errors='ignore')
    
    # Extract signature
    sig_match = re.search(r'(CREATE\s+OR\s+REPLACE\s+(?:EDITIONABLE\s+)?(?:FUNCTION|PROCEDURE)\s+[^\n]+(?:\n[^)]+\))?)', content, re.IGNORECASE | re.DOTALL)
    signature = sig_match.group(1).strip() if sig_match else ''
    
    # Extract parameters
    params = []
    param_pattern = r'(\w+)\s+(IN|OUT|IN\s+OUT)\s+(\w+)'
    for match in re.finditer(param_pattern, content[:2000], re.IGNORECASE):
        params.append({
            'name': match.group(1),
            'direction': match.group(2).upper(),
            'type': match.group(3)
        })
    
    return {'signature': signature, 'parameters': params}


# Load Master Collection for Context Descriptions
MASTER_COLLECTION_PATH = PROJECT_ROOT / 'legacy-system' / 'reference-data' / 'master_object_collection.json'

def load_master_collection():
    if MASTER_COLLECTION_PATH.exists():
        try:
            with open(MASTER_COLLECTION_PATH) as f:
                data = json.load(f)
                return data.get('objects', {})
        except:
            return {}
    return {}

OBJECTS = load_master_collection()

def get_context_description(obj_id):
    """Get description from master object collection."""
    obj = OBJECTS.get(obj_id.upper())
    if obj:
        # Prefer name provided in inventory
        return obj.get('name', '-')
    return '-'

def update_table_overview(overview_path: Path, sql_path: Path, obj_name: str):
    """Update table overview with parsed SQL data."""
    if not sql_path.exists():
        return False
    
    parsed = parse_table_sql(sql_path)
    callers = get_callers(obj_name)
    constraints = get_table_constraints(obj_name)
    indexes = get_table_indexes(obj_name)
    
    # Build columns table
    cols_md = "| Column | Type | Nullable | Description |\n|---|---|---|---|\n"
    if parsed['columns']:
        for col in parsed['columns'][:30]:
            cols_md += f"| {col['name']} | {col['type']} | {col['nullable']} | - |\n"
    else:
        cols_md += "| *(See source SQL)* | | | |\n"
    
    # Build constraints table
    constraints_md = "| Constraint | Type | Definition |\n|---|---|---|\n"
    if constraints:
        for c in constraints:
            constraints_md += f"| [{c}] | - | - |\n"
    else:
        constraints_md += "| *(None detected)* | | |\n"
    
    # Build indexes table
    indexes_md = "| Index | Columns | Purpose |\n|---|---|---|\n"
    if indexes:
        for idx in indexes:
            indexes_md += f"| [{idx}] | - | - |\n"
    else:
        indexes_md += "| *(None detected)* | | |\n"
    
    # Build callers section (by type)
    callers_md = ""
    has_callers = any(callers.values())
    if has_callers:
        if callers['Forms']:
            callers_md += "### Forms\n| Form | Context |\n|---|---|\n"
            for f in callers['Forms']:
                desc = get_context_description(f)
                callers_md += f"| [{f}] | {desc} |\n"
            callers_md += "\n"
        
        if callers['Libraries']:
            callers_md += "### Libraries\n| Library | Context |\n|---|---|\n"
            for lib in callers['Libraries']:
                desc = get_context_description(lib)
                callers_md += f"| [{lib}] | {desc} |\n"
            callers_md += "\n"
        
        if callers['Packages']:
            callers_md += "### Packages\n| Package | Context |\n|---|---|\n"
            for pkg in callers['Packages']:
                desc = get_context_description(pkg)
                callers_md += f"| [{pkg}] | {desc} |\n"
            callers_md += "\n"
        
        if callers['Views']:
            callers_md += "### Views\n| View | Context |\n|---|---|\n"
            for v in callers['Views']:
                desc = get_context_description(v)
                callers_md += f"| [{v}] | {desc} |\n"
            callers_md += "\n"
    else:
        callers_md = "*(None detected in dependency map)*\n"
    
    # Relative path to SQL source
    rel_sql_path = f"../../oracle-database/Tables/{obj_name}.sql"
    
    # Read current content
    content = overview_path.read_text()
    
    # Update Source File to be a clickable link
    content = re.sub(
        r'\| \*\*Source File\*\* \| `[^`]+` \|',
        f'| **Source File** | [{obj_name}.sql]({rel_sql_path}) |',
        content
    )
    
    # Replace columns section
    content = re.sub(
        r'## Columns\n\|[^\n]+\n\|[^\n]+\n(?:\|[^\n]+\n)*',
        f'## Columns\n{cols_md}',
        content
    )
    
    # Replace Constraints section
    content = re.sub(
        r'## Constraints\n\|[^\n]+\n\|[^\n]+\n(?:\|[^\n]+\n)*',
        f'## Constraints\n{constraints_md}',
        content
    )
    
    # Replace or add Indexes section
    if '## Indexes' in content:
        content = re.sub(
            r'## Indexes\n\|[^\n]+\n\|[^\n]+\n(?:\|[^\n]+\n)*',
            f'## Indexes\n{indexes_md}',
            content
        )
    
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(r'Last Analyzed\*\* \| \d{4}-\d{2}-\d{2}', f'Last Analyzed** | {today}', content)
    
    overview_path.write_text(content, encoding='utf-8')
    return True


def get_downstream_dependencies(obj_name: str) -> dict:
    """Find objects this view depends on."""
    downstream = {
        'Tables': [],
        'Views': [],
        'Packages': []
    }
    
    obj_data = DEPS.get(obj_name.upper())
    if obj_data:
        deps = obj_data.get('Dependencies', {})
        if 'Tables' in deps:
            downstream['Tables'] = sorted(deps['Tables'])
        if 'Views' in deps:
            downstream['Views'] = sorted(deps['Views'])
        if 'Packages' in deps:
            downstream['Packages'] = sorted(deps['Packages'])
            
    return downstream


def update_view_overview(overview_path: Path, sql_path: Path, obj_name: str):
    """Update view overview with parsed SQL data."""
    if not sql_path.exists():
        return False
    
    view_sql = parse_view_sql(sql_path)
    callers = get_callers(obj_name)
    dependencies = get_downstream_dependencies(obj_name)
    
    # Build Dependencies section (Downstream)
    deps_md = ""
    has_deps = any(dependencies.values())
    if has_deps:
        if dependencies['Tables']:
            deps_md += "### Tables\n| Table | Access |\n|---|---|\n"
            for t in dependencies['Tables']:
                deps_md += f"| [{t}] | SELECT |\n"
            deps_md += "\n"
        if dependencies['Views']:
            deps_md += "### Views\n| View | Access |\n|---|---|\n"
            for v in dependencies['Views']:
                deps_md += f"| [{v}] | SELECT |\n"
            deps_md += "\n"
    else:
        deps_md = "*(None detected)*\n"

    # Build Callers section (Upstream)
    callers_md = ""
    has_callers = any(callers.values())
    if has_callers:
        if callers['Forms']:
            callers_md += "### Forms\n| Form | Context |\n|---|---|\n"
            for f in callers['Forms']:
                desc = get_context_description(f)
                callers_md += f"| [{f}] | {desc} |\n"
            callers_md += "\n"
        if callers['Packages']:
            callers_md += "### Packages\n| Package | Context |\n|---|---|\n"
            for pkg in callers['Packages']:
                desc = get_context_description(pkg)
                callers_md += f"| [{pkg}] | {desc} |\n"
            callers_md += "\n"
        if callers['Views']:
            callers_md += "### Views\n| View | Context |\n|---|---|\n"
            for v in callers['Views']:
                desc = get_context_description(v)
                callers_md += f"| [{v}] | {desc} |\n"
            callers_md += "\n"
    else:
        callers_md = "*(None detected)*\n"
    
    # Relative path to SQL source
    rel_sql_path = f"../../oracle-database/Views/{obj_name}.sql"
    
    content = overview_path.read_text()
    
    # Update Source File link
    content = re.sub(
        r'\| \*\*Source File\*\* \| `[^`]+` \|',
        f'| **Source File** | [{obj_name}.sql]({rel_sql_path}) |',
        content
    )
    
    # Update View Definition
    # We escape the SQL slightly to ensure triple backticks don't break
    view_sql_safe = view_sql.replace('```', "'''")
    content = re.sub(
        r'```sql\n\{VIEW_SQL\}\n```',
        f'```sql\n{view_sql_safe}\n```',
        content
    )
    
    # Update Relationships/Dependencies (Downstream)
    # Using "Relationships" section in template
    if '## Relationships' in content:
        content = re.sub(
            r'## Relationships.*',
            f'## Dependencies (Downstream)\n{deps_md}\n\n## Called By (Upstream Dependencies)\n{callers_md}',
            content,
            flags=re.DOTALL
        )
    elif '## Used By' in content: # Fallback
        content = re.sub(
             r'## Used By.*',
             f'## Dependencies (Downstream)\n{deps_md}\n\n## Called By (Upstream Dependencies)\n{callers_md}',
             content,
             flags=re.DOTALL
        )
        
    # Update timestamp
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(r'Last Analyzed\*\* \| \d{4}-\d{2}-\d{2}', f'Last Analyzed** | {today}', content)

    overview_path.write_text(content, encoding='utf-8')
    return True


def update_generic_db_object(overview_path: Path, sql_path: Path, obj_name: str, type_label: str, source_folder: str = None):
    """Generic updater for Packages, Procedures, Functions, Types, etc."""
    if not sql_path.exists():
        # Try to find file with case insensitivity? 
        # For now return false
        return False
    
    # Read Source
    try:
        source_content = sql_path.read_text(encoding='utf-8', errors='ignore')
    except:
        return False

    is_package = (type_label == 'Package')
    callers = get_callers(obj_name, is_package=is_package)
    dependencies = get_downstream_dependencies(obj_name)
    
    # Build Dependencies section (Downstream)
    deps_md = ""
    has_deps = any(dependencies.values())
    if has_deps:
        if dependencies.get('Tables'):
            deps_md += "### Tables\n| Table | Access |\n|---|---|\n"
            for t in dependencies['Tables']:
                deps_md += f"| [{t}] | SELECT/DML |\n"
            deps_md += "\n"
        if dependencies.get('Views'):
            deps_md += "### Views\n| View | Access |\n|---|---|\n"
            for v in dependencies['Views']:
                deps_md += f"| [{v}] | SELECT |\n"
            deps_md += "\n"
        if dependencies.get('Packages'):
            deps_md += "### Packages\n| Package | Access |\n|---|---|\n"
            for p in dependencies['Packages']:
                 deps_md += f"| [{p}] | EXECUTE |\n"
            deps_md += "\n"
    else:
        deps_md = "*(None detected)*\n"

    # Build Callers section (Upstream)
    callers_md = ""
    has_callers = any(callers.values())
    if has_callers:
        if callers['Forms']:
            callers_md += "### Forms\n| Form | Context |\n|---|---|\n"
            for f in callers['Forms']:
                desc = get_context_description(f)
                callers_md += f"| [{f}] | {desc} |\n"
            callers_md += "\n"
        if callers['Packages']:
            callers_md += "### Packages\n| Package | Context |\n|---|---|\n"
            for pkg in callers['Packages']:
                desc = get_context_description(pkg)
                callers_md += f"| [{pkg}] | {desc} |\n"
            callers_md += "\n"
        if callers['Views']:
            callers_md += "### Views\n| View | Context |\n|---|---|\n"
            for v in callers['Views']:
                desc = get_context_description(v)
                callers_md += f"| [{v}] | {desc} |\n"
            callers_md += "\n"
        if callers['Procedures']:
            callers_md += "### Procedures\n| Procedure | Context |\n|---|---|\n"
            for p in callers['Procedures']:
                desc = get_context_description(p)
                callers_md += f"| [{p}] | {desc} |\n"
            callers_md += "\n"
    else:
        callers_md = "*(None detected)*\n"
    
    # Relative path to SQL source
    if not source_folder:
        source_folder = f"{type_label}s" # Default pluralization
    rel_sql_path = f"../../oracle-database/{source_folder}/{obj_name}.sql"
    
    content = overview_path.read_text()
    
    content = re.sub(
        r'\| \*\*Source File\*\* \| `[^`]+` \|',
        f'| **Source File** | [{obj_name}.sql]({rel_sql_path}) |',
        content
    )

    # 1. Logic for Package: Add "## Contains" section
    if type_label == 'Package':
        obj_upper = obj_name.upper()
        
        # Method A: DEPS keys (Split files)
        members_deps = [k for k in DEPS.keys() if k.startswith(obj_upper + '.')]
        
        # Method B: Parse SQL source (Monolithic)
        # Simple regex to find exposed Procedures/Functions in Spec
        # Matches: PROCEDURE Name ... or FUNCTION Name ...
        # We assume source_content contains the spec
        members_sql = []
        if source_content:
             # Match PROCEDURE <Name> or FUNCTION <Name>
             # We handle optional whitespace and basic parameter start
             matches = re.findall(r'(?i)^\s*(PROCEDURE|FUNCTION)\s+([A-Z0-9_$#]+)', source_content, re.MULTILINE)
             for rectype, name in matches:
                 members_sql.append((f"{obj_upper}.{name.upper()}", rectype.title())) # FQDN
        
        # Combine
        all_members = {} # Key: Name, Value: Type
        
        for m in members_deps:
            all_members[m] = DEPS[m].get('Type', 'Unknown')
        
        for m_name, m_type in members_sql:
            if m_name not in all_members:
                 all_members[m_name] = f"DB_{m_type.upper()}" # Align with DEPS type format roughly or just use human readable?
                 # Actually DEPS uses 'DB_PROCEDURE'. Let's use human friendly "Procedure" here if we want, or map it.
                 # Let's clean up types for display.
        
        if all_members:
            rows = []
            for m in sorted(all_members.keys()):
                raw_type = all_members[m]
                display_type = raw_type.replace('DB_', '').title()
                
                # If it's in DEPS, we might have a link (files exist)
                # If it's only in SQL, we don't have a separate overview file...
                # So we should probably link to the Package anchor? e.g. #procedure-name?
                # Or just listing it is fine.
                if m in members_deps:
                     link = f"[{m}]" # Smart link resolves to file
                else:
                     # Internal member, no file. Link to package source anchor or just text
                     # For now, let's just make it bold text or link to self anchor?
                     link = m # No overview
                     
                rows.append(f"| {link} | {display_type} |")
            
            contains_tbl = "| Member | Type |\n|---|---|\n" + "\n".join(rows)
            contains_section = f"\n## Contains\n{contains_tbl}\n"
            
            # Insert after Purpose section if it exists
            # Update regex to replace existing Contains if present (re-run safety)
            # Check if ## Contains exists
            if '## Contains' in content:
                 content = re.sub(
                    r'## Contains\n.*?((?=\n## )|\Z)',
                    f'## Contains\n{contains_tbl}\n',
                    content,
                    flags=re.DOTALL
                 )
            elif '## Purpose' in content:
                content = re.sub(
                    r'(## Purpose\n.*?(?=\n## |\Z))',
                    r'\1' + contains_section,
                    content,
                    flags=re.DOTALL
                )

    # 2. Logic for Member (Func/Proc): Add "Package" to Object Info
    if type_label in ['Procedure', 'Function'] and '.' in obj_name:
        parent = obj_name.split('.')[0]
        # Check if we already have Package row
        if '| **Package** |' not in content:
            # Insert after Type row. Path relative from functions/ or procedures/ to packages/
            # Assuming flat structure inside overviews/ (packages/, functions/)
            pkg_link = f"[{parent}](../packages/{parent}-Package-Overview.md)"
            content = re.sub(
                r'(\| \*\*Type\*\* \| .*? \|\n)',
                r'\1| **Package** | ' + pkg_link + ' |\n',
                content
            )
    
    # Update Definition/Code Block if placeholder exists
    # We look for simple placeholders like {SQL}, {PACKAGE_SPEC}, etc.
    # or just replace the generic code block
    
    # Simple formatting of source (truncated if too long for overview?)
    # For now, put full source but safe quoting
    source_safe = source_content.replace('```', "'''")
    
    if '{PACKAGE_SPEC}' in content:
        content = content.replace('{PACKAGE_SPEC}', source_safe)
    elif '{PROCEDURE_SQL}' in content:
        content = content.replace('{PROCEDURE_SQL}', source_safe)
    elif '{FUNCTION_SQL}' in content:
        content = content.replace('{FUNCTION_SQL}', source_safe)
    elif '{TYPE_SQL}' in content:
        content = content.replace('{TYPE_SQL}', source_safe)
    elif '{CONSTRAINT_SQL}' in content:
        content = content.replace('{CONSTRAINT_SQL}', source_safe)
    
    # Update Dependencies/Callers
    # 1. Handle "Called By" / "Called By (Upstream Dependencies)"
    # We use a pattern that matches the header and consumes until the next header
    
    # Generic matcher for "Called By..." block
    # Matches: ## Called By [optional suffix] \n [content until next ## or end]
    called_by_pattern = r'(## Called By(?: \(Upstream Dependencies\))?)\n(.*?)(?=\n## |\Z)'
    
    if re.search(called_by_pattern, content, re.DOTALL):
        content = re.sub(
            called_by_pattern,
            f'## Called By (Upstream Dependencies)\n{callers_md}',
            content,
            flags=re.DOTALL
        )
    
    # 2. Handle "Dependencies (Downstream)" / "Calls" / "Database Operations"
    # Matches: ## Dependencies (Downstream) \n [content]
    deps_pattern = r'(## Dependencies(?: \(Downstream\))?)\n(.*?)(?=\n## |\Z)'
    calls_pattern = r'(## (?:Calls|Database Operations))\n(.*?)(?=\n## |\Z)'
    
    # If we already have the new section, update it
    if re.search(deps_pattern, content, re.DOTALL):
        content = re.sub(
            deps_pattern,
            f'## Dependencies (Downstream)\n{deps_md}',
            content,
            flags=re.DOTALL
        )
    # Else check for legacy sections
    elif re.search(calls_pattern, content, re.DOTALL):
         content = re.sub(
            calls_pattern,
            f'## Dependencies (Downstream)\n{deps_md}',
            content,
            flags=re.DOTALL
        )

    # 3. Handle Generic "Dependencies" or "Used By" (Tables/Views legacy)
    # This might overlap with above if we aren't careful, but we check specific headers
    if '## Used By' in content:
             content = re.sub(
                r'## Used By.*?(?=\n## |\Z)',
                f'## Dependencies (Downstream)\n{deps_md}\n\n## Called By (Upstream Dependencies)\n{callers_md}',
                content,
                flags=re.DOTALL
             )
    elif '## Related Objects' in content:
             content = re.sub(
                r'## Related Objects.*?(?=\n## |\Z)',
                f'## Dependencies (Downstream)\n{deps_md}\n\n## Called By (Upstream Dependencies)\n{callers_md}',
                content,
                flags=re.DOTALL
             )
        
    # Update timestamp
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(r'Last Analyzed\*\* \| \d{4}-\d{2}-\d{2}', f'Last Analyzed** | {today}', content)

    overview_path.write_text(content, encoding='utf-8')
    return True

# Wrappers
def update_package_overview(o, s, n): return update_generic_db_object(o, s, n, 'Package', 'Packages')
def update_procedure_overview(o, s, n): return update_generic_db_object(o, s, n, 'Procedure', 'Procedures')
def update_function_overview(o, s, n): return update_generic_db_object(o, s, n, 'Function', 'Functions')
def update_type_overview(o, s, n): return update_generic_db_object(o, s, n, 'Type', 'Types')
def update_constraint_overview(o, s, n): return update_generic_db_object(o, s, n, 'Constraint', 'Constraints')
def update_index_overview(o, s, n): return update_generic_db_object(o, s, n, 'Index', 'Indexes')
def update_sequence_overview(o, s, n): return update_generic_db_object(o, s, n, 'Sequence', 'Sequences')


def process_type(obj_type: str, limit: int = None):
    """Process all overviews of a given type."""
    configs = {
        'db_table': {
            'overview_dir': OVERVIEWS_DIR / 'tables',
            'source_dir': SOURCE_DIR / 'Tables',
            'pattern': '*-Table-Overview.md',
            'updater': update_table_overview
        },
        'db_view': {
            'overview_dir': OVERVIEWS_DIR / 'views',
            'source_dir': SOURCE_DIR / 'Views',
            'pattern': '*-View-Overview.md',
            'updater': update_view_overview
        },
        'db_package': {
            'overview_dir': OVERVIEWS_DIR / 'packages',
            'source_dir': SOURCE_DIR / 'Packages',
            'pattern': '*-Package-Overview.md',
            'updater': update_package_overview
        },
        'db_procedure': {
            'overview_dir': OVERVIEWS_DIR / 'procedures',
            'source_dir': SOURCE_DIR / 'Procedures',
            'pattern': '*-Procedure-Overview.md',
            'updater': update_procedure_overview
        },
        'db_function': {
            'overview_dir': OVERVIEWS_DIR / 'functions',
            'source_dir': SOURCE_DIR / 'Functions',
            'pattern': '*-Function-Overview.md',
            'updater': update_function_overview
        },
        'db_type': {
            'overview_dir': OVERVIEWS_DIR / 'types',
            'source_dir': SOURCE_DIR / 'Types',
            'pattern': '*-Type-Overview.md',
            'updater': update_type_overview
        },
        'db_constraint': {
            'overview_dir': OVERVIEWS_DIR / 'constraints',
            'source_dir': SOURCE_DIR / 'Constraints',
            'pattern': '*-Constraint-Overview.md',
            'updater': update_constraint_overview
        },
        'db_index': {
            'overview_dir': OVERVIEWS_DIR / 'indexes',
            'source_dir': SOURCE_DIR / 'Indexes',
            'pattern': '*-Index-Overview.md',
            'updater': update_index_overview
        },
        'db_sequence': {
            'overview_dir': OVERVIEWS_DIR / 'sequences',
            'source_dir': SOURCE_DIR / 'Sequences',
            'pattern': '*-Sequence-Overview.md',
            'updater': update_sequence_overview
        }
    }
    
    if obj_type not in configs:
        print(f"Type {obj_type} not yet supported")
        return
    
    config = configs[obj_type]
    overview_dir = config['overview_dir']
    source_dir = config['source_dir']
    
    files = list(overview_dir.glob(config['pattern']))
    if limit:
        files = files[:limit]
    
    print(f"\nEnriching {obj_type}: {len(files)} files")
    
    updated = 0
    for i, overview_file in enumerate(files):
        # Extract object name
        suffix = f"-{config['pattern'].split('-')[1]}-Overview" 
        # e.g -Table-Overview. But regex replacement is safer
        obj_name = overview_file.name.split('-')[0] # Rough assumption, but mostly true for legacy objects
        # To be safer, we can use the pattern suffix removal
        
        # Better name extraction:
        suffix_map = {
            'db_table': '-Table-Overview.md',
            'db_view': '-View-Overview.md',
            'db_package': '-Package-Overview.md',
            'db_procedure': '-Procedure-Overview.md',
            'db_function': '-Function-Overview.md',
            'db_type': '-Type-Overview.md',
            'db_constraint': '-Constraint-Overview.md',
            'db_index': '-Index-Overview.md',
            'db_sequence': '-Sequence-Overview.md'
        }
        
        suff = suffix_map.get(obj_type, '')
        if overview_file.name.endswith(suff):
             obj_name = overview_file.name[:-len(suff)]
        else:
             obj_name = overview_file.stem # Fallback
        
        sql_file = source_dir / f"{obj_name}.sql"
        
        if config['updater'](overview_file, sql_file, obj_name):
            updated += 1
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(files)}...")
    
    print(f"  Done: {updated} enriched")


def main():
    parser = argparse.ArgumentParser()
    all_types = ['db_table', 'db_view', 'db_package', 'db_procedure', 
                 'db_function', 'db_type', 'db_constraint', 'db_index', 'db_sequence']
    parser.add_argument('--type', choices=all_types + ['all'], default='all')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    
    print("=" * 60)
    print("Database Object Enrichment")
    print("=" * 60)
    
    types = all_types if args.type == 'all' else [args.type]
    
    for t in types:
        process_type(t, args.limit)
    
    print("\nNext: Run enrich_links_v2.py to resolve smart links")


if __name__ == "__main__":
    main()
