---
concept: tools-manifest
source: plugin-code
source_file: tools_manifest.json
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:04.428271+00:00
cluster: scripts
content_hash: 7219c8614831b375
---

# Tools Manifest

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

{
  "metadata": {
    "generated_at": "2026-03-09T08:39:11.576352",
    "source": "plugins/",
    "description": "Auto-discovered scripts from the plugins/ hierarchy"
  },
  "plugins": {
    "adr-manager": {
      "count": 2,
      "scripts": [
        {
          "name": "adr_manager.py",
          "path": "plugins/adr-manager/skills/adr-management/scripts/adr_manager.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "next_number.py",
          "path": "plugins/adr-manager/skills/adr-management/scripts/next_number.py",
          "purpose": "",
          "type": "python"
        }
      ]
    },
    "agent-loops": {
      "count": 4,
      "scripts": [
        {
          "name": "swarm_run.py",
          "path": "plugins/agent-loops/scripts/swarm_run.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "swarm_run.py",
          "path": "plugins/agent-loops/skills/agent-swarm/scripts/swarm_run.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "agent_orchestrator.py",
          "path": "plugins/agent-loops/skills/orchestrator/scripts/agent_orchestrator.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "swarm_run.py",
          "path": "plugins/agent-loops/skills/orchestrator/scripts/swarm_run.py",
          "purpose": "",
          "type": "python"
        }
      ]
    },
    "agent-scaffolders": {
      "count": 7,
      "scripts": [
        {
          "name": "analyze_scripts.py",
          "path": "plugins/agent-scaffolders/scripts/analyze_scripts.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "auto_fix_local_links.py",
          "path": "plugins/agent-scaffolders/scripts/auto_fix_local_links.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "validate_local_links.py",
          "path": "plugins/agent-scaffolders/scripts/validate_local_links.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "inventory_plugin.py",
          "path": "plugins/agent-scaffolders/skills/analyze-plugin/scripts/inventory_plugin.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "execute.py",
          "path": "plugins/agent-scaffolders/skills/audit-plugin-l5/scripts/execute.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "bad_script.py",
          "path": "plugins/agent-scaffolders/tests/flawed-plugin/scripts/bad_script.py",
          "purpose": "Deliberately flawed script for testing security detection.",
          "type": "python"
        },
        {
          "name": "danger.sh",
          "path": "plugins/agent-scaffolders/tests/flawed-plugin/scripts/danger.sh",
          "purpose": "",
          "type": "bash"
        }
      ]
    },
    "agent-scaffolders": {
      "count": 7,
      "scripts": [
        {
          "name": "scaffold.py",
          "path": "plugins/agent-scaffolders/scripts/scaffold.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "audit.py",
          "path": "plugins/agent-scaffolders/skills/audit-plugin/scripts/audit.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "scaffold_agentic_workflow.py",
          "path": "plugins/agent-scaffolders/skills/create-agentic-workflow/scripts/scaffold_agentic_workflow.py",
          "purpose": "",
          "type": "python"
        },
        {
          "name": "scaffold_azure_agent.py",
          "path": "plugins/agent-scaffolders/skills/create-azure-agent/scripts/scaffold_azure_agent.py",
          "purpose": "scaffold_azure_agent.py",
          "type": "python"
        },
        {
          "name": "scaffold_github_action.py",
          "path": "plugins/agent-scaffolders/skills/cre

*(content truncated)*

## See Also

- [[rlm-tools-manifest]]
- [[1-initialize-a-custom-manifest-in-a-temp-folder]]
- [[add-project-root-to-syspath-to-ensure-we-can-import-tools-package]]
- [[default-file-extensions-to-index-if-manifest-is-empty]]
- [[distiller-manifest]]
- [[file-manifest]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `tools_manifest.json`
- **Indexed:** 2026-04-27T05:21:04.428271+00:00
