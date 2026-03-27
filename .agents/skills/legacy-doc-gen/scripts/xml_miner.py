#!/usr/bin/env python3
"""
xml_miner.py (CLI)
=====================================

Purpose:
    Extracts declaratives (Triggers, PUs, Props) from Form XML.

Layer: Curate / Miners

Usage Examples:
    python plugins/legacy-system-oracle-forms/scripts/xml_miner.py --help
    python plugins/legacy-system-oracle-forms/scripts/xml_miner.py --target FORM0000 --json
    python plugins/legacy-system-oracle-forms/scripts/xml_miner.py --search "ADD_ACCESS_LOG_RECORD" --json
    python plugins/legacy-system-oracle-forms/scripts/xml_miner.py --target FORM0000            # Analyze Form
    python plugins/legacy-system-oracle-forms/scripts/xml_miner.py --target FORM0000            # Analyze Menu
    python plugins/legacy-system-oracle-forms/scripts/xml_miner.py --target APP2_OLB             # Analyze Object Library
    python plugins/legacy-system-oracle-forms/scripts/xml_miner.py --target "path/to/file.xml"  # Analyze file path

Supported Object Types:
    - Generic

CLI Arguments:
    --target        : Form ID (e.g., FORM0000) or path to XML file
    --search        : Keyword to search across all Forms (Validation Logic, Calls, Subclasses)
    --out           : Path to save JSON output
    --json          : Output raw JSON to stdout (suppress logs)

Input Files:
    - (See code)

Output:
    - (See code)

Key Functions:
    - find_xml_file(): Locates the XML file for a given Form/Menu/Lib ID.
    - mine_declarative_rules(): Parses the Oracle Forms XML using Object-Oriented Processors.
    - main(): No description.

Script Dependencies:
    (None detected)

Consumed by:
    (Unknown)
"""
import xml.etree.ElementTree as ET
import argparse
import os
import re
import json
import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
import sys

_SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in _SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

# Ensure tools module can be imported
sys.path.append(os.getcwd())
try:
    from tools.investigate.utils.path_resolver import PathResolver
except ImportError:
    # Fallback if running from subfolder (not recommended but handled)
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from tools.investigate.utils.path_resolver import PathResolver

