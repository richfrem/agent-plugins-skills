# Plugin Manager

**The Deployment & Synchronization Hub for Your Plugin Ecosystem**

The **Plugin Manager** is the core toolkit for maintaining a healthy plugin ecosystem. It connects your project to the central vendor repository and ensures your local environment (Copilot, Gemini, Antigravity) is always in sync.

## 🚀 Quick Start

### 1. Initial Setup
New to this repo? Run these commands to get started:
1.  **Clone Vendor Repo**: `git clone ... .vendor/agent-plugins-skills`
2.  **Install Plugins**: Copy what you need to `plugins/`
3.  **Sync**: `python plugins/plugin-manager/scripts/sync_with_inventory.py`

👉 **[Read the Full Setup Guide](../../INIT_SETUP.md)**

### 2. Daily Commands
Use these Agent Commands to manage your plugins:

| Command | Description |
| :--- | :--- |
| `/plugin-manager_update` | **Update Everything**. Pulls latest code from vendor and syncs agents. |
| `/plugin-manager_install` | **Install New**. Adds a specific plugin (e.g., `agency-swarm`) from vendor. |
| `/plugin-manager_cleanup` | **Housekeeping**. Removes orphaned artifacts from deleted vendor plugins. |

---

## core Capabilities

### 1. Inventory Sync (The Brain)
**"Keep my agents in sync with my plugins folder."**

The `sync_with_inventory.py` script is the heart of the system. It:
*   **Generates Inventory**: Creates `local-plugins-inventory.json` (your Bill of Materials).
*   **Safe Cleanup**: Identifies if you deleted a vendor plugin and removes its traces from `.agent`, `.github`, etc.
*   **Protection**: *Never* deletes your custom, project-specific plugins.

👉 **[Read the Maintenance & Cleanup Guide](../../CLEANUP.md)**

### 2. Agent Bridge (The Adapter)
**"Make my plugins work in GitHub Copilot or Gemini."**

The **Agent Bridge** adapts your standard `.claude-plugin` structure into the specific formats required by other AI agents. It is automatically run by the Sync process.

*   **GitHub Copilot**: Converts commands to `.prompt.md` files in `.github/prompts/`.
*   **Gemini**: Wraps commands in TOML for `.gemini/commands`.
*   **Antigravity**: Adapts workflows for the `.agent/workflows` structure.

### 3. Plugin Updates (The Refresher)
**"I want to get the latest code for my plugins."**

The **Update from Vendor** script handles synchronizing your existing plugins with the vendor source.
```bash
python3 plugins/plugin-manager/scripts/update_from_vendor.py
```
This is safer than manual copying as it only updates what you have installed.

---

## Directory Structure
This tool expects the following standard layout in your project root:

```
my-repo/
├── .vendor/          # Hidden source of truth (central repo)
├── .github/          # Target for Copilot prompts
├── .gemini/          # Target for Gemini commands
├── .agent/           # Target for Antigravity workflows
└── plugins/          # Your active plugins
    ├── plugin-manager/  <-- This tool
    └── ...
```
