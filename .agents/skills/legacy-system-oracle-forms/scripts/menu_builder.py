#!/usr/bin/env python3
"""
Menu Builder Module - Layer 1+2 Merger (Core Logic)
====================================================

Purpose:
    Merges MMB structure (Layer 1) with MenuConfig role rules (Layer 2) to produce
    React-consumable menu configuration files.

Inputs:
    - legacy-system/reference-data/inventories/mmb_structure.json (Layer 1: Menu structure)
    - legacy-system/reference-data/collections/menuconfig/MenuConfig Menu Item Rules.csv (Layer 2: Role rules)

Outputs:
    - legacy-system/reference-data/inventories/menu_inventory.json (Master inventory)
    - sandbox/ui/public/config/menus/{APP}_Menu.json (Per-app React configs)

Key Classes:
    - MenuBuilder: Main class with methods for loading, merging, and exporting

Key Methods:
    - load_static_definitions(): Loads Layer 1 (MMB structure)
    - build_menu_items(): Recursively builds menu tree with role overrides
    - export_application_menu(): Generates per-app JSON for React

Processing Logic:
    1. Parse MMB structure to get menu hierarchy and commands
    2. Parse MenuConfig CSV to get role-based visibility/enablement rules
    3. For each menu item, compute default roles and form-specific overrides
    4. Build nested tree structure with children
    5. Export as JSON for React consumption

Known Issues:
    - MenuConfig uses hierarchical paths (e.g., "ACTION_MENU.ADMIN_MENU.FORM0000")
    - Built-in items (Save, Exit) are NOT in MMB, may need hardcoding
    - <New_Item> labels are placeholders that UI must filter out

Used By:
    - menu_inventory_generator.py (CLI Script)
    - manifest_manager.py (Main CLI: `python plugins/legacy system/legacy-system-oracle-forms/skills/legacy-system-oracle-forms/scripts/menu_miner.py --app AppFour`)

Related:
    - ADR-0002: Menu Configuration as Code
    - extract_mmb_structure.py: Generates Layer 1 input
    
"""

import csv
import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
# Adjust paths assuming this file is in tools/business-rule-extraction/scripts/
SCRIPT_DIR = Path(__file__).parent.resolve()

def _find_project_root() -> Path:
    """Walk up from script to find project root (sentinel: skills-lock.json or .git)."""
    for parent in SCRIPT_DIR.parents:
        if (parent / 'skills-lock.json').exists() or (parent / '.git').exists():
            return parent
    raise RuntimeError(f"Could not find project root from {__file__}")

PROJECT_ROOT = _find_project_root()
STATIC_DEF_PATH = PROJECT_ROOT / "legacy-system" / "reference-data" / "inventories" / "mmb_structure.json"
CSV_PATH = PROJECT_ROOT / "legacy-system" / "reference-data" / "collections" / "menuconfig" / "MenuConfig Menu Item Rules.csv"
INVENTORY_PATH = PROJECT_ROOT / "legacy-system" / "reference-data" / "inventories" / "menu_inventory.json"


