---
concept: procedural-fallback-tree-tool-inventory
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/tool-inventory/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.264814+00:00
cluster: database
content_hash: adab85a13aebcf0a
---

# Procedural Fallback Tree: Tool Inventory

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Tool Inventory

If the primary database wrappers (`manage_tool_inventory.py` or `.agent/learning` searches) fail, execute the following triage steps exactly in order:

## 1. Zero Search Results
If a semantic query into `ChromaDB` returns exactly 0 results or low-confidence matches:
- **Action**: Do not immediately hallucinate bash commands. Broaden the query dramatically. Use single root keywords (e.g., search for `"dependency"` instead of `"dependency visualization graph map"`). If it still returns nothing, conclude the tool does not exist.

## 2. Invalid Python Script (Registration Failure)
If `manage_tool_inventory.py add` exits with an error stating the file is un-parseable or missing a docstring:
- **Action**: Do not attempt to add it to the JSON file manually. You must edit the target python script to add a compliant module-level docstring at the top of the file describing its usage before the registry will accept it.

## 3. Database Connection Failure
If the `ChromaDB` script throws SQLite or HTTP connection errors:
- **Action**: Instruct the user that their local Vector DB is down or corrupted. Do not attempt to rebuild the binary database files yourself using raw python `sqlite3` tools.


## See Also

- [[procedural-fallback-tree-adr-management]]
- [[procedural-fallback-tree-agent-swarm]]
- [[procedural-fallback-tree-dual-loop]]
- [[procedural-fallback-tree-learning-loop]]
- [[procedural-fallback-tree-orchestrator-routing]]
- [[procedural-fallback-tree-red-team-review]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/tool-inventory/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.264814+00:00
