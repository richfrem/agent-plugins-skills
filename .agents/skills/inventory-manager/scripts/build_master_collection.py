#!/usr/bin/env python3
"""
build_master_collection.py (CLI)
=====================================

Purpose:
    Aggregates all individual inventories into a single master_object_collection.json.

Layer: Curate / Inventories

Usage Examples:
    python plugins/inventory-manager/scripts/build_master_collection.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --full          : Populate all objects (default: header only)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - load_json(): Load JSON file if exists.
    - resolve_artifact_path(): Resolve actual artifact path, checking if file exists.
    - add_object(): Adds object to collection, handling ID collisions and Exclusions.
    - populate_forms(): Populate FORM objects from oracle_forms_manifest.json.
    - populate_reports(): Populate REPORT objects.
    - populate_plls(): Populate PLL objects.
    - populate_packages(): Populate DB_PACKAGE objects.
    - populate_tables(): Populate TABLE objects.
    - populate_views(): Populate VIEW objects.
    - populate_db_functions(): Populate DB_FUNCTION objects.
    - populate_db_procedures(): Populate DB_PROCEDURE objects.
    - populate_db_types(): Populate DB_TYPE objects.
    - populate_constraints(): Populate CONSTRAINT objects.
    - populate_indexes(): Populate INDEX objects.
    - populate_sequences(): Populate SEQUENCE objects.
    - populate_triggers(): Populate DB_TRIGGER objects.
    - populate_menus(): Populate MENU objects.
    - populate_olbs(): Populate OBJ_LIB objects.
    - populate_roles(): Populate ROLE objects.
    - populate_applications(): Populate APPLICATION objects.
    - populate_workflows(): Populate WORKFLOW objects.
    - populate_business_rules(): Populate BUSINESS_RULE objects.
    - build_full_collection(): Build the complete master collection with all objects.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import sys
import json
import argparse
from datetime import datetime, timezone

# Ensure UTF-8 output on Windows (avoids charmap errors from emoji in print statements)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Paths
CWD = os.getcwd()
REFERENCE_DATA_DIR = os.path.join(CWD, 'legacy-system', 'reference-data')
INVENTORIES_DIR = os.path.join(REFERENCE_DATA_DIR, 'inventories')
OUTPUT_PATH = os.path.join(REFERENCE_DATA_DIR, 'master_object_collection.json')
EXCLUDE_LIST_PATH = os.path.join(REFERENCE_DATA_DIR, 'master_object_collection_exclude_list.json')

# Load Exclude List
EXCLUDE_CONFIG = {"objects": [], "files": []}
if os.path.exists(EXCLUDE_LIST_PATH):
    try:
        with open(EXCLUDE_LIST_PATH, 'r', encoding='utf-8') as f:
            exclude_data = json.load(f)
            EXCLUDE_CONFIG["objects"] = [x.upper() for x in exclude_data.get("objects", [])]
            EXCLUDE_CONFIG["files"] = [x.lower() for x in exclude_data.get("files", [])]
    except Exception as e:
        print(f"⚠️ Error loading exclude list: {e}")


# Source inventory paths
INVENTORIES = {
    "forms_inventory.json": "FORM",
    "reports_inventory.json": "REPORT",
    "pll_inventory.json": "PLL",
    "tables_inventory.json": "TABLE",
    "views_inventory.json": "VIEW",
    "functions_inventory.json": "DB_FUNCTION",
    "procedures_inventory.json": "DB_PROCEDURE",
    "types_inventory.json": "DB_TYPE",
    "triggers_inventory.json": "DB_TRIGGER",
    "constraints_inventory.json": "CONSTRAINT",
    "indexes_inventory.json": "INDEX",
    "sequences_inventory.json": "SEQUENCE",
    "menu_inventory.json": "MENU",
    "olb_inventory.json": "OBJ_LIB",
    "roles_inventory.json": "ROLE",
    "applications_inventory.json": "APPLICATION",
    "business_workflows_inventory.json": "WORKFLOW",
    "business_rules_inventory.json": "BUSINESS_RULE"
}

# ... (OBJECT_TYPES definition skipped - assumed correct from previous step) ...



# Define the Object Types Schema
OBJECT_TYPES = {
    "FORM": {
        "description": "Oracle Forms (.fmb) - UI screens for data entry and navigation",
        "sourceCollection": "forms_inventory.json",
        "availableArtifacts": ["overview", "xml-md", "xml"],
        "pathTemplates": {
            "overview": "legacy-system/oracle-forms-overviews/forms/{ID}-Overview.md",
            "xml-md": "legacy-system/oracle-forms-markdown/XML/{id}-FormModule.md",
            "xml": "legacy-system/oracle-forms/XML/{id}_fmb.xml"
        },
        "linkFormat": "[{ID}]({overview_path})",
        "idPattern": r"^[A-Z]{3,4}[EMS]\d{4}[a-z]?$",
        "examples": ["JCSE0030", "RCCE0020", "JASM0000"]
    },
    "REPORT": {
        "description": "Oracle Reports (.rdf) - Printable documents and data exports",
        "sourceCollection": "reports_inventory.json",
        "availableArtifacts": ["overview", "xml"],
        "pathTemplates": {
            "overview": "legacy-system/oracle-forms-overviews/reports/{ID}-Report-Overview.md",
            "xml": "legacy-system/oracle-forms/Reports/{id}.xml"
        },
        "linkFormat": "[{ID}]({overview_path})",
        "idPattern": r"^[A-Z]{3,4}R\d{4}[a-z]?$",
        "examples": ["JRSR0101", "RCCR0050"]
    },
    "PLL": {
        "description": "Oracle Forms Library (.pll) - Shared PL/SQL code libraries",
        "sourceCollection": "pll_inventory.json",
        "availableArtifacts": ["overview", "source", "markdown"],
        "pathTemplates": {
            "overview": "legacy-system/oracle-forms-overviews/libraries/{ID}-Library-Overview.md",
            "source": "legacy-system/oracle-forms/pll/{id}.txt",
            "markdown": "legacy-system/oracle-forms-markdown/pll/{id}.md"
        },
        "linkFormat": "[{ID}]({overview_path})",
        "idPattern": r"^[A-Z]{3,}LIB$|^AGLIB$|^WEBUTIL$|^D2KWUTIL$",
        "examples": ["JUSLIB", "AGLIB", "JCSLIB", "WEBUTIL"]
    },
    "TABLE": {
        "description": "Oracle Database Table - Persistent data storage",
        "sourceCollection": "tables_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/tables/{ID}-Table-Overview.md",
            "sql": "legacy-system/oracle-database/Tables/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["DCFL_COURT_FILES", "PART_PARTICIPANTS"]
    },
    "VIEW": {
        "description": "Oracle Database View - Virtual table derived from queries",
        "sourceCollection": "views_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/views/{ID}-View-Overview.md",
            "sql": "legacy-system/oracle-database/Views/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+_V$|^V_[A-Z_]+$",
        "examples": ["DCFL_COURT_FILES_V", "V_RCC_SUBMISSIONS"]
    },
    "DB_FUNCTION": {
        "description": "Oracle Database Function - Stored PL/SQL function",
        "sourceCollection": "functions_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/functions/{ID}-Function-Overview.md",
            "sql": "legacy-system/oracle-database/Functions/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["GET_DATE", "CALC_STATUS"]
    },
    "DB_PROCEDURE": {
        "description": "Oracle Database Procedure - Stored PL/SQL procedure",
        "sourceCollection": "procedures_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/procedures/{ID}-Procedure-Overview.md",
            "sql": "legacy-system/oracle-database/Procedures/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["UPDATE_STATUS", "PROCESS_DATA"]
    },
    "DB_TYPE": {
        "description": "Oracle Database Type - Custom data type",
        "sourceCollection": "types_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/types/{ID}-Type-Overview.md",
            "sql": "legacy-system/oracle-database/Types/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["T_ADDRESS_OBJ"]
    },
    "DB_PACKAGE": {
        "description": "Oracle Database Package - Stored PL/SQL package (Spec & Body)",
        "sourceCollection": "packages_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/packages/{ID}-Package-Overview.md",
            "sql": "legacy-system/oracle-database/Packages/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["JUSTIN_DEMS_INTERFACE", "PKG_TOOLS"]
    },
    "CONSTRAINT": {
        "description": "Oracle Database Constraint - Data integrity rule",
        "sourceCollection": "constraints_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/constraints/{ID}-Constraint-Overview.md",
            "sql": "legacy-system/oracle-database/Constraints/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["PK_USERS"]
    },
    "INDEX": {
        "description": "Oracle Database Index - Performance structure",
        "sourceCollection": "indexes_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/indexes/{ID}-Index-Overview.md",
            "sql": "legacy-system/oracle-database/Indexes/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["IDX_USERS_NAME"]
    },
    "SEQUENCE": {
        "description": "Oracle Database Sequence - Number generator",
        "sourceCollection": "sequences_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/sequences/{ID}-Sequence-Overview.md",
            "sql": "legacy-system/oracle-database/Sequences/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^[A-Z_]+$",
        "examples": ["SEQ_PART_ID"]
    },
    "DB_TRIGGER": {
        "description": "Oracle Database Trigger - Automated event-driven PL/SQL code",
        "sourceCollection": "triggers_inventory.json",
        "availableArtifacts": ["overview", "sql"],
        "pathTemplates": {
            "overview": "legacy-system/database-overviews/triggers/{ID}-Trigger-Overview.md",
            "sql": "legacy-system/oracle-database/Triggers/{file}"
        },
        "linkFormat": "[{ID}]({sql_path})",
        "idPattern": r"^JUSTIN_[A-Z_]+$",
        "examples": ["JUSTIN_PROF_R_A_IU", "JUSTIN_RCC_R_B_IU"]
    },
    "MENU": {
        "description": "Oracle Forms Menu (.mmb) - Application menu structure",
        "sourceCollection": "menus_inventory.json",
        "availableArtifacts": ["overview", "xml"],
        "pathTemplates": {
            "overview": "legacy-system/oracle-forms-overviews/menus/{ID}-Menu-Overview.md",
            "xml": "legacy-system/oracle-forms/XML/{file}"
        },
        "linkFormat": "[{ID}]({xml_path})",
        "idPattern": r"^[A-Z0-9_]+$",
        "examples": ["JASM_MENU"]
    },
    "OBJ_LIB": {
        "description": "Oracle Forms Object Library (.olb) - Reusable UI components",
        "sourceCollection": "olb_inventory.json",
        "availableArtifacts": ["xml"],
        "pathTemplates": {
            "xml": "legacy-system/oracle-forms/XML/{file}"
        },
        "linkFormat": "[{ID}]({xml_path})",
        "idPattern": r"^[A-Z0-9_]+$",
        "examples": ["AGOBJECTS"]
    },
    "ROLE": {
        "description": "JUSTIN Security Role - Access control identity",
        "sourceCollection": "roles_inventory.json",
        "availableArtifacts": ["definition"],
        "pathTemplates": {
            "definition": "legacy-system/justin-roles/{ID}.md"
        },
        "linkFormat": "[{ID}]({definition_path})",
        "idPattern": r"^(JAS|JCS|JRS|RCC|LEA|JUS|OCJ|POS)_[A-Z0-9_]+$",
        "examples": ["JCS_COURTS_CLERK", "RCC_ADMIN_LOCAL", "JAS_ADMIN"]
    },
    "APPLICATION": {
        "description": "JUSTIN Application - Top-level system module (RCC, JCS, JRS, JAS, LEA)",
        "sourceCollection": "applications_inventory.json",
        "availableArtifacts": ["overview"],
        "pathTemplates": {
            "overview": "legacy-system/applications/{ID}-Application-Overview.md"
        },
        "linkFormat": "[{ID}]({overview_path})",
        "idPattern": r"^(RCC|JCS|JRS|JAS|LEA)$",
        "examples": ["RCC", "JCS", "JRS", "JAS", "LEA"]
    },
    "WORKFLOW": {
        "description": "Business Workflow - Cross-form process documentation",
        "sourceCollection": "business_workflows_inventory.json",
        "availableArtifacts": ["overview"],
        "pathTemplates": {
            "overview": "legacy-system/business-workflows/{file}"
        },
        "linkFormat": "[{ID}]({overview_path})",
        "idPattern": r"^BW-\d{4}$",
        "examples": ["BW-0001", "BW-0002"]
    },
    "BUSINESS_RULE": {
        "description": "Business Rule - Documented business logic constraint",
        "sourceCollection": "business_rules_inventory.json",
        "availableArtifacts": ["overview"],
        "pathTemplates": {
            "overview": "legacy-system/business-rules/{file}"
        },
        "linkFormat": "[{ID}]({overview_path})",
        "idPattern": r"^BR-\d{4}$",
        "examples": ["BR-0001", "BR-0006"]
    }
}


def load_json(path):
    """Load JSON file if exists."""
    if not os.path.exists(path):
        print(f"  Warning: {path} not found")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def resolve_artifact_path(obj_id, obj_type, artifact_type, file_hint=None):
    """Resolve actual artifact path, checking if file exists."""
    type_info = OBJECT_TYPES.get(obj_type, {})
    templates = type_info.get('pathTemplates', {})
    template = templates.get(artifact_type)
    
    if not template:
        return None
    
    # Replace placeholders
    path = template.replace('{ID}', obj_id.upper())
    path = path.replace('{id}', obj_id.lower())
    if file_hint:
        path = path.replace('{file}', file_hint)
    
    # Check if file exists
    full_path = os.path.join(CWD, path)
    if os.path.exists(full_path):
        return path
    return None


def add_object(objects, obj_id, obj_data):
    """Adds object to collection, handling ID collisions and Exclusions."""
    
    # Check Exclude List (Objects)
    if obj_id.upper() in EXCLUDE_CONFIG["objects"]:
        # print(f"    🚫 Excluding Object: {obj_id}")
        return

    # Check Exclude List (Files)
    # Check if any artifact path matches an exclude file pattern
    for artifact_type, path in obj_data.get("artifacts", {}).items():
        path_lower = path.lower()
        if any(pattern in path_lower for pattern in EXCLUDE_CONFIG["files"]):
            # print(f"    🚫 Excluding File Match: {path}")
            return

    if obj_id not in objects:
        objects[obj_id] = obj_data
        return

    # Handle Collision
    existing = objects[obj_id]
    existing_type = existing['type']
    new_type = obj_data['type']
    
    if existing_type == new_type:
        # Same type update? Warning but overwrite
        print(f"    Warning: Overwriting duplicate {existing_type} {obj_id}")
        objects[obj_id] = obj_data
        return

    # Logic: Favor FORM over PLL (Code Libraries named after Forms)
    if existing_type == 'FORM' and new_type == 'PLL':
        # Create the PLL with specific suffix to preserve it
        pll_id = f"{obj_id}_PLL"
        objects[pll_id] = obj_data
        # Do not overwrite the main ID (Keep as FORM)
        return
        
    # Logic: PLL vs MENU (Ambiguous Name)
    # Generic logic handles creation of _PLL and _MENU suffixes.
    # Just suppress warning as this is expected for Libraries that share names with Menus.
    if (existing_type == 'PLL' and new_type == 'MENU') or \
       (existing_type == 'MENU' and new_type == 'PLL'):
        existing_new_id = f"{obj_id}_{existing_type}"
        new_id = f"{obj_id}_{new_type}"
        
        objects[existing_new_id] = existing
        objects[new_id] = obj_data
        
        # Keep the MENU as the primary ID (arbitrary choice, but follows Last Writer Wins)
        objects[obj_id] = obj_data
        return

    print(f"    ⚠️ ID Collision for {obj_id}: Existing {existing_type} vs New {new_type}")
    
    # Generic Collision Handling: Create suffixed aliases for BOTH
    existing_new_id = f"{obj_id}_{existing_type}"
    if existing_new_id not in objects:
        objects[existing_new_id] = existing
    
    new_id = f"{obj_id}_{new_type}"
    objects[new_id] = obj_data

    # Overwrite original ID with new object (Last Writer Wins logic for the ambiguous key)
    objects[obj_id] = obj_data

def populate_forms(objects):
    """Populate FORM objects from forms_inventory.json."""
    manifest_path = os.path.join(INVENTORIES_DIR, 'forms_inventory.json')
    try:
        data = load_json(manifest_path)
        
        count = 0
        for item in data if isinstance(data, list) else data.values():
            try:
                obj_id = item.get('ObjectID', item.get('id', '')).upper()
                if not obj_id:
                    continue
                
                artifacts = {}
                for artifact in ['overview', 'xml-md', 'xml']:
                    path = resolve_artifact_path(obj_id, 'FORM', artifact)
                    if path:
                        artifacts[artifact] = path
                
                obj_data = {
                    "type": "FORM",
                    "name": item.get('ObjectName', item.get('title', obj_id)),
                    "artifacts": artifacts
                }
                add_object(objects, obj_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing form item {item.get('ObjectID', '?')}: {e}")
        
        print(f"  FORM: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading forms inventory: {e}")
        return 0


def populate_reports(objects):
    """Populate REPORT objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'reports_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for obj_id, item in data.items():
            try:
                artifacts = {}
                for artifact in ['overview', 'xml']:
                    path = resolve_artifact_path(obj_id, 'REPORT', artifact)
                    if path:
                        artifacts[artifact] = path
                
                obj_data = {
                    "type": "REPORT",
                    "name": item.get('name', obj_id),
                    "artifacts": artifacts
                }
                add_object(objects, obj_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing report {obj_id}: {e}")
        
        print(f"  REPORT: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading reports inventory: {e}")
        return 0


def populate_plls(objects):
    """Populate PLL objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'pll_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for pll_name, item in data.items():
            try:
                obj_id = pll_name.upper()
                artifacts = {}
                
                # Check for source file
                for ext in ['.txt', '.pll', '.pld']:
                    source_path = resolve_artifact_path(obj_id, 'PLL', 'source')
                    if source_path:
                        artifacts['source'] = source_path
                        break
                
                # Check for Markdown file
                markdown_path = resolve_artifact_path(obj_id, 'PLL', 'markdown')
                if markdown_path:
                    artifacts['markdown'] = markdown_path

                obj_data = {
                    "type": "PLL",
                    "name": pll_name,
                    "status": item.get('status', 'Active'),
                    "notes": item.get('notes'),
                    "artifacts": artifacts,
                    "packages": list(item.get('packages', {}).keys()) if 'packages' in item else []
                }
                add_object(objects, obj_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing PLL {pll_name}: {e}")
        
        print(f"  PLL: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading PLL inventory: {e}")
        return 0

def populate_packages(objects):
    """Populate DB_PACKAGE objects."""
    return _populate_generic_db_object(objects, 'packages_inventory.json', 'DB_PACKAGE')


def populate_tables(objects):
    """Populate TABLE objects."""
    return _populate_generic_db_object(objects, 'tables_inventory.json', 'TABLE')

def populate_views(objects):
    """Populate VIEW objects."""
    return _populate_generic_db_object(objects, 'views_inventory.json', 'VIEW')

def populate_db_functions(objects):
    """Populate DB_FUNCTION objects."""
    return _populate_generic_db_object(objects, 'functions_inventory.json', 'DB_FUNCTION')

def populate_db_procedures(objects):
    """Populate DB_PROCEDURE objects."""
    return _populate_generic_db_object(objects, 'procedures_inventory.json', 'DB_PROCEDURE')

def populate_db_types(objects):
    """Populate DB_TYPE objects."""
    return _populate_generic_db_object(objects, 'types_inventory.json', 'DB_TYPE')

def populate_constraints(objects):
    """Populate CONSTRAINT objects."""
    return _populate_generic_db_object(objects, 'constraints_inventory.json', 'CONSTRAINT')

def populate_indexes(objects):
    """Populate INDEX objects."""
    return _populate_generic_db_object(objects, 'indexes_inventory.json', 'INDEX')

def populate_sequences(objects):
    """Populate SEQUENCE objects."""
    return _populate_generic_db_object(objects, 'sequences_inventory.json', 'SEQUENCE')

def populate_triggers(objects):
    """Populate DB_TRIGGER objects."""
    return _populate_generic_db_object(objects, 'triggers_inventory.json', 'DB_TRIGGER')

def _populate_generic_db_object(objects, filename, obj_type):
    """Helper for generic DB object population."""
    try:
        inv_path = os.path.join(INVENTORIES_DIR, filename)
        data = load_json(inv_path)
        
        count = 0
        if data:
            for name, file_name in data.items():
                try:
                    obj_id = name.upper()
                    artifacts = {}
                    
                    # Resolve SQL path using template
                    if file_name:
                         path = resolve_artifact_path(obj_id, obj_type, 'sql', file_hint=file_name)
                         if path:
                             artifacts['sql'] = path
                    
                    # Check for Markdown file
                    markdown_path = resolve_artifact_path(obj_id, obj_type, 'markdown')
                    if markdown_path:
                        artifacts['markdown'] = markdown_path
                        
                    obj_data = {
                        "type": obj_type,
                        "name": name,
                        "artifacts": artifacts
                    }
                    add_object(objects, obj_id, obj_data)
                    count += 1
                except Exception as e:
                    print(f"    Error processing {obj_type} {name}: {e}")
        
        print(f"  {obj_type}: {count} objects")
        return count
    except Exception as e:
        print(f"  Error processing {filename}: {e}")
        return 0

def populate_menus(objects):
    """Populate MENU objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'menus_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for name, item in data.items():
            try:
                obj_id = name.upper()
                artifacts = {}
                
                # Resolve path
                if 'file' in item:
                    path = resolve_artifact_path(obj_id, 'MENU', 'xml', file_hint=item['file'])
                    if path:
                        artifacts['xml'] = path
                
                # Check for Overview
                overview_path = resolve_artifact_path(obj_id, 'MENU', 'overview')
                if overview_path:
                    artifacts['overview'] = overview_path

                obj_data = {
                    "type": "MENU",
                    "name": name,
                    "artifacts": artifacts
                }
                add_object(objects, obj_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing menu {name}: {e}")
        print(f"  MENU: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading menus inventory: {e}")
        return 0

def populate_olbs(objects):
    """Populate OBJ_LIB objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'olb_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for name, item in data.items():
            try:
                obj_id = name.upper()
                artifacts = {}
                
                # Resolve path
                if 'file' in item:
                    path = resolve_artifact_path(obj_id, 'OBJ_LIB', 'xml', file_hint=item['file'])
                    if path:
                        artifacts['xml'] = path
                    
                obj_data = {
                    "type": "OBJ_LIB",
                    "name": name,
                    "artifacts": artifacts
                }
                add_object(objects, obj_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing OLB {name}: {e}")
        print(f"  OBJ_LIB: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading OLB inventory: {e}")
        return 0

def populate_roles(objects):
    """Populate ROLE objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'roles_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for role_name, item in data.items():
            try:
                obj_id = role_name.upper()
                artifacts = {}
                
                # Resolve Definition Path (Standardized)
                path = resolve_artifact_path(obj_id, 'ROLE', 'definition')
                if path:
                    artifacts['definition'] = path
                
                obj_data = {
                    "type": "ROLE",
                    "name": role_name,
                    "status": item.get('status', 'Active'),
                    "artifacts": artifacts
                }
                add_object(objects, obj_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing role {role_name}: {e}")
        
        print(f"  ROLE: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading roles inventory: {e}")
        return 0


def populate_applications(objects):
    """Populate APPLICATION objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'applications_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for app_id, item in data.items():
            try:
                artifacts = {}
                
                # Resolve Overview Path (Standardized)
                path = resolve_artifact_path(app_id, 'APPLICATION', 'overview')
                if path:
                    artifacts['overview'] = path
                
                obj_data = {
                    "type": "APPLICATION",
                    "name": item.get('name', app_id),
                    "mainMenu": item.get('mainMenu'),
                    "artifacts": artifacts
                }
                add_object(objects, app_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing application {app_id}: {e}")
        
        print(f"  APPLICATION: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading applications inventory: {e}")
        return 0


def populate_workflows(objects):
    """Populate WORKFLOW objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'business_workflows_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for wf_id, item in data.items():
            try:
                artifacts = {}
                
                # Extract filename from overviewPath if present
                file_hint = None
                if 'overviewPath' in item:
                    file_hint = os.path.basename(item['overviewPath'])
                elif 'file' in item:
                     file_hint = item['file']
                    
                if file_hint:
                     path = resolve_artifact_path(wf_id, 'WORKFLOW', 'overview', file_hint=file_hint)
                     if path:
                         artifacts['overview'] = path
                
                obj_data = {
                    "type": "WORKFLOW",
                    "name": item.get('title', wf_id),
                    "status": item.get('status', 'Active'),
                    "artifacts": artifacts
                }
                add_object(objects, wf_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing workflow {wf_id}: {e}")
        
        print(f"  WORKFLOW: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading workflows inventory: {e}")
        return 0


def populate_business_rules(objects):
    """Populate BUSINESS_RULE objects."""
    inv_path = os.path.join(INVENTORIES_DIR, 'business_rules_inventory.json')
    try:
        data = load_json(inv_path)
        
        count = 0
        for br_id, item in data.items():
            try:
                artifacts = {}
                
                # Extract filename from overviewPath
                file_hint = None
                if 'overviewPath' in item:
                    file_hint = os.path.basename(item['overviewPath'])
                elif 'file' in item:
                     file_hint = item['file']

                if file_hint:
                     path = resolve_artifact_path(br_id, 'BUSINESS_RULE', 'overview', file_hint=file_hint)
                     if path:
                         artifacts['overview'] = path
                
                obj_data = {
                    "type": "BUSINESS_RULE",
                    "name": item.get('title', br_id),
                    "category": item.get('category'),
                    "status": item.get('status', 'Active'),
                    "artifacts": artifacts
                }
                add_object(objects, br_id, obj_data)
                count += 1
            except Exception as e:
                print(f"    Error processing Business Rule {br_id}: {e}")
        
        print(f"  BUSINESS_RULE: {count} objects")
        return count
    except Exception as e:
        print(f"  Error loading Business Rules inventory: {e}")
        return 0


def build_full_collection():
    """Build the complete master collection with all objects."""
    objects = {}
    
    print("Populating objects from inventories...")
    
    #====================================
    #oracle forms objects
    #====================================
    populate_forms(objects) # verified
    populate_reports(objects) # verified
    populate_plls(objects) # verified
    populate_menus(objects)   
    populate_olbs(objects)    
    
    #====================================
    #oracle database objects
    #====================================
    populate_packages(objects) # verified
    populate_tables(objects) # verified
    populate_views(objects)
    populate_db_functions(objects)
    populate_db_procedures(objects)
    populate_db_types(objects)
    populate_constraints(objects)
    populate_indexes(objects)
    populate_sequences(objects)
    populate_triggers(objects)
    
    #====================================
    #Application role objects
    #====================================
    populate_roles(objects)
    
    #====================================
    # Business analysis objects
    #====================================
    populate_applications(objects)
    populate_workflows(objects)
    populate_business_rules(objects)
    
    master_collection = {
        "_metadata": {
            "description": "Master Object Collection - Unified index of all JUSTIN artifacts",
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "generatedBy": "build_master_collection.py",
            "version": "1.0.0",
            "totalObjects": len(objects)
        },
        "objectTypes": OBJECT_TYPES,
        "objects": dict(sorted(objects.items()))
    }
    
    return master_collection


def main():
    parser = argparse.ArgumentParser(description='Build Master Object Collection')
    parser.add_argument('--full', action='store_true', help='Populate all objects (default: header only)')
    args = parser.parse_args()
    
    if args.full:
        print("Building Master Object Collection (Full)...")
        collection = build_full_collection()
    else:
        print("Building Master Object Collection (Header Only)...")
        collection = {
            "_metadata": {
                "description": "Master Object Collection - Unified index of all JUSTIN artifacts",
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "generatedBy": "build_master_collection.py",
                "version": "1.0.0"
            },
            "objectTypes": OBJECT_TYPES,
            "objects": {}
        }
    
    # Write output
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(collection, f, indent=2)
    
    print(f"\nObject Types: {len(OBJECT_TYPES)}")
    if args.full:
        print(f"Total Objects: {collection['_metadata']['totalObjects']}")
    
    print(f"Master Collection written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
