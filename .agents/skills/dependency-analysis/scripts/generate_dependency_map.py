#!/usr/bin/env python3
"""
generate_dependency_map.py (CLI)
=====================================

Purpose:
    Generates a system-wide dependency map by scanning source files for direct dependencies.

Layer: Curate / Inventories

Usage Examples:
    python plugins/dependency-analysis/scripts/generate_dependency_map.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    (None detected)

Input Directories (Source Mining):
    - Forms: `legacy-system/oracle-forms/XML` & `legacy-system/oracle-forms-overviews/forms`
    - Reports: `legacy-system/oracle-forms/Reports`
    - Libraries: `legacy-system/oracle-forms/pll`
    - Database: `legacy-system/oracle-database/` (Packages, Views, Tables, etc.)

Input Files (Metadata):
    - `legacy-system/reference-data/inventories/relationship_graph.json` (Mined Form-to-Form calls)
    - `legacy-system/reference-data/master_object_collection.json` (Type Resolution)
    - `legacy-system/reference-data/master_object_collection_exclude_list.json`

Output:
    - `legacy-system/reference-data/inventories/dependency_map.json` (The system-wide direct dependency graph)

Key Functions:
    - load_json(): Helper to safely load a JSON file.
    - should_ignore(): Checks if the object name is in the exclude list or matches a pattern.
    - is_excluded_file(): Checks if the file path matches any exclusion patterns from the central list.
    - is_builtin_package(): Checks if package is a standard Oracle built-in to be ignored.
    - init_entry(): Initializes a new entry in the global map if it doesn't exist.
    - add_dep(): Adds a dependency to the specified category if unique and not excluded.
    - add_table_op(): Adds a table operation context (CRUD) to the dependency map.
    - add_def(): Adds a definition (procedure/function name) to the object's metadata.
    - scan_text_for_deps(): Scans a text block for SQL tables, Views, Package calls, and Definitions.
    - scan_forms(): Scans Oracle Forms (Markdown & XML).
    - scan_reports(): Scans Report XML files for dependencies.
    - scan_plls(): Scans PLL Text dumps for dependencies.
    - scan_db_packages(): Scans Database Package (.sql) files for dependencies.
    - scan_views(): Scans Database View (.sql) files for dependencies.
    - scan_db_procedures(): Scans Database Procedure (.sql) files for dependencies.
    - scan_db_functions(): Scans Database Function (.sql) files for dependencies.
    - scan_db_tables(): Scans Database Table (.sql) files - creates entries for Table objects.
    - scan_db_triggers(): Scans Database Trigger (.sql) files.
    - scan_db_types(): Scans Database Type (.sql) files.
    - scan_db_sequences(): Scans Database Sequence (.sql) files.
    - scan_db_indexes(): Scans Database Index (.sql) files.
    - scan_db_constraints(): Scans Database Constraint (.sql) files.
    - scan_menus(): Scans Menu Module XML files (*_mmb.xml) for dependencies.
    - scan_olbs(): Scans Object Library XML files (*_olb.xml) for dependencies.
    - load_relationship_graph(): Ingests the pre-calculated Relationship Graph JSON derived from MenuConfig `form_relationships.csv`.
    - main(): Main Orchestrator.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import os
import json
import re
import glob
import html
from typing import Dict, List, Set, Any

# Paths
CWD = os.getcwd()
REF_DATA_DIR = os.path.join(CWD, 'legacy-system', 'reference-data', 'inventories')
OUTPUT_PATH = os.path.join(REF_DATA_DIR, 'dependency_map.json')
EXCLUDE_LIST_PATH = os.path.join(CWD, 'legacy-system', 'reference-data', 'master_object_collection_exclude_list.json')

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


# Input Directories
FORMS_MD_DIR = os.path.join(CWD, 'legacy-system', 'oracle-forms-overviews', 'forms')
FORMS_XML_DIR = os.path.join(CWD, 'legacy-system', 'oracle-forms', 'XML')
REPORTS_XML_DIR = os.path.join(CWD, 'legacy-system', 'oracle-forms', 'Reports')
PLL_DIR = os.path.join(CWD, 'legacy-system', 'oracle-forms', 'pll')

# Database Directories
DB_PKG_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Packages')
DB_VIEW_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Views')
DB_PROC_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Procedures')
DB_FUNC_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Functions')
DB_TABLE_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Tables')
DB_TRIG_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Triggers')
DB_TYPE_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Types')
DB_SEQ_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Sequences')
DB_IND_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Indexes')
DB_CONST_DIR = os.path.join(CWD, 'legacy-system', 'oracle-database', 'Constraints')

# Global Dependency Map
# Structure: { "OBJECT_NAME": { "Type": "FORM", "Dependencies": { "Tables": [], ... } } }
DEPENDENCY_MAP: Dict[str, Dict[str, Any]] = {}

def load_json(path: str) -> Dict[str, Any]:
    """Helper to safely load a JSON file."""
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
             return {}
    return {}

# Load Reference Inventories for Validation
PLL_INVENTORY = load_json(os.path.join(REF_DATA_DIR, 'pll_inventory.json'))
TABLES_INVENTORY = load_json(os.path.join(REF_DATA_DIR, 'tables_inventory.json'))
VIEWS_INVENTORY = load_json(os.path.join(REF_DATA_DIR, 'views_inventory.json'))
TRIGGERS_INVENTORY = load_json(os.path.join(REF_DATA_DIR, 'triggers_inventory.json'))
TYPES_INVENTORY = load_json(os.path.join(REF_DATA_DIR, 'types_inventory.json'))
SEQUENCES_INVENTORY = load_json(os.path.join(REF_DATA_DIR, 'sequences_inventory.json'))

# Master Object Collection for Type Resolution
# Import from centralized search module
import sys
sys.path.insert(0, os.path.join(CWD, 'tools', 'investigate', 'search'))
sys.path.insert(0, os.path.join(CWD, 'tools', 'investigate', 'miners'))

try:
    from search_collection import load_collection, resolve_type
    MASTER_COLLECTION = load_collection()
except Exception:
    MASTER_COLLECTION = {}
    def resolve_type(object_id: str, collection=None) -> str:
        return 'UNKNOWN'

# Robust Form/Report Matching (Leveraging Miner Logic)
try:
    from python_regex import matchers
    from valid_form_ids import is_valid_id
    MINING_FUNCS = [
        matchers.match_call_form,
        matchers.match_open_form,
        matchers.match_new_form,
        matchers.match_run_product,
        matchers.match_execute_trigger,
        matchers.match_add_list_element,
        matchers.match_add_param,
        matchers.match_call_help_topic,
        matchers.match_call_prefix,
        matchers.match_get_menu_item_property,
        matchers.match_get_param_list,
        matchers.match_go_form_do,
        matchers.match_menubar_enable_item,
        matchers.match_menubar_hide_item,
        matchers.match_menubar_item_is_enabled,
        matchers.match_open_form_do,
        matchers.match_pr_call_form,
        matchers.match_pr_open_form,
        matchers.match_p_formmodule_name,
        matchers.match_xml_menu_module,
        matchers.match_xml_attached_lib,
        matchers.match_xml_parent_module,
        matchers.match_attr_all_ids,
        matchers.match_generic_references,
    ]
except Exception as e:
    print(f"Warning: Could not load robust form/report matchers: {e}")
    MINING_FUNCS = []
    def is_valid_id(x): return True # Fallback

# Sets for fast lookup (Optimized for O(1) checking)
KNOWN_TABLES: Set[str] = set(TABLES_INVENTORY.keys())
KNOWN_VIEWS: Set[str] = set(VIEWS_INVENTORY.keys())
KNOWN_TRIGGERS: Set[str] = set(TRIGGERS_INVENTORY.keys())
KNOWN_TYPES: Set[str] = set(TYPES_INVENTORY.keys())
KNOWN_SEQUENCES: Set[str] = set(SEQUENCES_INVENTORY.keys())
KNOWN_DB_PKGS: Set[str] = set()

# Populate known packages from file system since inventory was removed
if os.path.exists(DB_PKG_DIR):
    for f in os.listdir(DB_PKG_DIR):
        if f.lower().endswith('.sql'):
            KNOWN_DB_PKGS.add(os.path.splitext(f)[0].upper())

KNOWN_PLL_PKGS: Set[str] = set()
for p in PLL_INVENTORY.values():
    if 'packages' in p:
        KNOWN_PLL_PKGS.update(p['packages'].keys())

# Regex Patterns

def should_ignore(name: str) -> bool:
    """Checks if the object name is in the exclude list or matches a pattern."""
    name_upper = name.upper()
    name_lower = name.lower()
    
    # Check Exact Object Match
    if name_upper in EXCLUDE_CONFIG["objects"]:
        return True
        
    # Check Prefix/Pattern Match (Files list contains prefixes like 'AGLOGON', 'AGE')
    if any(name_lower.startswith(p) for p in EXCLUDE_CONFIG["files"]):
        return True
        
    return False

def is_excluded_file(filepath: str) -> bool:
    """Checks if the file path matches any exclusion patterns from the central list."""
    if not filepath:
        return False
    path_lower = filepath.lower().replace('\\', '/')
    return any(pattern in path_lower for pattern in EXCLUDE_CONFIG["files"])


def is_builtin_package(pkg_name: str) -> bool:
    """Checks if package is a standard Oracle built-in to be ignored."""
    pkg_upper = pkg_name.upper()
    pkg_lower = pkg_name.lower()
    
    # Check Exact Match
    if pkg_upper in ['DUAL', 'SQL'] or pkg_upper in EXCLUDE_CONFIG["objects"]:
        return True
        
    # Check Prefix/Pattern (Using loaded exclude list)
    if any(pkg_lower.startswith(p) for p in EXCLUDE_CONFIG["files"]):
        return True
        
    return False

# Group 1: Operation Keyword
# Group 2: Table Name
RE_TABLE_REF = re.compile(r'\b(FROM|JOIN|UPDATE|INTO|DELETE(?:\s+FROM)?)\s+([A-Z0-9_$#]+)(?:\.[A-Z0-9_$#]+)?', re.IGNORECASE)

# Capture Package Calls: PKG.PROC or PKG.FUNC
RE_PKG_CALL = re.compile(r'\b([A-Z0-9_$#]+)\.([A-Z0-9_$#]+)', re.IGNORECASE)

# Capture Definitions (Procedures/Functions)
RE_DEF = re.compile(r'\b(?:PROCEDURE|FUNCTION)\s+([A-Z0-9_$#]+)', re.IGNORECASE)


def init_entry(name: str, type_str: str, file_path: str = None) -> None:
    """
    Initializes a new entry in the global map if it doesn't exist.
    Sets up the default structure for dependencies.

    Args:
        name (str): The unique Object ID (e.g. FORM0001).
        type_str (str): The artifact type (FORM, REPORT, PLL, TABLE, etc.).
        file_path (str): The absolute path to the source file (will be stored as relative).
    """
    if name not in DEPENDENCY_MAP:
        # Check Exclusions
        if should_ignore(name) or is_excluded_file(file_path):
            return

        # Convert absolute path to relative for portability
        # Use forward slashes for cross-platform consistency
        rel_path = os.path.relpath(file_path, CWD).replace('\\', '/') if file_path else None
        
        DEPENDENCY_MAP[name] = {
            "Type": type_str,
            "FilePath": rel_path,
            "Dependencies": {
                "Tables": [],        # List of all tables (Simple Set)
                "TableCRUD": {},     # Usage Context: { "TABLE": ["SELECT", "INSERT"] }
                "Views": [],
                "Packages": [],      # DB Packages (High Level)
                "Procedures": [],    # DB Procedures
                "Functions": [],     # DB Functions
                "PLLs": [],          # Attached PLL Libraries (files)
                "Forms": [],         # Called Forms
                "Reports": [],       # Called Reports
                "Menus": [],         # Menu Modules
                "ObjectLibraries": [], # Object Libraries (OLBs)
                "Triggers": [],      # Database Triggers (ON Table)
                "Sequences": [],     # Database Sequences (NEXTVAL)
                "Types": [],         # Database Types (UDTs)
                "Indexes": [],       # Database Indexes
                "Constraints": [],   # Database Constraints
                "ExternalCalls": [], # Calls to Other Objects (Pkg.Proc)
                "InternalCalls": [], # Calls to Self (Self.Proc)
                "Inheritance": []    # Parent FMBs or OLBs
            },
            "MenuModule": None,      # The linked Menu Module
            "Definitions": []        # Embedded Procedures/Functions defined in this object
        }

def add_dep(name: str, category: str, value: str) -> None:
    """Adds a dependency to the specified category if unique and not excluded."""
    if not value or should_ignore(value):
        return
    
    # Check if the value matches a file exclusion (e.g., _200 versioned files)
    if is_excluded_file(value):
        return

    if name in DEPENDENCY_MAP and value not in DEPENDENCY_MAP[name]['Dependencies'][category]:
        DEPENDENCY_MAP[name]['Dependencies'][category].append(value)


def add_table_op(name: str, table: str, op_keyword: str) -> None:
    """
    Adds a table operation context (CRUD) to the dependency map.
    Maps SQL keywords (FROM, INTO, UPDATE) to operations (SELECT, INSERT, UPDATE).
    """
    # Map SQL keyword to simplified CRUD operation
    op = "SELECT" # Default for FROM/JOIN
    kw = op_keyword.upper()
    if "UPDATE" in kw:
        op = "UPDATE"
    elif "INTO" in kw:
        op = "INSERT" # INSERT INTO
    elif "DELETE" in kw:
        op = "DELETE"
    
    crud_map = DEPENDENCY_MAP[name]['Dependencies']['TableCRUD']
    if table not in crud_map:
        crud_map[table] = []
    if op not in crud_map[table]:
        crud_map[table].append(op)

def add_def(name: str, definition_name: str) -> None:
    """Adds a definition (procedure/function name) to the object's metadata."""
    if definition_name and definition_name not in DEPENDENCY_MAP[name]['Definitions']:
        DEPENDENCY_MAP[name]['Definitions'].append(definition_name)

