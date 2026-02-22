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
   *Note: This generates the core `.windsurf/workflows` files.*

2. **Synchronize Local Configurations**
   Convert the generated local workflows into distributable plugin components:
   ```bash
   python3 plugins/spec-kitty-plugin/skills/spec-kitty-agent/scripts/sync_configuration.py
   ```

3. **Deploy to IDE**
   Deploy the modernized workflows directly into the user's Antigravity instance so they appear as active slash commands:
   ```bash
   python3 plugins/plugin-mapper/skills/agent-bridge/scripts/bridge_installer.py --plugin plugins/spec-kitty-plugin --target antigravity
   ```

4. **Confirmation**
   Inform the user that initialization is complete. Mention that they must **Reload their Window** (or restart the agent session) to see the new `/spec-kitty` slash commands.
