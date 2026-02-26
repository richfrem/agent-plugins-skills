---
name: spec-kitty-init
description: Initialize the Spec-Kitty Spec-Driven Development framework within the current project repository and synchronize the resulting workflows into the IDE.
---

# Spec Kitty Init Skill

You are an active administrator for the **Spec-Driven Development** framework. Your job is to initialize the framework when the user requests it, and immediately deploy the generated slash-command workflows into the user's IDE so they can start working.

## Execution Protocol

**CRITICAL RULE**: Do not simulate these steps. You must invoke the bash commands and read their outputs.

1. **Initialize the Repository**
   Run the CLI initialization command:
   ```bash
   spec-kitty init . --ai windsurf
   ```
   *Note: This generates the core `.windsurf/workflows` files AND populates the templates in `.kittify/missions/` as well as `plugins/spec-kitty-plugin/templates`.*

2. **Run Master Synchronization**
   The `plugin-manager` orchestrates the replication of workflows and templates from `.kittify/missions` and `.windsurf/workflows` out to the individual agents. Run the master sync script:
   ```bash
   python3 plugins/plugin-manager/scripts/update_agent_system.py
   ```
   *Note: This 4-step process handles Kernel Sync, Core Workflow replication to `plugins/spec-kitty-plugin/templates`, Plugin Installation via plugin-mapper, and final Skill Distribution.*

4. **Confirmation**
   Inform the user that initialization is complete. Mention that they must **Reload their Window** (or restart the agent session) to see the new `/spec-kitty` slash commands.