# =================================================================================
# 1. Base Processor
# =================================================================================
class BaseProcessor:
    """Base class for mining business rules from specific XML elements."""
    def __init__(self, tag_name: str):
        self.tag_name = tag_name
        
    def get_prop(self, elem: ET.Element, name: str) -> Optional[str]:
        """
        Helper to safely get attribute value (checked first) or Property sub-element.
        
        Args:
            elem: The XML element to search.
            name: The name of the property/attribute.
            
        Returns:
            The value as a string, or None if not found.
        """
        # 1. Check direct attribute (XML Attribute)
        if name in elem.attrib:
            return elem.attrib[name]
            
        # 2. Check Property sub-element (Verbose XML)
        # Note: Strip namespace if needed in XPath, but here we assume cleaned tree
        p = elem.find(f"./Property[@Name='{name}']")
        return p.get("Value") if p is not None else None

    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        Override this method to extract rules and append to rules_dict.
        """
        pass

    def check_inheritance(self, elem: ET.Element, obj_name: str, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        """Checks for ParentModule or ParentFilename to detect OLB/Subclassing."""
        parent_mod = self.get_prop(elem, "ParentModule")
        parent_file = self.get_prop(elem, "ParentFilename")
        if parent_mod or parent_file:
            rules_dict["Inheritance"].append({
                "Object": obj_name,
                "Type": self.tag_name,
                "ParentModule": parent_mod,
                "ParentFilename": parent_file
            })

# =================================================================================
# 2. Element Processors
# =================================================================================
class FormModuleProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("FormModule")
        
    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        name = elem.get("Name")
        rules_dict["Metadata"].append({
            "FormName": name,
            "Title": self.get_prop(elem, "Title"),
            "MenuModule": self.get_prop(elem, "MenuModule")
        })

class AttachedLibraryProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("AttachedLibrary")
        
    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        rules_dict["Libraries"].append({
            "LibraryName": elem.get("Name")
        })

class BlockProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("Block")
        
    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        block_name = elem.get("Name")
        
        # Rule: Where Clause (Row Level Security / Filtering)
        val = self.get_prop(elem, "WhereClause")
        if val:
            rules_dict["SecurityFilters"].append({
                "Block": block_name,
                "Rule": "WhereClause",
                "Value": val
            })
            
        # Rule: Delete Allowed (Immutability)
        val = self.get_prop(elem, "DeleteAllowed")
        if val == "false":
            rules_dict["Immutability"].append({
                "Block": block_name,
                "Rule": "DeleteAllowed=False"
            })
            
        # Rule: Enforced Column Security
        val = self.get_prop(elem, "EnforcedColumnSecurity")
        if val == "true":
            rules_dict["SecurityFilters"].append({
                "Block": block_name,
                "Rule": "EnforcedColumnSecurity"
            })
            
        self.check_inheritance(elem, block_name, rules_dict)

class ItemProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("Item")
        
    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        item_name = elem.get("Name")
        
        # Rule: Required (Mandatory Fields)
        val = self.get_prop(elem, "Required")
        if val == "true":
            rules_dict["MandatoryFields"].append({
                "Item": item_name,
                "Rule": "Required"
            })
            
        # Rule: Format Mask (Data Integrity)
        val = self.get_prop(elem, "FormatMask")
        if val:
            rules_dict["DataIntegrity"].append({
                "Item": item_name,
                "Rule": "FormatMask",
                "Value": val
            })
            
        # Rule: Update Allowed (Immutability)
        val = self.get_prop(elem, "UpdateAllowed")
        if val == "false":
            rules_dict["Immutability"].append({
                "Item": item_name,
                "Rule": "UpdateAllowed=False"
            })
            
        # Rule: Copy Value From (Data Flow)
        val = self.get_prop(elem, "CopyValueFromItem")
        if val:
            rules_dict["DataIntegrity"].append({
                "Item": item_name,
                "Rule": "CopyValueFrom",
                "Value": val
            })
            
        # Rule: Formula (Calculation Logic)
        val = self.get_prop(elem, "Formula")
        if val:
            rules_dict["DataIntegrity"].append({
                "Item": item_name,
                "Rule": "Formula",
                "Value": val
            })
            
        # Rule: Validate From List (Strict Reference Data)
        val = self.get_prop(elem, "ValidateFromList")
        if val == "true":
            rules_dict["DataIntegrity"].append({
                "Item": item_name,
                "Rule": "ValidateFromList",
                "Value": "True"
            })
            
        # Rule: Case Restriction
        val = self.get_prop(elem, "CaseRestriction")
        if val:
            rules_dict["DataIntegrity"].append({
                "Item": item_name,
                "Rule": "CaseRestriction",
                "Value": val
            })
            
        # Rule: Range Constraint
        val_low = self.get_prop(elem, "LowestAllowedValue")
        val_high = self.get_prop(elem, "HighestAllowedValue")
        if val_low or val_high:
            rules_dict["DataIntegrity"].append({
                "Item": item_name,
                "Rule": "RangeConstraint",
                "Value": f"{val_low} - {val_high}"
            })
        
        self.check_inheritance(elem, item_name, rules_dict)

class RecordGroupProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("RecordGroup")
        
    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        rg_name = elem.get("Name")
        val = self.get_prop(elem, "RecordGroupQuery")
        if val:
            # Clean up newlines/spaces for reading
            clean_query = " ".join(val.split())
            rules_dict["ValidValues"].append({
                "RecordGroup": rg_name,
                "Query": clean_query[:100] + "..." if len(clean_query) > 100 else clean_query
            })

class RelationProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("Relation")
        
    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        rel_name = elem.get("Name")
        detail_block = self.get_prop(elem, "DetailBlock")
        
        # Rule: Masterless Operations (Data Integrity)
        val = self.get_prop(elem, "PreventMasterlessOperations")
        if val == "true":
            rules_dict["DataIntegrity"].append({
                "Relation": rel_name,
                "DetailBlock": detail_block,
                "Rule": "PreventMasterlessOperations"
            })
            
        # Rule: Join Condition (Data Logic)
        val = self.get_prop(elem, "JoinCondition")
        if val:
            rules_dict["DataIntegrity"].append({
                "Relation": rel_name,
                "DetailBlock": detail_block,
                "Rule": "JoinCondition",
                "Value": val
            })
            
        # Rule: Delete Record Behavior (Cascading Logic)
        val = self.get_prop(elem, "DeleteRecord")
        if val:
             rules_dict["DataIntegrity"].append({
                "Relation": rel_name,
                "DetailBlock": detail_block,
                "Rule": "DeleteBehavior",
                "Value": val
            })

class MenuItemProcessor(BaseProcessor):
    def __init__(self):
        super().__init__("MenuItem")
        
    def process(self, elem: ET.Element, rules_dict: Dict[str, List[Dict[str, Any]]]) -> None:
        menu_name = elem.get("Name")
        
        # Rule: Access Control (Enabled/Visible)
        val_en = self.get_prop(elem, "Enabled")
        val_vis = self.get_prop(elem, "Visible")
        
        if val_en == "false":
            rules_dict["SecurityFilters"].append({
                "MenuItem": menu_name,
                "Rule": "Enabled=False"
            })
        if val_vis == "false":
            rules_dict["SecurityFilters"].append({
                "MenuItem": menu_name,
                "Rule": "Visible=False"
            })
            
        # Rule: Menu Logic (PL/SQL in Menu)
        val_code = self.get_prop(elem, "MenuItemCode")
        if val_code:
            rules_dict["ValidValues"].append({
                 "MenuItem": menu_name,
                 "Rule": "MenuItemCode",
                 "Value": "Has PL/SQL Logic"
            })

# =================================================================================
# 3. Main Miner Logic
# =================================================================================

def find_xml_file(target_id: str, base_dir: str = r"legacy-system/oracle-forms/XML") -> Optional[str]:
    """
    Locates the XML file for a given Form/Menu/Lib ID.
    Uses Master Object Collection via PathResolver first, then heuristics.
    """
    # 1. Try Master Index
    try:
        path = PathResolver.get_object_path(target_id, "xml")
        if path and os.path.exists(path):
            return path
    except Exception:
        pass # Fallback

    repo_root = PathResolver.get_project_root()
    search_dir = os.path.join(repo_root, base_dir)
    
    # Try exact path
    if target_id.endswith(".xml") and os.path.exists(target_id):
        return target_id
    
    # Try exact match ID (fmb, mmb, olb)
    for suffix in ["_fmb.xml", "_mmb.xml", "_olb.xml"]:
        xml_path = os.path.join(search_dir, f"{target_id.lower()}{suffix}")
        if os.path.exists(xml_path):
            return xml_path
        
    # Try Glob
    pattern = os.path.join(search_dir, f"{target_id.lower()}*.xml")
    matches = glob.glob(pattern)
    return matches[0] if matches else None

def mine_declarative_rules(xml_path: str) -> Dict[str, Any]:
    """
    Parses the Oracle Forms XML using Object-Oriented Processors.
    
    Args:
        xml_path: Path to the XML file.
        
    Returns:
        Dictionary of extracted rules categorized by type.
    """
    try:
        # Pre-process: Strip namespaces to simplify parsing
        with open(xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        xml_content = re.sub(r'xmlns="[^"]+"', '', xml_content, count=1)
        root = ET.fromstring(xml_content)
    except Exception as e:
        return {"error": f"Failed to parse XML: {e}"}

    # Initialize results container
    rules: Dict[str, Any] = {
        "FilePath": "",
        "MandatoryFields": [],
        "SecurityFilters": [],
        "Immutability": [],
        "DataIntegrity": [],
        "ValidValues": [],
        "Metadata": [],
        "Libraries": [],
        "Inheritance": []
    }
    
    # Initialize Processors
    processors: Dict[str, BaseProcessor] = {
        "FormModule": FormModuleProcessor(),
        "AttachedLibrary": AttachedLibraryProcessor(),
        "Block": BlockProcessor(),
        "Item": ItemProcessor(),
        "RecordGroup": RecordGroupProcessor(),
        "Relation": RelationProcessor(),
        "MenuItem": MenuItemProcessor()
    }
    
    # Walk the tree and dispatch to processors
    # Using iter() finds all elements at any depth
    for elem in root.iter():
        if elem.tag in processors:
            processors[elem.tag].process(elem, rules)

    return rules

def search_rules(rules: Dict[str, Any], term: str) -> List[str]:
    """Search extracted rules for a term."""
    term = term.lower()
    matches = []
    
    # Check Program Units (if they were extracted? xml_miner mines declarative rules mostly)
    # But wait, xml_miner mines "ProgramUnitCalls" in some versions? 
    # Let's check mine_declarative_rules function.
    # It extracts ValidationLogic which contains code snippets.
    
    for rule in rules.get("ValidationLogic", []):
         if term in rule.get("Code", "").lower():
              matches.append(f"ValidationLogic:{rule.get('Trigger')}")

    for call in rules.get("ProgramUnitCalls", []):
         if term in call.get("Target", "").lower():
              matches.append(f"Call:{call.get('Target')}")

    # Check Triggers/Code in declarative rules
    for sub in rules.get("SubclassSubstitutions", []):
         if term in sub.get("Object", "").lower():
             matches.append(f"Subclass:{sub.get('Object')}")

    return matches

def main():
    parser = argparse.ArgumentParser(description="Mine Declarative Business Rules from Oracle Forms XML")
    parser.add_argument("--target", help="Form ID (e.g., FORM0000) or path to XML file")
    parser.add_argument("--search", help="Keyword to search across Forms")
    parser.add_argument("--out", help="Path to save JSON output")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout (suppress logs)")
    
    args = parser.parse_args()
    
    if args.target:
        xml_path = find_xml_file(args.target)
        if not xml_path:
            print(f"Error: Could not find XML file for {args.target}")
            return

        if not args.json:
            print(f"Analyzing: {xml_path}")
            
        results = mine_declarative_rules(xml_path)
        
        # Add FilePath
        try:
             repo_root = str(_find_project_root())
             results["FilePath"] = os.path.relpath(xml_path, repo_root)
        except ValueError:
             results["FilePath"] = xml_path

        output_json = json.dumps(results, indent=2)
        
        if args.json:
            print(output_json)
            return

        print(output_json)
        
        if args.out:
            with open(args.out, 'w') as f:
                f.write(output_json)
            print(f"Saved to {args.out}")
        return

    # Bulk Mode
    if args.search:
        # We need to find ALL XMLs.
        # find_xml_file logic uses glob.
        search_dir = os.path.join(str(_find_project_root()), "legacy-system", "oracle-forms", "XML")
        files = glob.glob(os.path.join(search_dir, "*_fmb.xml"))
        
        if not args.json:
             print(f"Scanning {len(files)} forms in {search_dir}...")
             
        unique_paths = set()
        repo_root = str(_find_project_root())

        for f in files:
            # We strictly analyze if search term is present? Analysis is expensive.
            # xml_miner parses XML.
            res = mine_declarative_rules(f)
            matches = search_rules(res, args.search)
            if matches:
                 try:
                     rp = os.path.relpath(f, repo_root)
                 except:
                     rp = f
                 unique_paths.add(rp)
                 
                 if not args.json:
                    print(f"[{os.path.basename(f)}] Found {len(matches)} matches")

        if args.json:
            # Output matching files list
            print(json.dumps(sorted(list(unique_paths)), indent=2))

if __name__ == "__main__":
    main()
