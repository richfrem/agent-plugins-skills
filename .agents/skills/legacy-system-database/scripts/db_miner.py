#!/usr/bin/env python3
"""
db_miner.py (CLI)
=====================================

Purpose:
    Extracts Constraints, Security, Validations from DB SQL.

Layer: Curate / Miners

Usage Examples:
    python plugins/legacy-system-database/scripts/db_miner.py --help
    python plugins/legacy-system-database/scripts/db_miner.py --target JUSTIN_ACCESS_LOGS   # Analyze Table
    python plugins/legacy-system-database/scripts/db_miner.py --search "CHECK_ROLE" --json
    python plugins/legacy-system-database/scripts/db_miner.py --target JCS_UTILS            # Analyze Package
    python plugins/legacy-system-database/scripts/db_miner.py --target MY_VIEW_V            # Analyze View
    python plugins/legacy-system-database/scripts/db_miner.py --target MY_PROC              # Analyze Standalone Procedure
    python plugins/legacy-system-database/scripts/db_miner.py --target "path/to/proc.sql"   # Analyze file path

Supported Object Types:
    - Generic

CLI Arguments:
    --target        : Specific DB object ID (e.g., JCS_UTILS, JUSTIN_ACCESS_LOGS) to analyze
    --search        : Keyword to search across all DB objects (Packages, Views, Tables, etc.)
    --out           : Path to save JSON output
    --json          : Output raw JSON to stdout (suppress logs)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
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
import glob
from typing import Dict, List, Any, Optional
import sys

# Ensure tools module can be imported
sys.path.append(os.getcwd())
try:
    from plugins.context_bundler.scripts.path_resolver import PathResolver
except ImportError:
    # Alternative path for different execution contexts
    sys.path.append(os.path.join(os.getcwd(), "plugins", "context-bundler", "scripts"))
    from path_resolver import PathResolver

class DbMiner:
    """
    Miner for Database Schema objects (Packages, Views, Tables).
    Extracts constraints, security rules, and validation logic.
    """
    def __init__(self, quiet: bool = False):
        self.repo_root = PathResolver.get_project_root()
        self.quiet = quiet
        self.rules: Dict[str, List[Dict[str, Any]]] = {
            "ValidationRules": [],
            "SecurityChecks": [],
            "ViewFilters": [],
            "IntegrityConstraints": []
        }

    def scan_packages(self, target: Optional[str] = None) -> None:
        """
        Scans .sql files in legacy-system/oracle-database/Packages.
        If target provided, scans only that package.
        """
        pkg_dir = os.path.join(self.repo_root, "legacy-system", "oracle-database", "Packages")
        if not os.path.exists(pkg_dir):
            print(f"Warning: Package directory not found: {pkg_dir}")
            return

        files_to_scan = []
        if target:
            # Try exact match ID or filename
            t_base = os.path.basename(target).replace(".sql", "").upper()
            
            # 1. PathResolver check (if mapped)
            mapped = PathResolver.get_object_path(t_base, "sql")
            if mapped and os.path.exists(mapped) and "Packages" in mapped:
                files_to_scan.append(mapped)
            else:
                 # 2. Heuristic check in Packages dir
                 exact = os.path.join(pkg_dir, f"{t_base}.sql")
                 if os.path.exists(exact):
                     files_to_scan.append(exact)
                 else:
                     # Check if it's a file path provided
                     if os.path.exists(target) and os.path.isfile(target):
                         files_to_scan.append(target)
                     # Else assumed not a package or not found
        else:
             files_to_scan = glob.glob(os.path.join(pkg_dir, "*.sql"))
        
        if files_to_scan:
            if not self.quiet:
                print(f"Scanning {len(files_to_scan)} Packages...")
            for sql_file in files_to_scan:
                pkg_name = os.path.basename(sql_file).replace(".sql", "").upper()
                try:
                    rel_path = os.path.relpath(sql_file, self.repo_root)
                    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self._extract_package_rules(pkg_name, content, rel_path)
                except Exception as e:
                    print(f"Error reading {sql_file}: {e}")

    def scan_views(self, target: Optional[str] = None) -> None:
        """
        Scans granular view files in legacy-system/oracle-database/Views/.
        If target provided, filters for that VIEW file.
        """
        view_dir = os.path.join(self.repo_root, "legacy-system", "oracle-database", "Views")
        if not os.path.exists(view_dir):
            print(f"Warning: Views directory not found: {view_dir}")
            return
        
        files_to_scan = []
        if target:
            t_base = os.path.basename(target).replace(".sql", "").upper()
            exact = os.path.join(view_dir, f"{t_base}.sql")
            if os.path.exists(exact):
                files_to_scan.append(exact)
        else:
            files_to_scan = glob.glob(os.path.join(view_dir, "*.sql"))
        
        if files_to_scan:
            if not self.quiet:
                print(f"Scanning {len(files_to_scan)} Views...")
            for view_file in files_to_scan:
                view_name = os.path.basename(view_file).replace(".sql", "").upper()
                try:
                    rel_path = os.path.relpath(view_file, self.repo_root)
                    with open(view_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self._extract_view_rules(view_name, content, rel_path)
                except Exception as e:
                    print(f"Error reading {view_file}: {e}")

    def scan_tables(self, target: Optional[str] = None) -> None:
        """
        Scans granular table files in legacy-system/oracle-database/Tables/.
        If target provided, filters for that TABLE file.
        """
        table_dir = os.path.join(self.repo_root, "legacy-system", "oracle-database", "Tables")
        if not os.path.exists(table_dir):
            print(f"Warning: Tables directory not found: {table_dir}")
            return
        
        files_to_scan = []
        if target:
            t_base = os.path.basename(target).replace(".sql", "").upper()
            exact = os.path.join(table_dir, f"{t_base}.sql")
            if os.path.exists(exact):
                files_to_scan.append(exact)
        else:
            files_to_scan = glob.glob(os.path.join(table_dir, "*.sql"))
        
        if files_to_scan:
            if not self.quiet:
                print(f"Scanning {len(files_to_scan)} Tables...")
            for table_file in files_to_scan:
                table_name = os.path.basename(table_file).replace(".sql", "").upper()
                try:
                    rel_path = os.path.relpath(table_file, self.repo_root)
                    with open(table_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self._extract_table_rules(table_name, content, rel_path)
                except Exception as e:
                    print(f"Error reading {table_file}: {e}")

    def scan_functions(self, target: Optional[str] = None) -> None:
        """Scans standalone function files in legacy-system/oracle-database/Functions/."""
        func_dir = os.path.join(self.repo_root, "legacy-system", "oracle-database", "Functions")
        self._scan_plsql_dir(func_dir, "Function", target)

    def scan_procedures(self, target: Optional[str] = None) -> None:
        """Scans standalone procedure files in legacy-system/oracle-database/Procedures/."""
        proc_dir = os.path.join(self.repo_root, "legacy-system", "oracle-database", "Procedures")
        self._scan_plsql_dir(proc_dir, "Procedure", target)

    def scan_triggers(self, target: Optional[str] = None) -> None:
        """Scans trigger files in legacy-system/oracle-database/Triggers/."""
        trig_dir = os.path.join(self.repo_root, "legacy-system", "oracle-database", "Triggers")
        self._scan_plsql_dir(trig_dir, "Trigger", target)

    def _scan_plsql_dir(self, directory: str, obj_type: str, target: Optional[str] = None) -> None:
        """Generic scanner for PL/SQL files (Functions, Procedures, Triggers)."""
        if not os.path.exists(directory):
            return
        
        files_to_scan = []
        if target:
            t_base = os.path.basename(target).replace(".sql", "").upper()
            exact = os.path.join(directory, f"{t_base}.sql")
            if os.path.exists(exact):
                files_to_scan.append(exact)
        else:
            files_to_scan = glob.glob(os.path.join(directory, "*.sql"))
        
        if files_to_scan:
            if not self.quiet:
                print(f"Scanning {len(files_to_scan)} {obj_type}s...")
            for sql_file in files_to_scan:
                obj_name = os.path.basename(sql_file).replace(".sql", "").upper()
                try:
                    rel_path = os.path.relpath(sql_file, self.repo_root)
                    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self._extract_plsql_rules(obj_name, obj_type, content, rel_path)
                except Exception as e:
                    print(f"Error reading {sql_file}: {e}")

    def _extract_plsql_rules(self, obj_name: str, obj_type: str, content: str, rel_path: str) -> None:
        """Extract validation rules and security checks from PL/SQL code."""
        source_label = f"{obj_type}:{obj_name}"
        
        # Validation Rules (RAISE_APPLICATION_ERROR)
        # Improved Regex: Handles simple variable or single-quoted string. Expects optional spaces then ) then optional ;
        matches = re.finditer(r'RAISE_APPLICATION_ERROR\s*\(\s*(-20\d{3})\s*,\s*(.*?)\)\s*(?:;|$)', content, re.IGNORECASE)
        for m in matches:
            code = m.group(1)
            msg = m.group(2).strip().strip("'")
            self.rules["ValidationRules"].append({
                "Source": source_label,
                "FilePath": rel_path,
                "RuleType": "AppError",
                "Code": code,
                "Message": msg[:100] + "..." if len(msg) > 100 else msg
            })

        # Security Checks (CHECK_ROLE / JUSTIN_ADMIN)
        if "CHECK_ROLE" in content.upper() or "GLOBAL.JUSTIN_" in content.upper():
            lines = content.splitlines()
            for idx, line in enumerate(lines):
                if "CHECK_ROLE" in line.upper() or "GLOBAL.JUSTIN_" in line.upper():
                    self.rules["SecurityChecks"].append({
                        "Source": source_label,
                        "FilePath": rel_path,
                        "Line": idx + 1,
                        "Snippet": line.strip()[:100]
                    })
    
    def _extract_table_rules(self, table_name: str, content: str, rel_path: str) -> None:
        """Extract rules from a single table definition."""
        # Scan logic for table constraints like CHECK, NOT NULL, etc.
        # Check for CHECK constraints
        check_matches = re.finditer(r'CHECK\s*\(\s*([^)]+)\)', content, re.IGNORECASE)
        for m in check_matches:
            constraint = m.group(1).strip()
            self.rules["IntegrityConstraints"].append({
                "Source": f"Table:{table_name}",
                "FilePath": rel_path,
                "ConstraintType": "CHECK",
                "Expression": constraint[:100] + "..." if len(constraint) > 100 else constraint
            })
        
        # Check for NOT NULL constraints
        not_null_matches = re.finditer(r'(\w+)\s+\w+.*?\bNOT\s+NULL\b', content, re.IGNORECASE)
        for m in not_null_matches:
            col_name = m.group(1)
            self.rules["IntegrityConstraints"].append({
                "Source": f"Table:{table_name}",
                "FilePath": rel_path,
                "ConstraintType": "NOT_NULL",
                "Column": col_name
            })

    def search_rules(self, term: str) -> List[str]:
        """Search extracted rules for term."""
        term = term.lower()
        matches = []
        
        for rule in self.rules["ValidationRules"]:
             if term in rule.get("Code","").lower() or term in rule.get("Message","").lower():
                 matches.append(f"Validation:{rule.get('Code')}")
                 
        for sec in self.rules["SecurityChecks"]:
             if term in sec.get("Snippet","").lower():
                 matches.append(f"Security:{sec.get('Source')}")
                 
        for const in self.rules["IntegrityConstraints"]:
             if term in const.get("Column","").lower() or term in const.get("Rule","").lower():
                 matches.append(f"Constraint:{const.get('Source')}")
                 
        for view in self.rules["ViewFilters"]:
             if term in view.get("Logic","").lower():
                 matches.append(f"ViewFilter:{view.get('Source')}")
                 
        return matches


    def _extract_package_rules(self, pkg_name: str, content: str, rel_path: str) -> None:
        """Helper to extract rules from package content."""
        # 1. Validation Rules (RAISE_APPLICATION_ERROR)
        matches = re.finditer(r'RAISE_APPLICATION_ERROR\s*\(\s*(-20\d{3})\s*,\s*(.*?)\)\s*(?:;|$)', content, re.IGNORECASE)
        for m in matches:
            code = m.group(1)
            msg = m.group(2).strip().strip("'")
            self.rules["ValidationRules"].append({
                "Source": f"Package:{pkg_name}",
                "FilePath": rel_path,
                "RuleType": "AppError",
                "Code": code,
                "Message": msg[:100] + "..." if len(msg) > 100 else msg
            })

        # 2. Security Checks (CHECK_ROLE / JUSTIN_ADMIN)
        if "CHECK_ROLE" in content.upper() or "GLOBAL.JUSTIN_" in content.upper():
            # Find context?
            lines = content.splitlines()
            for idx, line in enumerate(lines):
                if "CHECK_ROLE" in line.upper() or "GLOBAL.JUSTIN_" in line.upper():
                    self.rules["SecurityChecks"].append({
                        "Source": f"Package:{pkg_name}",
                        "FilePath": rel_path,
                        "Line": idx + 1,
                        "Snippet": line.strip()[:100]
                    })
                    
        # 3. Integrity (PRAGMA)
        if "PRAGMA RESTRICT_REFERENCES" in content.upper():
             matches = re.finditer(r'PRAGMA\s+RESTRICT_REFERENCES\s*\(\s*(\w+)\s*,\s*([^)]+)\)', content, re.IGNORECASE)
             for m in matches:
                 func = m.group(1)
                 purity = m.group(2)
                 self.rules["IntegrityConstraints"].append({
                     "Source": f"Package:{pkg_name}",
                     "FilePath": rel_path,
                     "Function": func,
                     "Purity": purity
                 })

    def _extract_view_rules(self, view_name: str, view_chunk: str, rel_path: str) -> None:
        """Helper to extract RLS from view definition."""
        
        # Extract WHERE clause
        # This is heuristics based. Look for "WHERE "
        if "WHERE" in view_chunk.upper():
            # Grab content after last WHERE
            parts = re.split(r'\bWHERE\b', view_chunk, flags=re.IGNORECASE)
            if len(parts) > 1:
                where_clause = parts[-1].strip().strip(';')
                if len(where_clause) > 200:
                    where_clause = where_clause[:200] + "..."
                
                self.rules["ViewFilters"].append({
                    "Source": f"View:{view_name}",
                    "FilePath": rel_path,
                    "RuleType": "RowLevelSecurity",
                    "Logic": where_clause
                })



def main():
    parser = argparse.ArgumentParser(description="Mine Business Rules from Database Schema (Method C)")
    parser.add_argument("--target", help="Specific DB object ID (e.g., JCS_UTILS, JUSTIN_ACCESS_LOGS) to analyze")
    parser.add_argument("--search", help="Keyword to search across DB objects")
    parser.add_argument("--out", help="Path to save JSON output", default="db_rules.json")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout (suppress logs)")
    args = parser.parse_args()
    
    miner = DbMiner(quiet=args.json)
    
    if args.target:
        if not args.json:
            print(f"Scanning for target: {args.target}...")
        miner.scan_packages(args.target)
        miner.scan_views(args.target)
        miner.scan_tables(args.target)
        miner.scan_functions(args.target)
        miner.scan_procedures(args.target)
        miner.scan_triggers(args.target)
        
    elif args.search:
        # Bulk Scan + Search
        # We need to scan all types? Or just iterate all files?
        # DbMiner has separate scan methods. Let's call them all without target.
        if not args.json:
            print(f"Scanning Full Database for '{args.search}'...")
            
        miner.scan_packages()
        miner.scan_views()
        miner.scan_tables()
        miner.scan_triggers()
        
        if args.json:
             # Just return unique file paths for matches
             unique_paths = set()
             term = args.search.lower()
             
             # Create helper to check rule content
             def check_rule(rule):
                 # Convert rule content to string and check
                 return term in str(rule).lower()

             for category in miner.rules:
                 for rule in miner.rules[category]:
                      if check_rule(rule):
                          # Try to get FilePath
                          if "FilePath" in rule:
                               unique_paths.add(rule["FilePath"])
             
             print(json.dumps(sorted(list(unique_paths)), indent=2))
        else:
             matches = miner.search_rules(args.search)
             print(f"Found {len(matches)} matches: {', '.join(matches[:10])}...")
        return
        
    else:
        if not args.json:
            print(f"Scanning Full Database...")
    
        # Scan all object types
        miner.scan_packages(args.target)
        miner.scan_views(args.target)
        miner.scan_tables(args.target)
        miner.scan_functions(args.target)
        miner.scan_procedures(args.target)
        miner.scan_triggers(args.target)
    
    output_json = json.dumps(miner.rules, indent=2)

    if args.json:
        print(output_json)
        return

    print(f"\nFound {len(miner.rules['ValidationRules'])} Validation Rules")
    print(f"Found {len(miner.rules['SecurityChecks'])} Security Checks")
    print(f"Found {len(miner.rules['ViewFilters'])} View Filters")
    print(f"Found {len(miner.rules['IntegrityConstraints'])} Constraints")
    
    if args.out:
        with open(args.out, 'w') as f:
            f.write(output_json)
        print(f"Saved to {args.out}")
    else:
        print(output_json)

if __name__ == "__main__":
    main()
