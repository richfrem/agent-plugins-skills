# Acceptance Criteria: Tool Inventory

The `tool-inventory` workflow MUST satisfy the following success metrics:

1. **Strict Electric Fence Adherence**: During tool discovery tasks, the agent must NEVER be caught executing `grep` or `find` across the `plugins/` directory to discover functionality. It must always pipe queries into the semantic database or JSON registry.
2. **Database Supremacy**: The agent must explicitly defer all CRUD (Create, Read, Update, Delete) operations on `tool_inventory.json` and the Chroma cache to the python CLI tools rather than performing manual file writes.
3. **Bind Before Action**: When a tool is found, the agent must mathematically demonstrate it has read the tool's usage file (`view_file` on lines 1-200) before attempting to execute the script in a bash terminal.
