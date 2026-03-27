#!/usr/bin/env python3
"""
report_miner.py (CLI)
=====================================

Purpose:
    Extracts Queries, Params, Triggers from Reports.

Layer: Curate / Miners

Usage Examples:
Usage Examples:
    python plugins/legacy-system-oracle-reports/scripts/report_miner.py --help
    python plugins/legacy-system-oracle-reports/scripts/report_miner.py --target legacy-system/oracle-reports/XML/RPT0086.xml
    python plugins/legacy-system-oracle-reports/scripts/report_miner.py --search "invoice_dt" --json
    python plugins/legacy-system-oracle-reports/scripts/report_miner.py --search "RPT0086"

Supported Object Types:
    - Generic

CLI Arguments:
    file            : Path to Report XML

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
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent
REPORT_XML_DIR = PROJECT_ROOT / "legacy-system" / "oracle-reports" / "XML"

class ReportMiner:
    def __init__(self):
        self.metadata = {
            "ID": "",
            "FilePath": "",
            "Name": "",
            "Queries": [],
            "Parameters": [],
            "Triggers": [],
            "Groups": [],
            "AttachedLibraries": []
        }

    def analyze(self, file_path):
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Calculate relative path
            try:
                 repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                 self.metadata["FilePath"] = os.path.relpath(file_path, repo_root)
            except ValueError:
                 self.metadata["FilePath"] = file_path

        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return

        self.metadata["ID"] = os.path.basename(file_path).replace('.xml', '').upper()
        self.metadata["Name"] = root.attrib.get("name", self.metadata["ID"])

        # Data Sources & Queries
        for ds in root.findall(".//dataSource"):
            select_stmt = ds.find("select")
            query = ""
            if select_stmt is not None:
                # CDATA is handled by ElementTree automatically usually
                query = select_stmt.text.strip() if select_stmt.text else ""
            
            self.metadata["Queries"].append({
                "Name": ds.attrib.get("name"),
                "SQL": query
            })

            # Groups inside data source
            for grp in ds.findall("group"):
                self.metadata["Groups"].append({
                    "Name": grp.attrib.get("name"),
                    "DataSource": ds.attrib.get("name")
                })

        # Parameters
        for param in root.findall(".//userParameter"):
            self.metadata["Parameters"].append({
                "Name": param.attrib.get("name"),
                "Datatype": param.attrib.get("datatype"),
                "Width": param.attrib.get("width"),
                "Label": param.attrib.get("defaultLabel")
            })

        # Program Units (Triggers, Functions)
        # Search for all children of programUnits
        pu_container = root.find("programUnits")
        if pu_container is not None:
            for unit in pu_container:
                unit_type = unit.tag
                name = unit.attrib.get("name")
                text_source = unit.find("textSource")
                code = text_source.text.strip() if text_source is not None and text_source.text else ""
                
                self.metadata["Triggers"].append({
                    "Name": name,
                    "Type": unit_type,
                    "Code": code
                })

        # Attached Libraries
        for lib in root.findall(".//attachedLibrary"):
             self.metadata["AttachedLibraries"].append(lib.attrib.get("name"))

        # Heuristic Title Extraction
        possible_title = self.extract_title_heuristic(root)
        if possible_title:
             self.metadata["Name"] = possible_title

    def extract_title_heuristic(self, root):
        candidates = []
        for text_seg in root.findall(".//textSegment"):
            font = text_seg.find("font")
            string_elem = text_seg.find("string")
            if font is not None and string_elem is not None and string_elem.text:
                text = string_elem.text.strip()
                if not text: continue
                
                try:
                    size = float(font.attrib.get("size", "0"))
                except:
                    size = 0
                bold = font.attrib.get("bold", "no") == "yes"
                
                score = size
                if bold: score += 5
                
                # Filter common noise
                if any(x in text for x in ["Page:", "Report ID:", "Date:", "Time:", "of "]):
                    continue
                if len(text) < 4: 
                    continue
                    
                candidates.append((score, text))
        
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        return ""

    def search_content(self, term):
        """Search metadata for term."""
        term = term.lower()
        matches = []
        
        # Search Queries
        for q in self.metadata["Queries"]:
            if term in q["SQL"].lower() or term in (q["Name"] or "").lower():
                matches.append(f"Query:{q['Name']}")
        
        # Search Parameters
        for p in self.metadata["Parameters"]:
            if term in (p["Name"] or "").lower():
                matches.append(f"Param:{p['Name']}")
                
        # Search Triggers
        for t in self.metadata["Triggers"]:
            if term in (t["Code"] or "").lower() or term in (t["Name"] or "").lower():
                matches.append(f"Trigger:{t['Name']}")
                
        return matches

    def to_json(self):
        return json.dumps(self.metadata, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="Specific Report XML file to analyze")
    parser.add_argument("--search", help="Keyword to search for across all reports")
    parser.add_argument("--json", action="store_true", help="Output raw JSON to stdout (suppress logs)")
    args = parser.parse_args()
    
    if args.target:
        # Analyze single file
        if not args.json:
            print(f"Analyzing {args.target}...")
        miner = ReportMiner()
        miner.analyze(args.target)
        print(miner.to_json())
        return

    # Bulk Mode
    files = list(REPORT_XML_DIR.glob("*.xml"))
    
    if not args.json:
        print(f"Scanning {len(files)} reports in {REPORT_XML_DIR}...")

    results = []
    for f in files:
        miner = ReportMiner()
        miner.analyze(str(f))
        
        if args.search:
            matches = miner.search_content(args.search)
            if matches:
                if args.json:
                     # Minimal info for search list
                     results.append({
                         "Report": miner.metadata["ID"],
                         "FilePath": miner.metadata["FilePath"],
                         "Matches": matches
                     })
                else:
                     print(f"[{miner.metadata['ID']}] Found {len(matches)} matches: {', '.join(matches[:5])}...")
        else:
             # Just dump everything? or summary?
             # For bulk without search, maybe we just list them? 
             # Or if --json is passed, return LIST of all analysis?
             if args.json:
                 results.append(miner.metadata)
             else:
                 print(f"Processed {miner.metadata['ID']}")

    if args.json:
        print(json.dumps(sorted(list(set(r["FilePath"] for r in results))), indent=2))

if __name__ == "__main__":
    main()