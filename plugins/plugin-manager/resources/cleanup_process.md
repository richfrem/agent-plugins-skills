# Plugin Synchronization & Cleanup Process

This document explains the logic used by `sync_with_inventory.py` to manage plugin lifecycles in consuming repositories. The goal is to keep vendor plugins up-to-date while protecting project-specific customizations.

![Process Diagram](cleanup_flow.mmd)

## Key Concepts

### 1. Vendor Inventory (The Source of Truth)
*   **Definition**: The complete list of plugins available from the upstream repository (`.vendor/agent-plugins-skills`).
*   **File**: `vendor-plugins-inventory.json`
*   **Analogy**: The "Menu" at a restaurant. It lists everything that *could* be installed.

### 2. Local Inventory (Current State)
*   **Definition**: The plugins currently installed in your project's `plugins/` directory.
*   **Analogy**: Your "Order". It lists what you have actually chosen to use.

## The Logic: Three States

The synchronization script compares the **Vendor Inventory** against your **Local Inventory** to determine one of three states for every plugin:

### Case A: Active Vendor Plugin
*   **Condition**: Plugin exists in **BOTH** Vendor and Local inventories.
*   **Meaning**: This is a standard vendor plugin that you are using.
*   **Action**: **UPDATE**. The script runs the bridge installer to ensure agent artifacts (in `.agent`, `.claude`, etc.) match the latest code.

### Case B: Project Specific Plugin (PROTECTED)
*   **Condition**: Plugin exists in **Local** but **NOT** in Vendor.
*   **Meaning**: This is a custom plugin you created for this specific project (or a vendor plugin you renamed).
*   **Action**: **PROTECT**. The script **ignores** this plugin during cleanup. It will NEVER delete your custom work.

### Case C: User Deleted Plugin (CLEANUP)
*   **Condition**: Plugin exists in **Vendor** but **NOT** in Local.
*   **Meaning**: The plugin is available from the vendor, but you (the user) have deleted the folder from `plugins/`. This signals an intent to remove it.
*   **Action**: **CLEANUP**. The script identifies this as a "Deleted Vendor Plugin" and safely removes its associated artifacts from agent directories to prevent clutter.

## The Cleanup Rules

The script follows strict safety rules to avoid accidental data loss:

1.  **Origin Check**: It only considers a plugin "Deleted" if it *originated* from the Vendor inventory.
2.  **Name Matching**: Cleanup targets are specific. It deletes files matching the pattern `{plugin_name}_*` in agent directories.
3.  **Safe Fallback**: If the Vendor Inventory file is missing, the cleanup logic is **skipped entirely** to prevent false positives.
