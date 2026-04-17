---
concept: procedural-fallback-tree-plugin-maintenance
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/maintain-plugins/references/fallback-tree.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.111850+00:00
cluster: vendor
content_hash: 10dadfd84ea86db8
---

# Procedural Fallback Tree: Plugin Maintenance

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Procedural Fallback Tree: Plugin Maintenance

If the primary scripts fail or produce unexpected results, execute the following triage steps in order.

## 1. Vendor Inventory Not Found
If `./../scripts/sync_with_inventory.py` reports it cannot locate the vendor inventory file:
- **Action**: Enter Safety Mode. Do NOT proceed with any delete operations.
- **Resolution**: Instruct the user to run `plugin_bootstrap.py` or manually clone the vendor repo to `.vendor/agent-plugins-skills`. Never synthesize a vendor list from the local filesystem.

## 2. Custom Plugin Accidentally Removed
If a project-specific plugin (not in the vendor list) is missing after a sync operation:
- **Action**: STOP immediately. Do NOT re-run the sync. Run `git checkout -- plugins/<name>/` to restore the plugin. Identify why the plugin was not protected (i.e., whether it was incorrectly listed in the vendor inventory).

## 3. Agent Config Directory Missing
If `./../scripts/sync_with_inventory.py` reports a target directory (`.agents/`, `.gemini/`, etc.) does not exist:
- **Action**: Do NOT create the directory manually. Report to the user that the agent environment has not been initialized. Suggest running the `plugin-installer` skill from `plugin-manager` to initialize the environment first.

## 4. Audit Script Unavailable
If `../scripts/audit_structure.py` cannot be found or exits with a non-zero code:
- **Action**: Fall back to the manual audit checklist in the Audit section of `./SKILL.md`. Document findings as a markdown checklist. Do NOT skip the audit and claim success.


## See Also

- [[procedural-fallback-tree-plugin-analyzer]]
- [[procedural-fallback-tree-audit-plugin]]
- [[procedural-fallback-tree-create-plugin]]
- [[procedural-fallback-tree-plugin-analyzer]]
- [[procedural-fallback-tree-plugin-analyzer]]
- [[procedural-fallback-tree-audit-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/maintain-plugins/references/fallback-tree.md`
- **Indexed:** 2026-04-17T06:42:10.111850+00:00
