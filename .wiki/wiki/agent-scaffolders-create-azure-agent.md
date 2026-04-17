---
concept: agent-scaffolders-create-azure-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-azure-agent.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.317572+00:00
cluster: skill
content_hash: 315a9e16c7cf71cf
---

# Agent Scaffolders Create Azure Agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: create-azure-agent
description: Deploy a skill as an Azure AI Foundry hosted agent
argument-hint: "[skill-dir]"
allowed-tools: Bash, Write, Read
---

Follow the `create-azure-agent` skill workflow to generate Azure AI Foundry deployment
wrappers for an existing agent skill.

## Inputs

- `$ARGUMENTS` — optional path to the skill directory to deploy. Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` provides a skill directory, resolve and validate the path
2. Follow the create-azure-agent phased workflow: confirm the target skill, gather Azure
   configuration (subscription, resource group, region, naming preferences), then run
   `scaffold_azure_agent.py` to generate Bicep templates and the Python Azure AI Projects
   SDK deployment wrapper
3. Summarize generated files in the skill's `azure_deployment/` directory
4. Instruct on reviewing `.bicep` parameters and running `az deployment group create`

## Output

`azure_deployment/azure_agent.py` (Azure AI Projects SDK orchestration script) and
`azure_deployment/main.bicep` (Cosmos DB, AI Search, and Foundry Project infrastructure).

## Edge Cases

- If `$ARGUMENTS` is empty: ask for the target skill directory before proceeding
- If Azure credentials are not configured: instruct user to run `az login` first
- Azure AI Foundry enforces a 128-tool limit — scaffold generates a focused worker agent
- Offer to run `/agent-scaffolders:audit-plugin` to validate the skill before deploying


## See Also

- [[procedural-fallback-tree-create-azure-agent]]
- [[procedural-fallback-tree-create-azure-agent]]
- [[procedural-fallback-tree-create-azure-agent]]
- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-scaffolders-create-docker-skill]]
- [[agent-scaffolders-create-github-action]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-azure-agent.md`
- **Indexed:** 2026-04-17T06:42:10.317572+00:00