def scan_text_for_deps(name: str, text: str) -> None:
    """
    Scans a text block for SQL tables, Views, Package calls, and Definitions.
    Applies logic to categorize them correctly based on known inventories.
    
    This is the core analysis function used by all file scanners.

    Args:
        name (str): The Object ID being scanned.
        text (str): The raw content of the file.
    """
    if not text:
        return

    # PRE-PROCESSING (Synced with deep miner)
    # 1. Unescape XML entities (Mandatory for trigger parsing in XML/Markdown)
    text = html.unescape(text)
    text = text.replace('&#10;', '\n').replace('&amp;', '&').replace('&#x9;', '\t')

    # 2. Strip SQL comments (Prevents false positives in commented code)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL) # Multi-line
    text = re.sub(r'--.*', '', text) # Single line
    # 1. Tables & Views with Context
    for match in RE_TABLE_REF.finditer(text):
        op_keyword = match.group(1)
        obj = match.group(2).upper()
        
        if obj in KNOWN_TABLES:
            add_dep(name, 'Tables', obj)
            add_table_op(name, obj, op_keyword)
        elif obj in KNOWN_VIEWS:
            add_dep(name, 'Views', obj)
        elif obj in KNOWN_SEQUENCES:
            add_dep(name, 'Sequences', obj)
        elif obj in KNOWN_TYPES:
            add_dep(name, 'Types', obj)
            
    # 2. Package/Library Calls (External vs Internal)
    for match in RE_PKG_CALL.finditer(text):
        pkg = match.group(1).upper()
        proc = match.group(2).upper()
        full_call = f"{pkg}.{proc}"
        
        # Check if "pkg" is actually a Sequence (Sequence.NEXTVAL)
        if pkg in KNOWN_SEQUENCES:
            add_dep(name, 'Sequences', pkg)
            continue
            
        # Skip Built-ins
        if is_builtin_package(pkg):
            continue
        
        # Check for Internal Call
        # If 'pkg' is the object's own name (e.g. FORM0001.SOME_PROC)
        if pkg == name:
             add_dep(name, 'InternalCalls', full_call)
             continue

        # External Logic Source
        is_db = pkg in KNOWN_DB_PKGS
        
        if is_db:
            add_dep(name, 'Packages', pkg)
            add_dep(name, 'ExternalCalls', full_call)
        
        # Heuristic for other external calls (PLLs)
        elif pkg in KNOWN_PLL_PKGS or pkg in DEPENDENCY_MAP: 
             add_dep(name, 'ExternalCalls', full_call)

    # 3. Definitions (Internal)
    for match in RE_DEF.finditer(text):
        defn = match.group(1).upper()
        if defn not in ['IS', 'AS', 'BEGIN', 'DECLARE']:
             add_def(name, defn)

    # 4. Form/Report/Library/Menu Calls (Robust Miner Patterns)
    for miner in MINING_FUNCS:
        try:
            # We use the same content-matching logic as the deep miner
            refs = miner(text, name)
            for ref in refs:
                target_id = ref['child'].upper()
                
                # Basic validation and self-reference check
                if not target_id or target_id == name:
                    continue
                
                # Resolve object type from Master Collection or heuristic
                obj_type = resolve_type(target_id)
                
                # Map to correct dependency category
                if obj_type == 'FORM':
                    add_dep(name, 'Forms', target_id)
                elif obj_type == 'REPORT':
                    add_dep(name, 'Reports', target_id)
                elif obj_type in ['PLL', 'LIBRARY']:
                    add_dep(name, 'PLLs', target_id)
                elif obj_type == 'MENU':
                    add_dep(name, 'Menus', target_id)
                elif obj_type == 'OBJ_LIB':
                    add_dep(name, 'ObjectLibraries', target_id)
                elif obj_type == 'DB_PACKAGE':
                    add_dep(name, 'Packages', target_id)
                    
        except Exception:
            # Silent fail for individual matchers to ensure script continues
            pass

