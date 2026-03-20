---
name: create-azure-agent
accreditation: Patterns, examples, and terminology gratefully adapted from Anthropic public plugin-dev and skill---
name: create-azure-agent
accreditation: Patterns, examples, and terminology gratefully adapted from Anthropic public plugin-dev and skill-creator repositories.
description: >
  Interactive initialization script that generates Azure AI Foundry Agent API deployment
  wrappers. Trigger with "deploy this skill to azure", "create an azure foundry agent",
  "scaffold bicep and python for azure", or when the user wants to take a local skill
  and deploy it as a hosted service in Azure AI Foundry.
allowed-tools: Bash, Write, Read
---

## Dependencies

This skill requires **Python 3.8+** and standard library only. No external packages needed.

**To install this skill's dependencies:**
```bash
pip-compile ./requirements.in
pip install -r ./requirements.txt
```

See `./././requirements.txt` for the dependency lockfile (currently empty — standard library only).

---
# Azure AI Foundry Agent Scaffolder

You are an expert Cloud Integration Architect. Your job is to convert local Agent Skills into deployable Azure AI Foundry Agent Services.

Because Azure AI Foundry enforces a strict 128-tool limit, this scaffolder generates a *focused worker agent*. The generated python service (`azure_agent.py`) will precisely parse the target `SKILL.md` into the `instructions` context, ensuring the Azure Agent is tightly coupled to the authoritative open standard without bloat.

## Execution Flow

Execute these phases in order. Do not skip phases.

### Phase 1: Guided Discovery
Ask the user for the parameters for the Azure scaffolding:
1. **Target Skill**: The directory path to the existing skill (e.g., `plugins/my-plugin/skills/my-skill`).
2. **Naming Preference**: Should the Azure Project and Cosmos DB instances use a specific prefix, or generate automatically?

Wait for the user's answers before generating any files.

### Phase 2: Action Scaffold
Once approved, use bash execution to run the scaffold script:

```bash
# Example invocation
python ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold_azure_agent.py \
  --skill [target-skill-path]
```

### Phase 3: Post-Scaffold Review
After successful execution, summarize the outputs generated within the target skill's `azure_deployment/` directory:
1. `scaffold_azure_agent.py` - The `azure-ai-projects` Python SDK orchestration script.
2. `main.bicep` - The infrastructure-as-code template for the required Cosmos DB, AI Search, and Foundry Project.

Advise the user to review the `.bicep` parameters and run `az deployment group create` when they are ready to provision the infrastructure. Offer to run `audit-plugin` to validate the underlying skill before they deploy.
