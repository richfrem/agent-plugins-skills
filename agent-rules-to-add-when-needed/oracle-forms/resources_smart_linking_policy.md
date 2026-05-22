# Standard: Smart Linking Syntax

## 1. Objective
To maintain a consistent, machine-readable linking structure that allows the RLM and visualizer to navigate the knowledge graph.

## 2. Syntax Rules
- **Form Reference**: `[FormID] (Reference Missing: overview)` `[[xml-md]]` `[[xml]]`
- **Role Reference**: `[ROLE_NAME] (Reference Missing: role.md)`
- **File Reference**: `[Filename] (Reference Missing: path)`

## 3. Automation
- **Enrichment Script**: `scripts/documentation/enrich_links_v2.py`
    - Parses `(Reference Missing: ...)` markers.
    - Resolves them against `master_object_collection.json`.
    - Updates the file with valid relative links.
- **Source Link Script**: `scripts/documentation/find_source_links.py` creates the initial block.

## 4. Usage
- **ALWAYS** use the script to generate links initially.
- **NEVER** manually create relative paths unless you are 100% sure of the target location.
- **VERIFY** target exists before linking (e.g., `ls path/to/target`).
- **ALWAYS** run the enrichment script after editing a file to fix broken/missing links.
