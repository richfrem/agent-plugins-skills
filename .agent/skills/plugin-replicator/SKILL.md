---
name: plugin-replicator
description: >
  Replicates, clones, or updates plugins from the central repository to
  other project repositories. Trigger when setting up a new project workspace
  or pulling the latest plugin source code into a consumer project.
allowed-tools: Bash, Write, Read
---

# Plugin Replicator

## Overview
This skill manages the synchronization of plugin source code between the central repository and other projects, ensuring tools are consistent across all workspaces.

## Usage

### 1. Replicate a Single Plugin
Install or update a specific plugin in another project.

```bash
# Copy mode (Default — for stable deployment)
python3 plugins/plugin-manager/scripts/plugin_replicator.py --plugin <plugin-name> --target <project-root>

# Link mode (Dev — changes reflect instantly)
python3 plugins/plugin-manager/scripts/plugin_replicator.py --plugin <plugin-name> --target <project-root> --link
```

**Example:**
```bash
python3 plugins/plugin-manager/scripts/plugin_replicator.py --plugin guardian-onboarding --target ../project-sanctuary --link
```

### 2. Bulk Replication
Replicate ALL plugins (or a subset) to a target project.

```bash
# Sync all plugins
python3 plugins/plugin-manager/scripts/bulk_replicator.py --target <project-root>

# Sync only specific plugins (glob filter)
python3 plugins/plugin-manager/scripts/bulk_replicator.py --target <project-root> --filter "investment-*"
```

## When to use
- **New Project Setup**: Populate a new project with the standard plugin toolkit.
- **Updates**: Pull the latest fixes from `agent-plugins-skills` into a consumer project.
- **Development**: Link plugins to work on them centrally while testing in another project context.