class MenuBuilder:
    def __init__(self, static_def_path=None, csv_path=None):
        self.static_def_path = static_def_path or STATIC_DEF_PATH
        self.csv_path = csv_path or CSV_PATH
        self.static_menus = None
        
    def load_inventory(self, path=None):
        """Load the generated inventory JSON."""
        p = path or INVENTORY_PATH
        if not p.exists():
            return {"applications": {}}
        with open(p, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_static_definitions(self):
        """Load the XML-mined menu structure."""
        if not self.static_def_path.exists():
            raise FileNotFoundError(f"Static definitions not found at {self.static_def_path}. Run extract_mmb_structure.py first.")
            
        with open(self.static_def_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Use the raw MMB structure extracted by extract_mmb_structure.py
        self.static_menus = data.get('raw_menus', {})
        return self.static_menus

    def compute_roles_and_overrides(self, item_key, item_form_data):
        """
        Determine default roles using Majority Rule (Mode).
        Finds the most common role configuration across all forms.
        """
        if not item_form_data:
            return [], [], {}

        all_forms = list(item_form_data.keys())
        if not all_forms:
            return [], [], {}

        # 1. Collect all variations
        # usage_map: tuple(visible_tuple, enabled_tuple) -> count
        usage_counts = defaultdict(int)
        
        for d in item_form_data.values():
            vis_tuple = tuple(sorted(list(d['visible'])))
            ena_tuple = tuple(sorted(list(d['enabled'])))
            usage_counts[(vis_tuple, ena_tuple)] += 1
            
        # 2. Find the Mode (Most common configuration)
        # Sort by count descending, then by content for stability
        sorted_configs = sorted(usage_counts.items(), key=lambda x: (-x[1], x[0]))
        (common_vis_tuple, common_ena_tuple), count = sorted_configs[0]
        
        common_visible = list(common_vis_tuple)
        common_enabled = list(common_ena_tuple)
        
        # 3. Compute overrides (Only those differing from Mode)
        overrides = {}
        for form in all_forms:
            form_vis = sorted(list(item_form_data[form]['visible']))
            form_ena = sorted(list(item_form_data[form]['enabled']))
            
            if form_vis != common_visible or form_ena != common_enabled:
                overrides[form] = {
                    "visible": form_vis,
                    "enabled": form_ena
                }

        return common_visible, common_enabled, overrides

    def build_menu_items(self, menu_name, app_data, processed_menus=None):
        """
        Recursively build menu items for a specific menu.
        Returns a list of dicts conforming to MenuItem schema.
        """
        if self.static_menus is None:
            self.load_static_definitions()
            
        if processed_menus is None:
            processed_menus = set()
        
        # Prevent infinite loops
        if menu_name in processed_menus:
            return []
        processed_menus.add(menu_name)

        if menu_name not in self.static_menus:
            # DEBUG
            if menu_name == "ACTION_MENU":
                print(f"DEBUG: ACTION_MENU not found in static_menus!")
            return []
            
        # DEBUG
        if menu_name == "ACTION_MENU":
            print(f"DEBUG: Processing ACTION_MENU with {len(self.static_menus[menu_name])} items from MMB.")

        nodes = []
        for item in self.static_menus[menu_name]:
            # Schema match: mmb_structure.json uses 'id' instead of 'name'
            item_name = item.get('id') or item.get('name')
            
            # DEBUG
            if menu_name == "ACTION_MENU":
                print(f"DEBUG:   > Finding item: {item_name} ({item.get('label')})")

            item_key = f"{menu_name}.{item_name}"
            item_form_data = app_data.get(item_key, {})
            
            default_visible, default_enabled, overrides = self.compute_roles_and_overrides(item_key, item_form_data)
            
            # Optimization: Remove redundant overrides (Reduce Bloat)
            clean_overrides = {}
            # Ensure defaults are lists before set conversion (just in case)
            def_vis_list = default_visible if isinstance(default_visible, list) else []
            def_ena_list = default_enabled if isinstance(default_enabled, list) else []
            
            # Semantic Optimization: If PUBLIC is present, it supersedes all others
            def normalize_roles(roles):
                if not roles: return set()
                s = set(roles)
                if "PUBLIC" in s:
                    return {"PUBLIC"}
                return s

            def_vis_set = normalize_roles(def_vis_list)
            def_ena_set = normalize_roles(def_ena_list)
            
            for form_id, rule in overrides.items():
                minimized_rule = {}
                
                ov_vis = normalize_roles(rule.get('visible', []))
                ov_ena = normalize_roles(rule.get('enabled', []))
                
                # Only include keys that differ from default
                if ov_vis != def_vis_set:
                    minimized_rule['visible'] = rule.get('visible', [])
                if ov_ena != def_ena_set:
                    minimized_rule['enabled'] = rule.get('enabled', [])
                
                if minimized_rule:
                    clean_overrides[form_id] = minimized_rule
            
            # Construct MenuItem
            node = {
                "id": item_name,
                "label": item['label'] or "",  # Ensure string
                "itemType": "MenuItem", # Default
                "roles": {
                    "visible": default_visible,
                    "enabled": default_enabled
                }
            }
            
            # Map specific types if known
            if item.get('type') == 'Separator':
                node['itemType'] = 'Separator'
            
            # Command/Action mapping
            if item.get('commandType'):
                 node['commandType'] = item['commandType']
            
            if item.get('command'):
                 node['command'] = item['command']
                 # Action is the primary command text
                 node['action'] = item['command']
            
            if clean_overrides:
                node["overrides"] = clean_overrides

            # Recursion for Submenus
            # Schema match: mmb_structure.json uses 'submenu_ref'
            submenu_name = item.get('submenu_ref') or item.get('subMenu')
            if submenu_name:
                children = self.build_menu_items(submenu_name, app_data, set(processed_menus))
                if children:
                    node["children"] = children
                    node["itemType"] = "Submenu"
            
            nodes.append(node)
            
        return nodes

    def filter_sections(self, sections, role, form=None):
        """
        Filters the sections and items.
        If role is provided, pre-calculates visibility/enablement (Server-side filtering).
        If role is None, exports full structure with role metadata (Client-side filtering).
        """
        filtered_sections = []
        for section in sections:
            
            # Recursive item filter
            def filter_items(items):
                filtered = []
                for item in items:
                    # 1. Resolve Overrides
                    visible_roles = item.get("roles", {}).get("visible", [])
                    enabled_roles = item.get("roles", {}).get("enabled", [])
                    
                    if form and "overrides" in item and form in item["overrides"]:
                         if "visible" in item["overrides"][form]:
                             visible_roles = item["overrides"][form]["visible"]
                         if "enabled" in item["overrides"][form]:
                             enabled_roles = item["overrides"][form]["enabled"]
                    
                    # 2. Filtering Logic
                    should_include = False
                    is_visible_static = True
                    is_enabled_static = True
                    roles_metadata = None

                    if role:
                        # Server-side Filtering
                        if not visible_roles:
                            # Strict: Hidden if empty
                            pass 
                        elif role in visible_roles:
                             should_include = True
                             is_visible_static = True
                        
                        if should_include:
                            if not enabled_roles:
                                is_enabled_static = False
                            else:
                                is_enabled_static = role in enabled_roles
                    else:
                        # Client-side Export (Include All)
                        should_include = True
                        roles_metadata = {
                            "visible": visible_roles,
                            "enabled": enabled_roles
                        }
                    
                    if should_include:
                         # 3. Construct Item
                         new_item = {
                             "id": item["id"],
                             "label": item["label"],
                             "itemType": item.get("itemType", "MenuItem"),
                             "action": item.get("action"),
                             "enabled": is_enabled_static,
                             "visible": is_visible_static
                         }
                         
                         if roles_metadata:
                             new_item["roles"] = roles_metadata
                         
                         # Recurse children
                         children = item.get("children")
                         if children:
                             filtered_children = filter_items(children)
                             # Only include submenu if children exist (or if we are raw exporting submenus)
                             # For raw export, we might want to keep empty submenus? Let's keep consistent behavior.
                             if filtered_children:
                                 new_item["children"] = filtered_children
                         
                         filtered.append(new_item)
                return filtered

            # Filter items in this section
            filtered_root_items = filter_items(section.get("items", []))
            
            if filtered_root_items:
                new_section = {
                    "id": section["id"],
                    "name": section["name"],
                    "sectionType": section["sectionType"],
                    "items": filtered_root_items
                }
                filtered_sections.append(new_section)
                
        return filtered_sections

    def export_for_react(self, form_id, output_dir, role=None):
        """
        Exports a React-compatible menu configuration for a specific form.
        """
        inventory = self.load_inventory()
        if not inventory:
            raise ValueError("Menu inventory not found. Run 'menu rebuild' first.")
            
        app_code = form_id[:3].upper()
        if app_code not in inventory.get("applications", {}):
            raise ValueError(f"Application '{app_code}' not found in inventory.")
            
        sections = inventory["applications"][app_code].get("sections", [])
        
        # Filter
        # If role is None, we might export everything but marked visible=False?
        # For now, strict filtering as per CLI requirements.
        if role:
             filtered = self.filter_sections(sections, role, form_id)
        else:
             # If no role, export everything but maybe simplified?
             # For export to React static file, we likely prefer to include logic 
             # OR we export a role-specific slice. 
             # For now, rely on filter_sections strictness (empty if no role match).
             filtered = self.filter_sections(sections, role, form_id)

        # Output
        out_path = Path(output_dir)
        os.makedirs(out_path, exist_ok=True)
        filename = f"{app_code}_{form_id}.json"
        full_path = out_path / filename
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump({"sections": filtered}, f, indent=2)
            
        return str(full_path)

    def enable_menu_item(self, menu_def, item_id, role, form_id=None):
        """
        Method 2: Enable a menu item for a specific role (and optional form override).
        Modifies the passed menu_def structure in place.
        """
        # Find the item
        target_item = None
        for menu in menu_def["menus"]:
            for item in menu["items"]:
                if item["id"] == item_id:
                    target_item = item
                    break
            if target_item: break
            
        if not target_item:
            # print(f"⚠️ Warning: Item {item_id} not found in base definition.")
            return

        if form_id:
            # Handle Form Override
            # PRUNING LOGIC: If role is already in Base Enabled, do not add to Override
            # This prevents redundancy (e.g. Help enabled for Public globally AND in form override)
            if role in target_item.get("enabled", []):
                return

            if "overrides" not in target_item:
                target_item["overrides"] = {}
            if form_id not in target_item["overrides"]:
                target_item["overrides"][form_id] = {"enabled": []}
            
            if role not in target_item["overrides"][form_id]["enabled"]:
                 target_item["overrides"][form_id]["enabled"].append(role)
                 target_item["overrides"][form_id]["enabled"].sort()
        else:
            # Global/Base Role
            if role not in target_item["enabled"]:
                target_item["enabled"].append(role)
                target_item["enabled"].sort()

    def enable_menu(self, menu_def, menu_id, role, form_id=None):
        """
        Method 4: Enable a parent menu for a specific role.
        """
        target_menu = None
        for menu in menu_def["menus"]:
            if menu["id"] == menu_id:
                target_menu = menu
                break
        
        if not target_menu: return

        if form_id:
            # PRUNING LOGIC
            if role in target_menu.get("enabled", []):
                return

            if "overrides" not in target_menu:
                target_menu["overrides"] = {}
            if form_id not in target_menu["overrides"]:
                target_menu["overrides"][form_id] = {"enabled": []}
            
            if role not in target_menu["overrides"][form_id]["enabled"]:
                 target_menu["overrides"][form_id]["enabled"].append(role)
                 target_menu["overrides"][form_id]["enabled"].sort()
        else:
            if role not in target_menu["enabled"]:
                target_menu["enabled"].append(role)
                target_menu["enabled"].sort()

    def populate_application_roles(self, app_code, output_dir):
        """
        Method 3: Iterates Inventory and populates the Base Menu with roles.
        Generates [APP]_Menu_Populated.json.
        Phase 3: Automatically enables parent menus if any child item is enabled.
        """
        # 1. Generate Base (Empty) Structure first
        base_path = self.generate_application_base_menu_system(app_code, output_dir)
        with open(base_path, 'r', encoding='utf-8') as f:
            menu_def = json.load(f)

        # 2. Iterate Inventory to find rules
        inventory = self.load_inventory()
        sections = inventory["applications"][app_code].get("sections", [])

        print(f"🔨 Populating roles for {app_code}...")
        
        # Track all roles/forms encountered to drive Phase 3
        all_roles = set()
        all_forms = set()

        for section in sections:
            for item in section.get("items", []):
                # Check Global Enabled
                item_roles = item.get("roles", {})
                global_enabled = item_roles.get("enabled", [])
                
                for role in global_enabled:
                    self.enable_menu_item(menu_def, item["id"], role)
                    all_roles.add(role)
                
                # Check Overrides
                overrides = item.get("overrides", {})
                for form_id, rule in overrides.items():
                    form_enabled = rule.get("enabled", [])
                    if form_enabled:
                        all_forms.add(form_id)
                    for role in form_enabled:
                        self.enable_menu_item(menu_def, item["id"], role, form_id)
                        all_roles.add(role)

        # Phase 3: Parent Menu Enablement
        # For each menu, for each role (global + forms), check if any child is enabled.
        print(f"   > Post-processing parent menu visibility ({len(all_roles)} roles)...")
        
        for menu in menu_def["menus"]:
            # 3a. Check Global Roles
            for role in all_roles:
                has_enabled = False
                for item in menu["items"]:
                    if role in item.get("enabled", []):
                        has_enabled = True
                        break
                
                if has_enabled:
                    self.enable_menu(menu_def, menu["id"], role)
            
            # 3b. Check Form Overrides
            for form_id in all_forms:
                for role in all_roles:
                    has_enabled = False
                    for item in menu["items"]:
                        effective_enabled = item.get("enabled", [])
                        # Check override
                        if "overrides" in item and form_id in item["overrides"]:
                            effective_enabled = item["overrides"][form_id].get("enabled", [])
                        
                        if role in effective_enabled:
                            has_enabled = True
                            break
                    
                    if has_enabled:
                        self.enable_menu(menu_def, menu["id"], role, form_id)

        def optimize_roles(node_list):
            """
            Minimization Rule: If 'PUBLIC' is in the allowed list, remove all other roles.
            """
            for node in node_list:
                # Optimize node enabled list
                if "enabled" in node and "PUBLIC" in node["enabled"]:
                    node["enabled"] = ["PUBLIC"]
                
                # Recurse
                if "items" in node:
                    optimize_roles(node["items"])
                if "children" in node:
                    optimize_roles(node["children"])

        # 4. Split & Save Strategy
        # Separate Form Overrides from Application Core
        forms_dir = Path(output_dir).parent / "forms"
        os.makedirs(forms_dir, exist_ok=True)
        
        form_configs = defaultdict(lambda: {"overrides": {}})
        
        def extract_overrides(node_list):
            for node in node_list:
                # Extract Overrides
                if "overrides" in node:
                    for form_id, rules in node["overrides"].items():
                        # Optimize Override Lists too
                        if "enabled" in rules and "PUBLIC" in rules["enabled"]:
                            rules["enabled"] = ["PUBLIC"]

                        # Structure: form_config[form_id]["overrides"][item_id] = rules
                        if node["id"] not in form_configs[form_id]["overrides"]:
                             form_configs[form_id]["overrides"][node["id"]] = rules
                    
                    # Remove from Core
                    del node["overrides"]
                
                # Recurse
                if "items" in node: # Menu/Section
                    extract_overrides(node["items"])
                if "children" in node: # Submenu
                    extract_overrides(node["children"])

        print("   > Optimizing role lists (Core)...")
        optimize_roles(menu_def["menus"])

        print("   > Extracting form-specific overrides...")
        extract_overrides(menu_def["menus"])
        
        # Save Form Files
        saved_forms = 0
        for form_id, config in form_configs.items():
            form_path = forms_dir / f"{form_id}.json"
            # Add metadata
            final_config = {
                "formId": form_id,
                "overrides": config["overrides"]
            }
            with open(form_path, "w", encoding="utf-8") as f:
                json.dump(final_config, f, indent=2)
            saved_forms += 1
            
        print(f"   > Saved {saved_forms} form configuration files to {forms_dir}")

        # 5. Output Core Collection
        out_path = Path(output_dir)
        filename = f"{app_code}_Menu_Collection.json"
        full_path = out_path / filename
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(menu_def, f, indent=2)
            
        print(f"✅ Generated Core Menu Collection: {filename}")
        return str(full_path)

    def export_application_menu(self, app_code, output_dir):
        """
        Exports the main application menu (e.g. APP2_Menu.json).
        """
        inventory = self.load_inventory()
        if not inventory:
            # Try to build if missing
            inventory = self.build_full_inventory()
            
        if app_code not in inventory.get("applications", {}):
            print(f"⚠️ App {app_code} not found in inventory.")
            return

        sections = inventory["applications"][app_code].get("sections", [])
        
        out_path = Path(output_dir)
        os.makedirs(out_path, exist_ok=True)
        filename = f"{app_code}_Menu.json"
        full_path = out_path / filename
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump({"sections": sections}, f, indent=2)
        
        print(f"✅ Exported {filename}")
        return str(full_path)

    def apply_default_enablements(self, menu_def, app_code):
        """
        Enables specific items for ALL users (["PUBLIC"]) by default.
        Reads from menu_defaults.json.
        """
        # Load Defaults Configuration
        defaults_path = Path(__file__).parent / "menu_defaults.json"
        
        target_ids = set()
        if defaults_path.exists():
            try:
                with open(defaults_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                # Get app-specific defaults or fallback
                if app_code in config:
                    target_ids.update(config[app_code])
                else:
                    target_ids.update(config.get("DEFAULT", []))
            except Exception as e:
                print(f"⚠️ Error loading menu_defaults.json: {e}")
        else:
            print("⚠️ menu_defaults.json not found. Using empty defaults.")

        if not target_ids:
            return

        for menu in menu_def["menus"]:
            has_enabled_child = False
            for item in menu["items"]:
                if item["id"] in target_ids:
                    item["enabled"] = ["PUBLIC"]
                    has_enabled_child = True
            
            # If parent needs enabling because query methods check parents
            # Force enable parents for these defaults
            if has_enabled_child:
                if "PUBLIC" not in menu["enabled"]:
                    menu["enabled"].append("PUBLIC")

    def generate_application_base_menu_system(self, app_code, output_dir):
        """
        Method 1: Generate Base Menu Collection.
        Structure: Menus -> Items -> enabled: [] (Strictly empty).
        Method 1a: Apply Defaults (Help/Action enabled for all).
        This serves as the foundational layer.
        """
        inventory = self.load_inventory()
        if not inventory:
            inventory = self.build_full_inventory()
            
        if app_code not in inventory.get("applications", {}):
            print(f"⚠️ App {app_code} not found in inventory.")
            return

        sections = inventory["applications"][app_code].get("sections", [])
        
        base_menus = []
        
        for section in sections:
            menu_def = {
                "id": section["id"],
                "label": section["name"],
                "enabled": [], # Phase 3 Prep: Parent menus need enabled lists too
                "items": []
            }
            
            for item in section.get("items", []):
                # Strict Base Initialization: Always empty enabled list
                proto_item = {
                    "id": item["id"],
                    "label": item["label"],
                    "enabled": []
                }
                menu_def["items"].append(proto_item)
            
            base_menus.append(menu_def)
            
        output = {
            "application": app_code,
            "menus": base_menus
        }
        
        # Apply Global Defaults
        self.apply_default_enablements(output, app_code)
        
        out_path = Path(output_dir)
        os.makedirs(out_path, exist_ok=True)
        filename = f"{app_code}_Menu_Base.json"
        full_path = out_path / filename
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        
        print(f"✅ Generated Base Menu: {filename}")
        return str(full_path)

    d
# ------------------------------------------------------------------
# Functional Wrappers for CLI compatibility
# ------------------------------------------------------------------

def build_menu_inventory(csv_rows=None):
    # Wrapper compatible with CLI if we passed rows, but cleaner to use class
    mb = MenuBuilder()
    return mb.build_full_inventory()

def save_inventory(inventory, path=None):
    target = path or INVENTORY_PATH
    os.makedirs(target.parent, exist_ok=True)
    with open(target, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, indent=2)
    return target


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Menu Builder - Generate React menu configurations")
    parser.add_argument("--build", action="store_true", help="Build full menu inventory from MenuConfig + MMB")
    parser.add_argument("--export", metavar="APP", help="Export menu JSON for a specific app (e.g., AppFour)")
    parser.add_argument("--output", metavar="DIR", help="Output directory for exported menu JSON")
    parser.add_argument("--base", action="store_true", help="Generate Base Menu Collection (Method 1)")
    parser.add_argument("--populate", action="store_true", help="Populate Base Menu with Roles (Method 3)")
    parser.add_argument("--all", action="store_true", help="Export menus for all applications")
    
    args = parser.parse_args()
    
    builder = MenuBuilder()
    
    if args.build or args.export or args.all:
        # Build inventory first
        print("🔨 Building menu inventory from MenuConfig + MMB...")
        inventory = builder.build_full_inventory()
        save_inventory(inventory)
        print(f"✅ Saved inventory to {INVENTORY_PATH}")
    
    output_dir = args.output or str(PROJECT_ROOT / "sandbox" / "ui" / "public" / "config" / "menus")
    
    if args.export:
        builder.export_application_menu(args.export, output_dir)
        # Also generate base menu if requested
        if args.base:
            builder.generate_application_base_menu_system(args.export, output_dir)
        # Populated menu logic (Method 3)
        if args.populate:
            builder.populate_application_roles(args.export, output_dir)
    
    if args.all:
        inventory = builder.load_inventory()
        for app_code in inventory.get("applications", {}):
            builder.export_application_menu(app_code, output_dir)
            if args.base:
                builder.generate_application_base_menu_system(app_code, output_dir)
            if args.populate:
                builder.populate_application_roles(app_code, output_dir)
        print(f"✅ Exported all application menus to {output_dir}")
    
    if not (args.build or args.export or args.all):
        parser.print_help()

