# Acceptance Criteria: Tool Inventory

## Objective
Ensure the Agent can correctly interact with the `tool_inventory.json` registry.

## Scenario 1: Search the Registry
- **Setup**: Agent uses the semantic search prompt.
- **Action**: The Agent executes `tool_chroma.py search` (via `rlm-factory`).
- **Validation**: The Agent successfully retrieves a list of relevant scripts from the semantic index.

## Scenario 2: Register a New Tool
- **Setup**: Agent identifies a script that is missing from `tool_inventory.json`.
- **Action**: The Agent runs `manage_tool_inventory.py add --path [path]`.
- **Validation**: The tool is successfully added to the registry JSON file.

## Scenario 3: Agentic Distillation Delegation
- **Setup**: An internal script is updated and needs summarization.
- **Action**: The Agent delegates summarization to `distiller.py` located in `rlm-factory/skills/rlm-curator/scripts/`.
- **Validation**: The summary is updated in the semantic ledger.
