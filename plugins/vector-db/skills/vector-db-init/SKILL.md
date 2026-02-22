---
name: vector-db-init
description: Interactively initializes the Vector DB plugin. Installs the required pip dependencies (chromadb, langchain wrappers) and configures the user's .env file for Native Python Server connections. Run this before attempting to use the vector-db-agent or vector-db-launch skills.
---

# Vector DB Initialization

The `vector-db-init` skill is an automated setup routine that prepares the environment for the Vector DBMS. 

## When to Use This
- When a user first installs the `vector-db` plugin.
- If the user complains that `chromadb` is not installed or `ModuleNotFoundError` is thrown.
- If the Vector DB configuration is missing from `.env`.

## Instructions for Agent

1. **Run the Initialization Script:**
   You must execute the interactive initialization script located at `scripts/init.py`.
   ```bash
   python3 plugins/vector-db/skills/vector-db-init/scripts/init.py
   ```

2. **Wait for Completion:** 
   The script will automatically run `pip install`, scan the `.env` file, and append the necessary `CHROMA_HOST` and `CHROMA_PORT` variables if they do not exist.

3. **Verify:**
   After the script completes successfully, inform the user that their environment is ready, and they can now run the `vector-db-launch` skill to start the background server.
