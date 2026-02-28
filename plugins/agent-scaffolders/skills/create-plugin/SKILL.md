---
name: create-plugin
description: Interactive initialization script that generates a compliant '.claude-plugin' directory structure and `plugin.json` manifest. Use when building a new plugin wrapper to distribute skills or agent logic.
disable-model-invocation: false
---

# Plugin Scaffold Generator

You are tasked with generating a new Agent Plugin boundary. Because we demand absolute determinism and compliance with Open Standards, you MUST use the internal CLI tool to scaffold the files.

## Execution Steps:

1. **Gather Requirements:**
   Ask the user for the name of the intended plugin. 

2. **Scaffold the Plugin:**
   You must execute the hidden deterministic `scaffold.py` script included in this plugin to guarantee perfect Open Standard compliance. Do not use standard `echo` or `mkdir` commands unless the script fails.
   
   Run the following bash command:
   ```bash
   python3 plugins/scripts/scaffold.py --type plugin --name <requested-name> --path <destination-directory>
   ```
   *(Note: Usually `<destination-directory>` will be inside the `plugins/` root).*

3. **Confirmation:**
   Print a success message indicating the plugin distribution wrapper has been created.
