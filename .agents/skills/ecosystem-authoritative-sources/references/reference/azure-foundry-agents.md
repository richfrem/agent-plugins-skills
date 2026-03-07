# Azure AI Foundry Agents & Open Agent-Skills

This document outlines the architectural mapping between the Open Agent-Skill format and the Microsoft Azure AI Foundry Agent Service, establishing the authoritative patterns for enterprise deployments.

## The Paradigm: "Context-Driven Development"
Azure AI Foundry uses agents not as monolithic chat bots, but as "Assembly Line" components. Frontier LLMs already possess knowledge of patterns and SDKs; they simply need **Activation Context**. 

Instead of typing large unstructured prompts or relying on manual documentation, domain knowledge is packaged as governed `SKILL.md` files. This machine-readable skill serves as the precise activation context injected into the Foundry agent.

## Core Architectural Mappings

When instantiating an Azure Foundry agent (e.g., via the `azure-ai-projects` Python SDK), the Open Skill package components map cleanly into the API arguments:

1. **`instructions` (The Brain):** The raw markdown content of the `SKILL.md` file is passed exactly as the `instructions` string limit.
2. **`tools` (The Limbs):** The tools declared by the skill (e.g., specific MCP servers, OpenAPI specs, or native Azure Functions/Logic Apps) are bound to the `tools` array. The Agent Service handles orchestration, state tracking, and execution retry loops on the backend.
3. **`tool_resources` (The Memory):** If the skill includes domain documents in a `reference/` folder, those files upload to an Azure Vector Store. The vector store ID is attached via the `tool_resources` argument for native File Search capabilities.

### Conceptual API Integration
```python
# The Open Skill package becomes the Azure API arguments
skill_content = read_file("my-skill/SKILL.md")

agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="OIDC_Setup_Specialist",
    instructions=skill_content, # <-- The Open Skill is injected here
    tools=skill_required_tools  # <-- The MCP/OpenAPI tools the skill needs
)
```

## Hard Constraints & Enterprise Limits

### 1. The 128 Tool Limit (Context Rot Prevention)
Azure Foundry enforces a hard limit of **128 tools per agent**. 
*   **Rule:** You **MAY NOT** create monolithic agents with hundreds of tools. 
*   **Solution:** You must use specialized Worker Agents. A worker agent is instantiated with one specific `SKILL.md` and *only* the specific tools required for that skill.
*   **Orchestration:** Master orchestrator agents observe user intent, delegate tasks to specialized Foundry worker agents via the Agent Service, and use shared Cosmos DB threads and Model Context Protocol (MCP) to maintain overarching context.

### 2. Standard Setup & Virtual Networks (Enterprise Governance)
For enterprise workloads requiring strict governance, skills deployed to Azure Foundry must support the **Standard Setup with BYO Virtual Network**.
*   **Execution:** Fully private execution isolating traffic inside a VNet.
*   **State:** Agent states, file searches, and conversation threads are backed by Customer-Owned Azure Cosmos DB and Azure AI Search.
*   **Authentication:** Managed Identity and Customer Managed Keys (CMK) are standard.

## Summary
Open Agent-Skills are the governed, portable "configuration payload" for the secure, compliant runtime "engine" provided by Azure AI Foundry.
