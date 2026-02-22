---
name: spec-kitty-update
description: Update an existing Spec-Kitty workflow environment, refresh the templates from upstream sources, and redeploy the synchronized configurations to the active agent environment.
---

# Spec Kitty Update Skill

You are an active administrator for the **Spec-Driven Development** framework. Your job is to update the framework when the user requests it (e.g. they upgraded the `spec-kitty-cli` via pip), and re-deploy the updated slash-command workflows into the user's IDE.

## Execution Protocol

**CRITICAL RULE**: Do not simulate these steps. You must invoke the bash commands and read their outputs.

1. **Update the Repository Workflows**
   Run the CLI initialization command with the force update parameter to refresh existing `.windsurf/workflows` files with new templates:
   ```bash
   spec-kitty init . --ai windsurf --force
   ```
   *Note: Accept any confirmation prompts.*

2. **Synchronize Local Configurations**
   Convert the refreshed local workflows into distributable plugin components:
   ```bash
   python3 plugins/spec-kitty-plugin/skills/spec-kitty-agent/scripts/sync_configuration.py
   ```

3. **Deploy to IDE**
   Redeploy the modernized workflows directly into the user's Antigravity instance so they reflect the latest features:
   ```bash
   python3 plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/spec-kitty-plugin --target antigravity
   ```

4. **Confirmation**
   Inform the user that the update is complete. Mention that they must **Reload their Window** (or restart the agent session) to see any new `/spec-kitty` slash commands.
