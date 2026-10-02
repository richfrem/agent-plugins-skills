---
name: create-azure-agent
plugin: agent-scaffolders
description: >
  Deploys a skill as an Azure AI Foundry hosted agent. NOT for Docker runtime skills (use `create-docker-skill`) and NOT for MCP server integrations (use `create-mcp-integration`).
argument-hint: "[skill-dir]"
allowed-tools: Bash, Write, Read
---

# Create Azure Agent (`create-azure-agent`)

Generates Azure AI Foundry deployment wrappers, Bicep infrastructure templates, and Azure AI Projects SDK orchestration scripts for existing skills.

## Contents

- [Critical Constraints](#critical-constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Critical Constraints

1. **Scope Boundaries**: Designed specifically for Azure AI Foundry hosted agents. Use `create-docker-skill` for containerized runtimes and `create-mcp-integration` for MCP servers.
2. **Tool Ceiling Limit**: Azure AI Foundry enforces a strict 128-tool limit per agent. The scaffolder generates a focused worker configuration.
3. **Authentication Pre-Condition**: Azure CLI authentication (`az login`) and active subscription context are required before deployment execution.

## Quick start

Scaffold Azure AI Foundry deployment templates for a target skill:

```bash
python3 scripts/scaffold_azure_agent.py --skill-dir plugins/<plugin>/skills/<skill-name>
```

## Workflow

1. **Resolve Target Skill**: Validate that the input path contains a functional `SKILL.md`.
2. **Gather Configuration**: Collect Azure subscription, resource group, region, and project naming preferences.
3. **Generate Artifacts**: Run `scaffold_azure_agent.py` to create `azure_deployment/azure_agent.py` and `azure_deployment/main.bicep`.
4. **Deploy Infrastructure**: Review Bicep parameters and deploy via `az deployment group create`.

## Verification

Validate generated Bicep and Python deployment wrappers against Azure schema:

```bash
az bicep build --file azure_deployment/main.bicep
```

## References

- [acceptance-criteria.md](references/acceptance-criteria.md) — Acceptance gates and deployment wrapper requirements.
- [fallback-tree.md](references/fallback-tree.md) — Fallback resolution when Azure CLI or Bicep validation fails.
