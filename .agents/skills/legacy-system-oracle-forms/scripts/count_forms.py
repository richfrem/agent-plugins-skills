"""
plugins/legacy-system-oracle-forms/scripts/count_forms.py

Purpose: Counts total JUSTIN Forms from the inventory JSON.
Layer: Investigate / Utils
Used by: Reporting, Dashboard

Usage:
    python plugins/legacy-system-oracle-forms/scripts/count_forms.py
"""
import json

try:
    with open('legacy-system/reference-data/inventories/forms_and_reports_inventory.json', 'r') as f:
        data = json.load(f)
        
    justin_forms = [
        item for item in data 
        if item.get('APPLICATION', '').upper() == 'JUSTIN' and item.get('OBJECT_TYPE', '').upper() == 'FORM'
    ]
    
    print(f"Total JUSTIN Forms: {len(justin_forms)}")
    
except Exception as e:
    print(f"Error: {e}")