def scan_forms() -> None:
    """
    Scans Oracle Forms (Markdown & XML).
    
    Extracts:
    - Attached Libraries (PLLs)
    - Called Forms (CALL_FORM, OPEN_FORM)
    - Called Reports (RUN_PRODUCT, RUN_REPORT_OBJECT)
    - Menu Modules
    - SQL/PLSQL Dependencies
    """
    print("Scanning Forms (Markdown)...")
    if not os.path.exists(FORMS_MD_DIR):
        print(f"Warning: Forms Markdown Dir not found at {FORMS_MD_DIR}")
        return

    # Also scan raw XML for attached libraries
    forms_xml_dir = os.path.join(CWD, 'legacy-system', 'oracle-forms', 'XML')

    for filepath in glob.glob(os.path.join(FORMS_MD_DIR, '*.md')):
        filename = os.path.basename(filepath)
        # ID is usually the first part: FORM0001-FormModule.md
        form_id = filename.split('-')[0].upper()
        
        if should_ignore(form_id):
            continue
            
        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue
            
        init_entry(form_id, 'FORM', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1a. Attached Libraries from Markdown
            # Regex captures "AttachedLibrary: NAME"
            libs = re.findall(r'AttachedLibrary\s*[:]\s*([A-Z0-9_$]+)', content, re.IGNORECASE)
            for lib in libs:
                add_dep(form_id, 'PLLs', lib.upper())
            
            # 1b. Attached Libraries from Raw XML (more reliable)
            xml_file = os.path.join(forms_xml_dir, f"{form_id.lower()}_fmb.xml")
            if os.path.exists(xml_file):
                try:
                    with open(xml_file, 'r', encoding='utf-8', errors='ignore') as xf:
                        xml_content = xf.read()
                        
                    # Match <AttachedLibrary Name="LIBNAME" ...>
                    xml_libs = re.findall(r'<AttachedLibrary\s+Name="([^"]+)"', xml_content, re.IGNORECASE)
                    for lib in xml_libs:
                        add_dep(form_id, 'PLLs', lib.upper())
                    
                    # 1c. Menu Module
                    menu_match = re.search(r'<FormModule\s+[^>]*MenuModule="([^"]+)"', xml_content, re.IGNORECASE)
                    if menu_match:
                        menu_name = menu_match.group(1).upper()
                        if not should_ignore(menu_name):
                            DEPENDENCY_MAP[form_id]['MenuModule'] = menu_name
                    
                    # 1d. Inheritance (Parent FMB / OLB)
                    # Searches for ParentModule="..." or ParentFilename="..."
                    inheritance = re.findall(r'(?:ParentModule|ParentFilename)="([^"]+)"', xml_content, re.IGNORECASE)
                    for inh in inheritance:
                        inh_name = inh.split('.')[0].upper()
                        if inh_name != form_id and inh_name not in DEPENDENCY_MAP[form_id]['Dependencies']['Inheritance']:
                            add_dep(form_id, 'Inheritance', inh_name)
                except Exception:
                    pass
                
            # 2. Called Forms (Legacy Matcher - Kept for redundancy/augmentation)
            called_forms = re.findall(r"(?:CALL_FORM|OPEN_FORM|NEW_FORM)\s*\(\s*'([A-Z0-9]+)'", content, re.IGNORECASE)
            for cf in called_forms:
                 add_dep(form_id, 'Forms', cf.upper())

            # 3. Called Reports (Legacy Matcher - Kept for redundancy/augmentation)
            reports = re.findall(r"\b(J[A-Z]{2,3}R[0-9]{4}[A-Z0-9]*)\b", content, re.IGNORECASE)
            for rep in reports:
                if rep.upper() != form_id and "J" in rep.upper(): # Simple guard
                     add_dep(form_id, 'Reports', rep.upper())

            # 4. SQl & PL/SQL (Augmented with robust Miner matchers)
            scan_text_for_deps(form_id, content)
            
        except Exception as e:
            print(f"Error reading form {filename}: {e}")

def scan_reports() -> None:
    """Scans Report XML files for dependencies."""
    print("Scanning Reports (XML)...")
    if not os.path.exists(REPORTS_XML_DIR):
        print(f"Warning: Reports XML Dir not found at {REPORTS_XML_DIR}")
        return

    for filepath in glob.glob(os.path.join(REPORTS_XML_DIR, '*.xml')):
        filename = os.path.basename(filepath)
        # ID is usually filename without extension: RPT0001.xml
        report_id = os.path.splitext(filename)[0].upper()
        
        if should_ignore(report_id):
            continue
            
        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(report_id, 'REPORT', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 1. Attached Libraries (XML attribute)
            libs = re.findall(r'attachedLibrary\s+name="([^"]+)"', content, re.IGNORECASE)
            for lib in libs:
                # Lib name: /path/to/LIBRARY -> LIBRARY
                lib_name = os.path.basename(lib).split('.')[0].upper()
                add_dep(report_id, 'PLLs', lib_name)

            # 2. SQl & PL/SQL
            scan_text_for_deps(report_id, content)

        except Exception as e:
            print(f"Error reading report {filename}: {e}")

def scan_plls() -> None:
    """Scans PLL Text dumps for dependencies."""
    print("Scanning PLLs (Text)...")
    if not os.path.exists(PLL_DIR):
        return

    for filepath in glob.glob(os.path.join(PLL_DIR, '*.txt')):
        filename = os.path.basename(filepath)
        pll_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(pll_name):
            continue
            
        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(pll_name, 'PLL', filepath)  # Aligned with master_object_collection
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            scan_text_for_deps(pll_name, content)
        except Exception as e:
            print(f"Error reading PLL {filename}: {e}")

def scan_db_packages() -> None:
    """Scans Database Package (.sql) files for dependencies."""
    print("Scanning DB Packages (SQL)...")
    if not os.path.exists(DB_PKG_DIR):
        return

    for filepath in glob.glob(os.path.join(DB_PKG_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        pkg_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(pkg_name):
            continue

        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(pkg_name, 'DB_PACKAGE', filepath)  # Aligned with master_object_collection
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            scan_text_for_deps(pkg_name, content)

            # 3. Extract Internal Members (Procedures/Functions)
            # Simple regex to find "PROCEDURE Pname" or "FUNCTION Fname"
            # We assume these are public if in the Spec (.sql usually Spec)
            members = re.findall(r'(?:PROCEDURE|FUNCTION)\s+([a-zA-Z0-9_$#]+)', content, re.IGNORECASE)
            
            for member in set(members): # Dedup
                member_name = member.upper()
                full_name = f"{pkg_name}.{member_name}"
                
                # Heuristic: Determine type based on match context? 
                # For simplicity, we default to DB_PROCEDURE unless we re-scan for FUNCTION specific keyword
                # Let's be slightly more precise
                is_func = re.search(f'FUNCTION\\s+{member}', content, re.IGNORECASE)
                m_type = 'DB_FUNCTION' if is_func else 'DB_PROCEDURE'
                
                # 3a. Create Node for Member
                init_entry(full_name, m_type, filepath)
                
                # 3b. Link Member -> Parent Package
                add_dep(full_name, 'Packages', pkg_name)
                
                # 3c. Link Parent Package -> Member
                # Use strictly typed category based on m_type
                cat = 'Functions' if m_type == 'DB_FUNCTION' else 'Procedures'
                add_dep(pkg_name, cat, full_name)
        except Exception as e:
             print(f"Error reading package {filename}: {e}")

def scan_views() -> None:
    """Scans Database View (.sql) files for dependencies."""
    print("Scanning DB Views (SQL)...")
    if not os.path.exists(DB_VIEW_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_VIEW_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        view_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(view_name):
            continue

        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(view_name, 'VIEW', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            scan_text_for_deps(view_name, content)
        except Exception as e:
             print(f"Error reading view {filename}: {e}")


def scan_db_procedures() -> None:
    """Scans Database Procedure (.sql) files for dependencies."""
    print("Scanning DB Procedures (SQL)...")
    if not os.path.exists(DB_PROC_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_PROC_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        proc_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(proc_name):
            continue
            
        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(proc_name, 'DB_PROCEDURE', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            scan_text_for_deps(proc_name, content)
            
            # Implicit Parent Package Dependency
            if '.' in proc_name:
                parent_pkg = proc_name.split('.')[0]
                add_dep(proc_name, 'Packages', parent_pkg)
        except Exception as e:
             print(f"Error reading procedure {filename}: {e}")


def scan_db_functions() -> None:
    """Scans Database Function (.sql) files for dependencies."""
    print("Scanning DB Functions (SQL)...")
    if not os.path.exists(DB_FUNC_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_FUNC_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        func_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(func_name):
            continue

        init_entry(func_name, 'DB_FUNCTION', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            scan_text_for_deps(func_name, content)
            
            # Implicit Parent Package Dependency
            if '.' in func_name:
                parent_pkg = func_name.split('.')[0]
                add_dep(func_name, 'Packages', parent_pkg)
        except Exception as e:
             print(f"Error reading function {filename}: {e}")


def scan_db_tables() -> None:
    """Scans Database Table (.sql) files - creates entries for Table objects."""
    print("Scanning DB Tables (SQL)...")
    if not os.path.exists(DB_TABLE_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_TABLE_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        table_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(table_name):
            continue

        # Tables don't have dependencies in the same way, but we add them to the map
        # so they can be looked up as targets
        init_entry(table_name, 'TABLE', filepath)



def scan_db_triggers() -> None:
    """Scans Database Trigger (.sql) files."""
    print("Scanning DB Triggers (SQL)...")
    if not os.path.exists(DB_TRIG_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_TRIG_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        trig_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(trig_name):
            continue

        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(trig_name, 'TRIGGER', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            scan_text_for_deps(trig_name, content)
            
            # Extract "ON TABLE" dependency
            table_match = re.search(r'\bON\s+([A-Z0-9_$#]+)', content, re.IGNORECASE)
            if table_match:
                table = table_match.group(1).upper()
                add_dep(trig_name, 'Tables', table)
                
        except Exception as e:
            pass # Suppress read errors to keep output clean

def scan_db_types() -> None:
    """Scans Database Type (.sql) files."""
    print("Scanning DB Types (SQL)...")
    if not os.path.exists(DB_TYPE_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_TYPE_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        type_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(type_name):
            continue

        init_entry(type_name, 'TYPE', filepath)
        # Scan body for usage of other types/tables
        try:
             with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
             scan_text_for_deps(type_name, content)
        except:
            pass

def scan_db_sequences() -> None:
    """Scans Database Sequence (.sql) files."""
    print("Scanning DB Sequences (SQL)...")
    if not os.path.exists(DB_SEQ_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_SEQ_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        seq_name = os.path.splitext(filename)[0].upper()
        
        if should_ignore(seq_name):
            continue
            
        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(seq_name, 'SEQUENCE', filepath)

def scan_db_indexes() -> None:
    """Scans Database Index (.sql) files."""
    print("Scanning DB Indexes (SQL)...")
    if not os.path.exists(DB_IND_DIR):
        return
        
    for filepath in glob.glob(os.path.join(DB_IND_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        ind_name = os.path.splitext(filename)[0].upper()
        
        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue
            
        init_entry(ind_name, 'INDEX', filepath)
        
        # Parse "ON TABLE (COL)"
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            table_match = re.search(r'\bON\s+([A-Z0-9_$#]+)', content, re.IGNORECASE)
            if table_match:
                table = table_match.group(1).upper()
                add_dep(ind_name, 'Tables', table)
        except:
            pass

def scan_db_constraints() -> None:
    """Scans Database Constraint (.sql) files."""
    print("Scanning DB Constraints (SQL)...")
    if not os.path.exists(DB_CONST_DIR):
        return
    for filepath in glob.glob(os.path.join(DB_CONST_DIR, '*.sql')):
        filename = os.path.basename(filepath)
        const_name = os.path.splitext(filename)[0].upper()
        
        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue
            
        init_entry(const_name, 'CONSTRAINT', filepath)

def scan_menus() -> None:
    """Scans Menu Module XML files (*_mmb.xml) for dependencies."""
    print("Scanning Menus (XML)...")
    if not os.path.exists(FORMS_XML_DIR):
        print(f"Warning: Forms XML Directory not found at {FORMS_XML_DIR}")
        return

    # Use case-insensitive glob for Windows reliability
    files = [f for f in os.listdir(FORMS_XML_DIR) if f.lower().endswith('_mmb.xml')]
    print(f"   Found {len(files)} MMB files.")
    
    for filename in files:
        filepath = os.path.join(FORMS_XML_DIR, filename)
        # ID is usually filename without extension/suffix: EXAMPLE_LIB_mmb.xml -> EXAMPLE_LIB
        menu_id = filename.lower().replace('_mmb.xml', '').upper()
        
        if should_ignore(menu_id):
            continue

        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(menu_id, 'MENU', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 1. Attached Libraries (XML attribute)
            libs = re.findall(r'<AttachedLibrary\s+Name="([^"]+)"', content, re.IGNORECASE)
            for lib in libs:
                add_dep(menu_id, 'PLLs', lib.upper())
            
            # 2. SQL & PL/SQL
            scan_text_for_deps(menu_id, content)

        except Exception as e:
            print(f"Error reading menu {filename}: {e}")

def scan_olbs() -> None:
    """Scans Object Library XML files (*_olb.xml) for dependencies."""
    print("Scanning Object Libraries (XML)...")
    if not os.path.exists(FORMS_XML_DIR):
        return

    files = [f for f in os.listdir(FORMS_XML_DIR) if f.lower().endswith('_olb.xml')]
    print(f"   Found {len(files)} OLB files.")

    for filename in files:
        filepath = os.path.join(FORMS_XML_DIR, filename)
        olb_id = filename.lower().replace('_olb.xml', '').upper()
        
        if should_ignore(olb_id):
            continue

        # Check explicit file exclusion
        if is_excluded_file(filepath):
            continue

        init_entry(olb_id, 'OLB', filepath)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 1. Attached Libraries
            libs = re.findall(r'<AttachedLibrary\s+Name="([^"]+)"', content, re.IGNORECASE)
            for lib in libs:
                add_dep(olb_id, 'PLLs', lib.upper())
                
            # 2. Logic Scanner
            scan_text_for_deps(olb_id, content)
            
        except Exception as e:
            print(f"Error reading OLB {filename}: {e}")

RELATIONSHIP_GRAPH = os.path.join(REF_DATA_DIR, 'relationship_graph.json')

def load_relationship_graph() -> None:
    """
    Ingests the pre-calculated Relationship Graph JSON derived from `Automatic-combined-Relationships.csv`.
    This serves as a secondary source of truth, merging Manual Analysis, Code Mining, and Reports.

    Path: legacy-system/reference-data/inventories/relationship_graph.json
    """
    print(f"Scanning Combined Relationships (JSON)... {RELATIONSHIP_GRAPH}")
    if not os.path.exists(RELATIONSHIP_GRAPH):
        print(f"Warning: Relationship Graph JSON not found at {RELATIONSHIP_GRAPH}")
        return

    try:
        data = load_json(RELATIONSHIP_GRAPH)
        count = 0
        for entry in data:
            src = entry.get('Source', '').upper()
            tgt = entry.get('Target', '').upper()
            target_type = entry.get('TargetType', 'UNKNOWN')
            
            if not src or not tgt: continue

            # Initialize Source if missing
            if src not in DEPENDENCY_MAP:
                init_entry(src, entry.get('SourceType', 'FORM'))
            
            # Map based on target type
            category = 'Forms'
            if target_type == 'REPORT':
                category = 'Reports'
            elif target_type == 'PLL': # If identified as library
                 category = 'PLLs'
            
            add_dep(src, category, tgt)
            count += 1
            
        print(f"Ingested {count} relationships from JSON Graph.")
    except Exception as e:
        print(f"Error loading Relationship Graph: {e}")

def main() -> None:
    """
    Main Orchestrator.
    Executes scans in order and writes the final JSON to disk.
    """
    print("Generating Dependency Map (System-Wide)...")
    print("Note: This script finds DIRECT dependencies only (1 level deep).")
    
    # 1. Presentation Layer
    scan_forms()
    scan_reports()
    scan_menus()
    scan_olbs()
    
    # 2. Key Enhancement: Ingest Deep Analysis JSON
    load_relationship_graph()
    
    # 3. Logic Layer
    scan_plls()
    
    # 4. Data Layer - Full Coverage
    scan_db_packages()
    scan_db_procedures()
    scan_db_functions()
    scan_views()
    scan_db_tables()
    scan_db_triggers()
    scan_db_types()
    scan_db_sequences()
    scan_db_indexes()
    scan_db_constraints()
    
    # Filter out UNKNOWN types (external/orphaned references)
    filtered_map = {k: v for k, v in DEPENDENCY_MAP.items() if v.get('Type') != 'UNKNOWN'}

    
    # Sort keys for consistent output
    sorted_map = dict(sorted(filtered_map.items()))
    
    # Write Output to Reference Data
    os.makedirs(REF_DATA_DIR, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(sorted_map, f, indent=2)
        
    print(f"Dependency Map generated at {OUTPUT_PATH}")
    print(f"Total Objects Mapped: {len(sorted_map)}")
    
    # Verification Stats
    type_counts: Dict[str, int] = {}
    total_deps = 0
    dep_category_counts: Dict[str, int] = {}
    
    for obj in sorted_map.values():
        t = obj['Type']
        type_counts[t] = type_counts.get(t, 0) + 1
        
        # Count dependencies
        deps = obj.get('Dependencies', {})
        for category, items in deps.items():
            if isinstance(items, list):
                count = len(items)
                total_deps += count
                dep_category_counts[category] = dep_category_counts.get(category, 0) + count
            elif isinstance(items, dict):  # TableCRUD
                count = len(items)
                total_deps += count
                dep_category_counts[category] = dep_category_counts.get(category, 0) + count
    
    print("Mapped Objects by Type:", type_counts)
    print(f"Total Dependencies Mapped: {total_deps}")
    print("Dependencies by Category:", {k: v for k, v in sorted(dep_category_counts.items()) if v > 0})

if __name__ == "__main__":
    main()
