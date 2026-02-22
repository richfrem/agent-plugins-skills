---
name: vector-db-init
description: Interactively initializes the Vector DB plugin. Installs the required pip dependencies (chromadb, langchain wrappers) and configures the vector_profiles.json for Native Python Server connections. Run this before attempting to use the vector-db-agent or vector-db-launch skills.
---

# Vector DB Initialization

The `vector-db-init` skill is an automated setup routine that prepares the environment for the Vector DBMS. 

## When to Use This
- When a user first installs the `vector-db` plugin.
- If the user complains that `chromadb` is not installed or `ModuleNotFoundError` is thrown.
- If the Vector DB profile is missing from `.agent/learning/vector_profiles.json`.

## Instructions for Agent

1. **Run the Initialization Script:**
   You must execute the interactive initialization script located at `scripts/init.py`.
   ```bash
   python3 plugins/vector-db/skills/vector-db-init/scripts/init.py
   ```

2. **Wait for Completion:** 
   The script will automatically run `pip install`, then prompt the user to select their deployment architecture (In-Process or Native Server). All settings are written to `.agent/learning/vector_profiles.json`.

3. **Verify:**
   After the script completes successfully, inform the user that their environment is ready, and they can now run the `vector-db-launch` skill to start the background server (if they chose Option 2).
