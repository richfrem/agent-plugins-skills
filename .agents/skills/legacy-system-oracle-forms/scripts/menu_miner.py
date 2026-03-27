#!/usr/bin/env python3
"""
menu_miner.py (CLI)
=====================================

Purpose:
    Extracts Hierarchy, Roles, Commands from Menu Modules.

Layer: Curate / Miners

Usage Examples:
    python plugins/legacy-system-oracle-forms/scripts/menu_miner.py --help
    python plugins/legacy-system-oracle-forms/scripts/menu_miner.py --target legacy-system/oracle-forms/XML/FORM0000_mmb.xml
    python plugins/legacy-system-oracle-forms/scripts/menu_miner.py --search "APP2_ETRY" --json
    python plugins/legacy-system-oracle-forms/scripts/menu_miner.py --target legacy-system/oracle-forms/XML/FORM0000_mmb.xml --json

Supported Object Types:
    - Generic

CLI Arguments:
    file            : Path to Menu XML

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
import xml.etree.ElementTree as ET
import argparse
import json
import os
import re
import glob
from pathlib import Path

# Constants
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
MENU_XML_DIR = PROJECT_ROOT / "legacy-system" / "oracle-forms" / "XML"

class MenuMiner:
    def __init__(self):
        self.metadata = {
            "ID": "",
            "FilePath": "",
            "Name": "",
            "Roles": [],
            "AttachedLibraries": [],
            "Menus": [], 
            "ProgramUnits": []
        }
    
    def strip_namespace(self, tag):
        if '}' in tag:
            return tag.split('}', 1)[1]
        return tag

    def analyze(self, file_path):
        try:
            # Calculate relative path if possible, else abs
            try:
                 repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                 rel_path = os.path.relpath(file_path, repo_root)
                 self.metadata["FilePath"] = rel_path
            except ValueError:
                 self.metadata["FilePath"] = file_path

            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return
        
        # Traverse to find MenuModule
        menu_module = None
        # Root might be Module or MenuModule
        if self.strip_namespace(root.tag) == "MenuModule":
            menu_module = root
        else:
            for child in root:
                if self.strip_namespace(child.tag) == "MenuModule":
                    menu_module = child
                    break
        
        if menu_module is None:
            return

        self.metadata["Name"] = menu_module.attrib.get("Name", "")
        self.metadata["ID"] = self.metadata["Name"]

        # Attached Libraries
        # Using iter because findall with namespace wildcards behaves differently across versions
        for elem in menu_module.iter():
            tag = self.strip_namespace(elem.tag)
            
            if tag == "AttachedLibrary":
                 self.metadata["AttachedLibraries"].append(elem.attrib.get("Name"))
            
            elif tag == "MenuModuleRole":
                 val = elem.attrib.get("Value")
                 if val and val not in self.metadata["Roles"]:
                     self.metadata["Roles"].append(val)

            elif tag == "ProgramUnit":
                 text = elem.attrib.get("ProgramUnitText")
                 # Decode HTML entities if needed? ElementTree handles some.
                 # Actually in Oracle XML, newlines are &#10; which ET should decode?
                 # Let's check output.
                 self.metadata["ProgramUnits"].append({
                     "Name": elem.attrib.get("Name"),
                     "Type": elem.attrib.get("ProgramUnitType"),
                     "Text": text
                 })

        # Menus (Scan top level children of MenuModule that are Menus)
        # We need structure, so we iterate direct children or findall
        # findall needs namespace handling
        ns = ""
        if '}' in menu_module.tag:
            ns = menu_module.tag.split('}')[0] + "}"
        
        # Find all direct Menu children
        for menu in menu_module.findall(f"{ns}Menu"):
            menu_data = {
                "Name": menu.attrib.get("Name"),
                "Items": []
            }
            for item in menu.findall(f"{ns}MenuItem"):
                # Handle MenuItemRole
                item_roles = []
                for ir in item.findall(f"{ns}MenuItemRole"):
                     item_roles.append(ir.attrib.get("Value"))

                code = item.attrib.get("MenuItemCode", "")
                
                # Heuristic extract target
                target = ""
                if code:
                    # 1. Clean up common Oracle/Project trigger patterns
                    # We normalize code to uppercase for the regex, but strip wrappers first
                    # Look for strings inside single quotes first
                    potential_ids = re.findall(r"'([a-zA-Z0-9_]+)'", code)
                    
                    for candidate in potential_ids:
                        # Strip known prefixes from the candidate string
                        # e.g., OpenModuleFORM0000 -> FORM0000
                        clean_candidate = re.sub(r'^(?:AppFour|AppThree|AppFive|AppTwo|AppOne|POS|AGN)?(?:OpenModule|OpenReport|GoForm|GoReport|GoMainMenu)', '', candidate, flags=re.IGNORECASE)
                        
                        # Strict Form/Report ID Regex: 
                        # 3-4 letters (App Code), followed by E (Entry/Form), R (Report), M (Menu), or L (Library)
                        # followed by 4 digits, optional suffix.
                        # We use UPPER here to be precise.
                        m2 = re.search(r"([A-Z]{3,4}[ERML]\d{4}[A-Z]?)", clean_candidate.upper())
                        if m2:
                            target = m2.group(1)
                            # Handle those persistent prefixes like 'E' or 'T' if they still leaked through
                            if len(target) > 8 and target[0] in ['E', 'T']:
                                # If it's something like EFORM0000, check if stripping first char yields valid ID
                                if re.match(r"[A-Z]{3,4}[ERML]\d{4}", target[1:]):
                                    target = target[1:]
                            break

                    # 2. Fallback: Search the whole code block for anything looking like an ID 
                    # but avoid parts of words by checking boundaries
                    if not target:
                        # Extract any word-like chunks and check them
                        for chunk in re.split(r'[^a-zA-Z0-9_]', code):
                            m3 = re.search(r"^([A-Z]{3,4}[ERML]\d{4}[A-Z]?)$", chunk.upper())
                            if m3:
                                target = m3.group(1)
                                break

                menu_data["Items"].append({
                    "Name": item.attrib.get("Name"),
                    "Label": item.attrib.get("Label"),
                    "CommandType": item.attrib.get("CommandType"),
                    "CommandText": code,
                    "SubMenu": item.attrib.get("SubMenuName"),
                    "Roles": item_roles,
                    "Target": target
                })
            self.metadata["Menus"].append(menu_data)
        
        # Second pass: Look up procedure calls in ProgramUnits to extract targets
        self._resolve_procedure_targets()

    def _resolve_procedure_targets(self):
        """Look up procedure calls in ProgramUnits to extract form/report targets."""
        # Build lookup of procedure name -> extracted target from procedure text
        proc_targets = {}
        for pu in self.metadata["ProgramUnits"]:
            name = pu.get("Name", "").upper()
            text = pu.get("Text", "") or ""
            
            # Look for report_printing('XXXX0000' or CallForm.Do('XXXX0000'
            # or goform.do('XXXX0000'
            matches = re.findall(r"(?:report_printing|callform\.do|goform\.do|open_form|call_form)\s*\(\s*'([^']+)'", text, re.IGNORECASE)
            for match in matches:
                m = re.search(r"([A-Z]{3,4}[ERML]\d{4}[A-Z]?)", match.upper())
                if m:
                    proc_targets[name] = m.group(1)
                    break
        
        # Now scan menu items that have no target but call a procedure
        for menu in self.metadata["Menus"]:
            for item in menu["Items"]:
                if item.get("Target"):
                    continue
                    
                code = item.get("CommandText", "") or ""
                # Decode common entities and strip whitespace
                code = code.replace('&#10;', '\n').replace('&amp;', '&').strip()
                
                # Look for procedure call: PROC_NAME; or PROC_NAME();
                proc_match = re.search(r'^([A-Za-z_][A-Za-z0-9_]*)\s*[;\(]', code.strip())
                if proc_match:
                    proc_name = proc_match.group(1).upper()
                    if proc_name in proc_targets:
                        item["Target"] = proc_targets[proc_name]
                        item["Target"] = proc_targets[proc_name]

    def to_json(self):
        return json.dumps(self.metadata, indent=2)

    def search_content(self, term):
        """Search metadata for term."""
        term = term.lower()
        matches = []
        
        if term in self.metadata["Name"].lower():
             matches.append("MenuModule:Name")

        for pu in self.metadata["ProgramUnits"]:
             if term in pu["Name"].lower() or term in (pu["Text"] or "").lower():
                  matches.append(f"ProgramUnit:{pu['Name']}")
                  
        for menu in self.metadata["Menus"]:
             for item in menu["Items"]:
                  if term in (item["Label"] or "").lower() or term in (item["CommandText"] or "").lower():
                       matches.append(f"MenuItem:{item['Name']}")
                       
        return matches

    def to_json(self):
        return json.dumps(self.metadata, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="Path to Menu XML")
    parser.add_argument("--search", help="Keyword to search across Menus")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout (suppress logs)")
    args = parser.parse_args()
    
    if args.target:
        miner = MenuMiner()
        miner.analyze(args.target)
        print(miner.to_json())
        return

    # Bulk Mode
    files = list(MENU_XML_DIR.glob("*_mmb.xml"))
    
    if not args.json:
        print(f"Scanning {len(files)} menus in {MENU_XML_DIR}...")
        
    results = []
    for f in files:
        miner = MenuMiner()
        miner.analyze(str(f))
        
        if args.search:
            matches = miner.search_content(args.search)
            if matches:
                 if args.json:
                     results.append({
                         "Menu": miner.metadata["Name"],
                         "FilePath": miner.metadata["FilePath"],
                         "Matches": matches
                     })
                 else:
                     print(f"[{miner.metadata['Name']}] Found {len(matches)} matches: {', '.join(matches[:5])}...")
        else:
             if args.json:
                 results.append(miner.metadata)
             else:
                 print(f"Processed {miner.metadata['Name']}")

    if args.json:
        print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
