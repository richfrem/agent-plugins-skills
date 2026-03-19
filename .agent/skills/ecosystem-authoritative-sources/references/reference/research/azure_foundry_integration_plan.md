# Azure AI Foundry & Open Agent-Skill Integration Plan

This document outlines the research, sources, and recommendations for integrating the Open Agent-Skill format (used in `agent-plugins-skills`) with Microsoft's Azure AI Foundry Agent Service.

## 1. Research & Sources

The following architectural insights are derived from official Microsoft documentation and blog posts (Jan-Feb 2026):

*   **Source 1:** [Context-Driven Development: Agent Skills for Microsoft Foundry and Azure](https://devblogs.microsoft.com/all-things-azure/context-driven-development-agent-skills-for-microsoft-foundry-and-azure/)
    *   *Insight:* Validates the "documentation as skills" paradigm. Microsoft uses a `.github/skills/` directory structure with `SKILL.md` files identically to our open standard to provide "activation context" for agents.
*   **Source 2:** [Multi-Agent Orchestration with Azure AI Foundry: From Idea to Production](https://techcommunity.microsoft.com/blog/azureinfrastructureblog/multi%E2%80%91agent-orchestration-with-azure-ai-foundry-from-idea-to-production/4449925)
    *   *Insight:* Details the alignment between the Azure rules engine and open skills: Customize Instructions -> `SKILL.md`, Integrate Tools -> MCP Declarations. Highlights MCP for shared agent context.
*   **Source 3:** [Foundry Agent Service quickstarts and SDKs](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-foundry/agents/quickstart.md)
    *   *Insight:* When using the `azure-ai-projects` SDK, the agent is instantiated by passing the `SKILL.md` content into the `instructions` parameter and attaching required tool references to the `tools` array.
*   **Source 4:** [Foundry Agent Service quotas and limits](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-foundry/agents/quotas-limits.md)
    *   *Insight:* Hard limit of 128 registered tools per agent instance. This enforces a multi-agent orchestration architecture rather than monolithic agents.
*   **Source 5:** [Foundry Agent Service FAQ & Environment Setup](https://github.com/MicrosoftDocs/azure-ai-docs/blob/main/articles/ai-foundry/agents/environment-setup.md)
    *   *Insight:* Standard Setup allows BYO Virtual Network and Customer Managed Keys (CMK), storing state in Cosmos DB. This enables enterprise-grade execution of our skills.

## 2. Implementation Recommendations

To properly integrate Azure AI Foundry into our existing tooling and governance structure, we recommend a three-pronged approach:

### Phase 1: Establish the Standard (Update `ecosystem-authoritative-sources`)
Before building deployment tools, we must define how Azure Foundry fits into our ecosystem constraints.
*   **Action:** Add a new reference file: `plugins/agent-skill-open-specifications/skills/ecosystem-authoritative-sources/reference/azure-foundry-agents.md`.
*   **Content:** Document how `SKILL.md` maps to the `instructions` parameter, how MCP tools are declared, and the strict adherence to the 128-tool limit requiring multi-agent orchestration. This serves as the ground truth for any scripts we write later.

### Phase 2: Update the Bridge (`agent-bridge` Skill)
Our current ecosystem has bridging capabilities to take a skill and deploy it to a specific environment (e.g., `.github/agents`, Claude Code).
*   **Action:** Enhance the `agent-bridge` skill (and its underlying python scripts like `bridge_installer.py`) to recognize `azure-foundry` as a target environment.
*   **Content:** The bridge should be able to read a `/skills` directory and output the necessary foundational code (e.g., Python SDK snippets or Bicep templates) required to instantiate those skills as Azure Foundry Agents.

### Phase 3: Create a Dedicated Scaffolder (`create-azure-agent` Skill)
Similar to the recent work on `create-agentic-workflow` for GitHub Actions, we need a dedicated interactive scaffolder for Azure.
*   **Action:** Create a new skill in the `agent-scaffolders` plugin called `create-azure-agent`.
*   **Content:** This interactive CLI tool will ask the user which existing `SKILL.md` to target, whether they need a Basic or Standard (VNet) setup, what MCP tools are needed, and output a ready-to-deploy Azure Bicep/Terraform template and Python wrapper for that specific skill.

## 3. Next Steps

1.  Review and approve this integration plan.
2.  Begin Phase 1 by drafting the `azure-foundry-agents.md` reference document for the authoritative sources skill.
3.  Design the Python/SDK payload templates required for Phase 2.
