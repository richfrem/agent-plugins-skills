---
description: Update tool inventories, RLM cache, and associated artifacts after creating or modifying tools.
tier: 2
track: Curate
inputs:
  - ToolPath: Path to the new or modified tool (e.g., tools/retrieve/bundler/validate.py)
---

# Workflow: Tool Update

> **Purpose:** Register new or modified tools in the discovery system so future LLM sessions can find them.

## Pre-Requisites
- Tool script exists and follows `.agent/rules/coding_conventions_policy.md` (proper headers)
- Virtual environment active: `source .venv/bin/activate`

---

## Step 1: Register Tool in Inventory

### Option A: CLI (Automated)
// turbo
```bash
python3 plugins/tool-inventory/scripts/manage_tool_inventory.py add --path "[ToolPath]"
```

### Option B: Manual Edit (For complex entries)
Edit `tools/tool_inventory.json` directly, adding an entry like:
```json
{
  "name": "validate.py",
  "path": "tools/retrieve/bundler/validate.py",
  "description": "Validates manifest files against schema. Checks required fields, path traversal, and legacy format warnings.",
  "original_path": "new-creation",
  "decision": "keep",
  "header_style": "extended",
  "last_updated": "2026-02-01T10:00:00.000000",
  "compliance_status": "compliant",
  "category": "bundler"
}
```

**Expected Output:** Tool entry exists in `tools/tool_inventory.json`

---

## Step 2: Update RLM Cache

### Option A: CLI (Automated)
The inventory manager auto-triggers RLM distillation. To run manually:
// turbo
```bash
python3 plugins/rlm-factory/scripts/distiller.py --file "[ToolPath]" --type tool
```

### Option B: Manual Edit (For precise control)
Edit `.agent/learning/rlm_tool_cache.json` directly, adding an entry like:
```json
"tools/retrieve/bundler/validate.py": {
  "hash": "new_validate_2026",
  "summarized_at": "2026-02-01T10:00:00.000000",
  "summary": "{\n  \"purpose\": \"Validates manifest files against schema...\",\n  \"layer\": \"Retrieve / Bundler\",\n  \"usage\": [\"python tools/retrieve/bundler/validate.py manifest.json\"],\n  \"args\": [\"manifest: Path to manifest\", \"--all-base\", \"--check-index\"],\n  \"inputs\": [\"Manifest JSON files\"],\n  \"outputs\": [\"Validation report\", \"Exit code 0/1\"],\n  \"dependencies\": [\"file-manifest-schema.json\"],\n  \"consumed_by\": [\"/bundle-manage\", \"CI/CD\"],\n  \"key_functions\": [\"validate_manifest()\", \"validate_index()\"]\n}"
}
```

**Expected Output:** Entry exists in `.agent/learning/rlm_tool_cache.json`

---

## Step 3: Generate Markdown Inventory
Regenerate `tools/TOOL_INVENTORY.md` for human readability:
// turbo
```bash
python3 plugins/tool-inventory/scripts/manage_tool_inventory.py generate --output tools/TOOL_INVENTORY.md
```

**Expected Output:** `✅ Generated Markdown: tools/TOOL_INVENTORY.md`

---

## Step 4: Audit for Untracked Tools
Verify no tools are missing from the inventory:
// turbo
```bash
python3 plugins/tool-inventory/scripts/manage_tool_inventory.py audit
```

**Expected Output:** `✅ All tools registered` (or list of untracked tools to add)

---

## Step 5: Verify Discovery (Optional)
Test that the tool is now discoverable via RLM:
// turbo
```bash
python3 plugins/rlm-factory/scripts/query_cache.py --type tool "[keyword]"
```

**Expected Output:** Tool appears in search results

---

## Artifacts Updated

| Artifact | Path | Purpose |
|----------|------|---------|
| Master Inventory | `tools/tool_inventory.json` | Primary tool registry |
| RLM Cache | `.agent/learning/rlm_tool_cache.json` | Semantic search index |
| Markdown Inventory | `tools/TOOL_INVENTORY.md` | Human-readable inventory |

---

## Related Policies
- [Tool Discovery Policy](../.agent/rules/tool_discovery_and_retrieval_policy.md)
- [Coding Conventions](../.agent/rules/coding_conventions_policy.md)

## Related Tools
- `manage_tool_inventory.py` - Inventory CRUD operations
- `distiller.py` - RLM summarization engine
- `query_cache.py` - Tool discovery search
- `fetch_tool_context.py` - Tool manual retrieval
