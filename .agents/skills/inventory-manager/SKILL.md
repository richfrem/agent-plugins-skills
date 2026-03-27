---
name: inventory-manager
description: Manage the master object inventory (master_object_collection.json). Features phase-based curation, health classification, and explicit source transparency routing.
disable-model-invocation: false
tier: 1
---

# Inventory Manager

## Overview

This skill manages the central registry of all system objects. It ensures the `master_object_collection.json` is perfectly synced.

## Inventory Health Classification
Before making changes, classify the current inventory state using this strict formula:
1. **Calculate Drift Age (H):** `Current Time - Last Modified Time` of `master_object_collection.json` in hours.
2. **Calculate Conflict Count (C):** Number of unmerged standard files or git conflicts.

Apply the classification:
- **GREEN (Healthy)**: If `(H < 24) AND (C == 0)`. Proceed with incremental updates.
- **YELLOW (Drifted)**: If `(H >= 24) AND (H < 168) AND (C < 5)`. Ask user for permission before bulk-updating.
- **RED (Corrupt)**: If `(H >= 168) OR (C >= 5)` or if the JSON is malformed. **HALT**. Alert user and recommend a full rebuild.

## Phase-Based Workflow Execution

### Phase 1: Discovery & Classification
Assess the health of the target directories and the `master_object_collection.json`. Run `curate_inventories.py` in dry-run mode if available. Classify as GREEN/YELLOW/RED.

### Phase 2: Action Execution (Script Decision Table)
Choose the appropriate script based on the task:
| Scenario | Action Required | Recommended Script (in `scripts/`) |
|----------|-----------------|-----------------------------------|
| Build from scratch | Need to generate new component registries | `build_component_registry.py` |
| Curate master | Merge all component registries into the master file | `curate_inventories.py` |
| Validate | Check integrity of the JSON against schema | `validate_inventory.py` |
| Search/Extract | Pull specific module trees | `extract_module.py` (if present) |

### Phase 3: Mandatory Self-Retrospective
After executing, explicitly run a check: did the script fail or succeed? If it failed due to an obvious bug, fix the Python script. If the instructions were confusing, document it.

## Output Report (Source Transparency)
Conclude your execution by declaring:
**Sources Checked:** [List of JSONs and directories scanned]
**Sources Unavailable:** [List of missing artifacts or read errors]
