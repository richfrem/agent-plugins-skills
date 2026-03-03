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

## Execution Protocol

Do not immediately generate bash commands. Instead, operate as an interactive assistant using the following human-in-the-loop phases:

### Phase 1: Guided Discovery Interview
When the user invokes this skill without specific arguments, begin by asking scoping questions:
1. **Plugin Target:** "Which plugin do you want to replicate, or do you want to bulk sync all of them?"
2. **Destination Path:** "What is the absolute path to the target project repository?" (Suggest their current working directory as a smart default unless specified otherwise).
3. **Replication Mode:** "Do you want to perform a stable **Copy** (for independent deployment) or a dynamic **Link** (for central development)?"

### Phase 2: Recap-Before-Execute
Once variables are gathered, explicitly state what you are about to do and ask for confirmation. Use this format:

```markdown
### Proposed Replication Task
- **Plugin(s)**: [Name or ALL]
- **Target Project**: `[Path]`
- **Mode**: [Copy / Link]

> Does this look correct? I will generate the exact replication commands once you confirm.
```

### Phase 3: Command Generation
Wait for the user's explicit confirmation (`yes`, `looks good`, `ok`). Once confirmed, generate the exact bash command according to their choices:

#### For Single Plugins
```bash
# Copy mode (Default — for stable deployment)
python3 plugins/plugin-manager/scripts/plugin_replicator.py --plugin <plugin-name> --target <project-root>

# Link mode (Dev — changes reflect instantly)
python3 plugins/plugin-manager/scripts/plugin_replicator.py --plugin <plugin-name> --target <project-root> --link
```

#### For Bulk Replication
```bash
# Sync all plugins
python3 plugins/plugin-manager/scripts/bulk_replicator.py --target <project-root>

# Sync only specific plugins (glob filter)
python3 plugins/plugin-manager/scripts/bulk_replicator.py --target <project-root> --filter "<pattern>"
```

## When to use
- **New Project Setup**: Populate a new project with the standard plugin toolkit.
- **Updates**: Pull the latest fixes from `agent-plugins-skills` into a consumer project.
- **Development**: Link plugins to work on them centrally while testing in another project context.
