# inventory-manager

Manages the master object inventory (`master_object_collection.json`). Features phase-based curation, health classification, and explicit source transparency routing.

## Workflows

| Command | Purpose |
|---|---|
| `/inventory-manager_curate-inventories` | Rebuild `master_object_collection.json` from all individual inventories |

## Scripts

| Script | Purpose |
|---|---|
| `build_master_collection.py` | Assemble all component inventories into the master JSON |
| `scan_forms_artifacts.py` | Scan the Forms source directory and register artifacts |
| `generate_forms_object_inventory.py` | Generate the Forms object inventory |
| `generate_pll_inventory.py` | Generate the PLL library inventory |
| `generate_reports_inventory.py` | Generate the Reports inventory |
| `generate_db_schema_inventory.py` | Generate the DB schema object inventory |
| `generate_applications_inventory.py` | Generate the Applications inventory |
| `audit_inventory.py` | Audit inventory completeness and flag gaps |
| `audit_scope_zombies.py` | Identify objects in scope that are no longer present on disk |
| `validate_counts.py` | Validate object counts against expected totals |
| `manage_missing_objects.py` | Track and manage objects flagged as missing |
| `manage_data_inventory.py` | Manage reference data inventory entries |
| `check_pll_usage.py` | Check which PLLs are referenced by Forms |
| `update_pll_status.py` | Update PLL modernization status flags |
| `process_relationship_csv.py` | Import relationship data from CSV exports |
| `remove_modernization_tracks.py` | Strip modernization tracking fields from inventory |
| `regenerate_all_inventories.py` | Full rebuild of all component inventories |

## Inventory Health States

| State | Condition | Action |
|---|---|---|
| GREEN | Age < 24h, no conflicts | Proceed normally |
| YELLOW | 24h–168h old, < 5 conflicts | Request user confirmation before bulk update |
| RED | Age ≥ 168h or ≥ 5 conflicts | Halt — alert user, recommend full rebuild |
