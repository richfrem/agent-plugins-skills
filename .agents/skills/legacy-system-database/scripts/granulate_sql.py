#!/usr/bin/env python3
"""
granulate_sql.py (CLI)
=====================================

Purpose:
    Splits monolithic SQL files into granular files per object (tables, views, etc).

Layer: Curate / Inventories

Usage Examples:
    python plugins/legacy-system-database/scripts/granulate_sql.py --help

Supported Object Types:
    - Generic

CLI Arguments:
    --types         : Comma-separated list of types to process (tables,views,packages,constraints,indexes,sequences) or 'all'
    --out           : Custom output root directory

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
import sys
import argparse

def get_repo_root():
    """Finds the repository root by looking for common markers."""
    current = os.getcwd()
    while current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, ".agent")) or \
           os.path.exists(os.path.join(current, ".git")) or \
           os.path.exists(os.path.join(current, "BOOTSTRAPPING.md")):
            return current
        current = os.path.dirname(current)
    return os.getcwd()

class SqlGranulator:
    def __init__(self, output_root: str = None):
        self.repo_root = get_repo_root()
        
        # Inputs (Source Directory)
        src_root = os.path.join(self.repo_root, "legacy-system", "oracle-database", "source")
        self.inputs = {
            "tables": os.path.join(src_root, "Tables", "JUSTIN_Tables.sql"),
            "views": os.path.join(src_root, "Views", "JUSTIN_Views.sql"),
            "constraints": os.path.join(src_root, "Contraints", "JUSTIN_Constraints.sql"), # Note: 'Contraints' typo in dir name
            "indexes": os.path.join(src_root, "Indexes", "JUSTIN-Indexes.sql"),
            "sequences": os.path.join(src_root, "Sequences", "JUSTIN_Sequences.sql"),
            "packages": os.path.join(self.repo_root, "legacy-system", "oracle-database", "Packages")
        }

        # Outputs (Top-level oracle-database)
        db_root = os.path.join(self.repo_root, "legacy-system", "oracle-database")
        if output_root:
            db_root = output_root

        self.outputs = {
            "tables": os.path.join(db_root, "Tables"),
            "views": os.path.join(db_root, "Views"),
            "constraints": os.path.join(db_root, "Constraints"),
            "indexes": os.path.join(db_root, "Indexes"),
            "sequences": os.path.join(db_root, "Sequences"),
            "functions": os.path.join(db_root, "Functions"),
            "procedures": os.path.join(db_root, "Procedures"),
            "types": os.path.join(db_root, "Types")
        }
        
        # Regexes
        self.regexes = {
            "tables": re.compile(r'^\s*(?:CREATE\s+(?:OR\s+REPLACE\s+)?(?:FORCE\s+)?(?:EDITIONABLE\s+)?)?TABLE\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?', re.IGNORECASE),
            "views": re.compile(r'^\s*(?:CREATE\s+(?:OR\s+REPLACE\s+)?(?:FORCE\s+)?(?:EDITIONABLE\s+)?)?VIEW\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?', re.IGNORECASE),
            "constraints": re.compile(r'^\s*ALTER\s+TABLE\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?\s+ADD\s+CONSTRAINT\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?', re.IGNORECASE),
            "indexes": re.compile(r'^\s*CREATE\s+(?:UNIQUE\s+|BITMAP\s+)?INDEX\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?\s+ON', re.IGNORECASE),
            "sequences": re.compile(r'^\s*CREATE\s+SEQUENCE\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?', re.IGNORECASE)
        }

    def process(self, types: list):
        """Runs the split process for requested types."""
        if "all" in types:
            types = ["tables", "views", "constraints", "indexes", "sequences", "packages"]

        for t in ["tables", "views", "indexes", "sequences"]:
            if t in types:
                self.split_file(self.inputs[t], self.outputs[t], t.capitalize(), self.regexes[t])
        
        if "constraints" in types:
            self.process_constraints()

        if "packages" in types:
            self.process_packages()

    def process_constraints(self):
        """Scans constraints file which has multi-line ALTER TABLE statements."""
        input_path = self.inputs["constraints"]
        output_dir = self.outputs["constraints"]
        print(f"Processing Constraints from {input_path} to {output_dir}...")
        
        if not os.path.exists(input_path):
            print(f"Error: File not found: {input_path}")
            return
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        current_table = None
        current_constraint = None
        current_buffer = []
        
        # Regexes
        alter_table_re = re.compile(r'^\s*ALTER\s+TABLE\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?', re.IGNORECASE)
        constraint_re = re.compile(r'^\s*ADD\s+(?:\(\s*)?CONSTRAINT\s+(?:\"[a-zA-Z0-9_]+\"\.)?\"?([a-zA-Z0-9_]+)\"?', re.IGNORECASE)
        
        count = 0
        
        for line in lines:
            # Check for Start (ALTER TABLE)
            match_table = alter_table_re.match(line)
            if match_table:
                # If we were processing one, verify if we need to close it? 
                # Usually blocks end with /
                # But if we see a new ALTER TABLE, the previous one is definitely done.
                if current_constraint and current_buffer:
                    self._write_file(output_dir, current_constraint, current_buffer)
                    count += 1
                
                current_table = match_table.group(1).upper()
                current_constraint = None # Unknown yet
                current_buffer = [line]
                continue
            
            # Check for Constraint Name (ADD CONSTRAINT)
            if current_buffer:
                current_buffer.append(line)
                match_con = constraint_re.match(line)
                if match_con:
                    current_constraint = match_con.group(1).upper()
                
                # Check for End (Slash /)
                if line.strip() == '/':
                    if current_constraint:
                        self._write_file(output_dir, current_constraint, current_buffer)
                        count += 1
                    current_table = None
                    current_constraint = None
                    current_buffer = []

        # Last one
        if current_constraint and current_buffer:
             self._write_file(output_dir, current_constraint, current_buffer)
             count += 1
             
        print(f"--> Generated {count} constraint files")

    def process_packages(self):
        """Scans source/Packages and splits them."""
        pkg_root = self.inputs["packages"]
        
        if not os.path.exists(pkg_root):
             print(f"Warning: Package source not found: {pkg_root}")
             return
             
        # Ensure outputs exist
        for d in [self.outputs["functions"], self.outputs["procedures"], self.outputs["types"]]:
            os.makedirs(d, exist_ok=True)

        print(f"Scanning Packages in {pkg_root}...")
        import glob
        pkg_files = glob.glob(os.path.join(pkg_root, "*.sql"))
        
        for pfile in pkg_files:
            try:
                self.split_package(pfile)
            except Exception as e:
                print(f"Error splitting package {pfile}: {e}")

    def split_package(self, pfile):
        with open(pfile, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract actual package name from the CREATE statement to preserve source case
        pkg_match = re.search(r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:PACKAGE\s+BODY|PACKAGE)\s+(?:\"?\w+\"?\.)?\"?(\w+)\"?', content, re.IGNORECASE)
        if pkg_match:
            pkg_name = pkg_match.group(1)
        else:
            # Fallback to filename logic if no CREATE match
            pkg_name = os.path.basename(pfile).replace(".sql", "")
            
        # Refinement: Search for END <name>; at the end of the file to discover developer-intended casing
        # We use \Z to ensure it's the final END tag, allowing optional / terminator and trailing whitespace
        end_pkg_match = re.search(r'\bEND\s+([a-zA-Z0-9_$]+)\s*;?\s*(?:/\s*)?\s*\Z', content.strip(), re.IGNORECASE)
        
        if end_pkg_match:
            end_name = end_pkg_match.group(1)
            if end_name.upper() == pkg_name.upper():
                pkg_name = end_name
        else:
            # Fallback: If this is a BODY file and we didn't find the name in the END tag,
            # check the corresponding specification file (if it exists) to discover the "Master Case".
            if "BODY" in os.path.basename(pfile).upper():
                spec_file = pfile.replace("Body.sql", ".sql").replace("BODY.sql", ".sql")
                if os.path.exists(spec_file) and spec_file != pfile:
                    try:
                        with open(spec_file, 'r', encoding='utf-8', errors='ignore') as sf:
                            spec_content = sf.read().strip()
                            s_match = re.search(r'\bEND\s+([a-zA-Z0-9_$]+)\s*;?\s*(?:/\s*)?\s*\Z', spec_content, re.IGNORECASE)
                            if s_match:
                                s_name = s_match.group(1)
                                if s_name.upper() == pkg_name.upper():
                                    pkg_name = s_name
                    except:
                        pass

        # Strip common body/spec suffixes for logical grouping (e.g. fis_clients_pkgBody -> fis_clients_pkg)
        pkg_name = re.sub(r'(_PKGBODY|_PKGSPEC|PKGBODY|PKGSPEC|_BODY|_SPEC|BODY|SPEC)$', '', pkg_name, flags=re.IGNORECASE).rstrip('_')

        lines = content.splitlines()
        current_type = None
        current_name = None
        current_buffer = []
        in_routine = False
        
        routine_start_re = re.compile(r'^\s*(PROCEDURE|FUNCTION)\s+([a-zA-Z0-9_]+)', re.IGNORECASE)
        routine_end_re = re.compile(r'^\s*END\s*([a-zA-Z0-9_]*)\s*;', re.IGNORECASE)
        type_start_re = re.compile(r'^\s*TYPE\s+([a-zA-Z0-9_]+)\s+IS', re.IGNORECASE)
        
        for line in lines:
            start_match = routine_start_re.match(line)
            
            if start_match and not in_routine:
                 rtype = start_match.group(1).upper()
                 rname = start_match.group(2) # Preserve case for filename
                 current_type = rtype
                 current_name = rname
                 current_buffer = [line]
                 in_routine = True
                 continue
            
            if not in_routine:
                type_match = type_start_re.match(line)
                if type_match:
                    tname = type_match.group(1).upper()
                    t_buffer = [line]
                    if ';' in line:
                         self._write_file(self.outputs["types"], f"{pkg_name}.{tname}", t_buffer)
                    else:
                         current_type = 'TYPE'
                         current_name = tname
                         current_buffer = [line]
                         in_routine = True
                    continue

            if in_routine:
                current_buffer.append(line)
                
                if current_type in ['PROCEDURE', 'FUNCTION']:
                    end_match = routine_end_re.match(line)
                    if end_match:
                        end_name = end_match.group(1).upper()
                        # Match if name matches OR if END; has no name but we are in a routine
                        if not end_name or end_name == current_name.upper():
                            out_dir = self.outputs["procedures"] if current_type == 'PROCEDURE' else self.outputs["functions"]
                            fname = f"{pkg_name}.{current_name}" # Uses case-preserved name
                            self._write_file(out_dir, fname, current_buffer)
                            in_routine = False
                            current_type = None
                            current_buffer = []
                
                if current_type == 'TYPE':
                    if line.strip().endswith(';'):
                        self._write_file(self.outputs["types"], f"{pkg_name}.{current_name}", current_buffer)
                        in_routine = False
                        current_type = None
                        current_buffer = []

    def split_file(self, input_path: str, output_dir: str, type_label: str, regex, name_group=1):
        print(f"Processing {type_label} from {input_path} to {output_dir}...")
        
        if not os.path.exists(input_path):
            print(f"Error: File not found: {input_path}")
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.splitlines()
            count = 0
            current_name = None
            current_buffer = []

            for line in lines:
                match = regex.match(line)
                
                if match:
                    if current_name and current_buffer:
                        self._write_file(output_dir, current_name, current_buffer)
                        count += 1
                    
                    # Group N is the name
                    try:
                        current_name = match.group(name_group).upper()
                    except IndexError:
                        print(f"Warning: Regex group {name_group} not found in match: {line}")
                        current_name = "UNKNOWN"

                    current_buffer = [line]
                else:
                    if current_name:
                        current_buffer.append(line)
            
            if current_name and current_buffer:
                self._write_file(output_dir, current_name, current_buffer)
                count += 1
                
            print(f"--> Generated {count} files")
            
        except Exception as e:
            print(f"Error processing {input_path}: {e}")

    def _write_file(self, output_dir: str, name: str, buffer: list):
        out_path = os.path.join(output_dir, f"{name}.sql")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(buffer))

def main():
    parser = argparse.ArgumentParser(description="Split monolithic SQL files into granular objects.")
    parser.add_argument("--types", help="Comma-separated list of types to process (tables,views,packages,constraints,indexes,sequences) or 'all'", default="tables,views")
    parser.add_argument("--out", help="Custom output root directory", default=None)
    
    args = parser.parse_args()
    
    types = [t.strip().lower() for t in args.types.split(",")]
    
    granulator = SqlGranulator(output_root=args.out)
    print(f"Starting SQL Granulator (Target: {types})...")
    granulator.process(types)
    print("Done.")

if __name__ == "__main__":
    main()
