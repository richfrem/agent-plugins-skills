# Microsoft Agent Framework (MAF) v1.0 — Comprehensive Component Research Summary

***

## 📌 Origin & Strategic Context

MAF v1.0 shipped **GA on April 3, 2026** as the production-ready convergence of two prior Microsoft open-source projects: **Semantic Kernel** (the kernel, plugin model, and provider connectors — \~22K GitHub stars) and **AutoGen** (multi-agent orchestration from Microsoft Research — \~53K stars). The merger means the "Semantic Kernel or AutoGen?" decision that shaped 2024–2025 agent architecture is now a legacy question — the graph-based workflow engine sits natively on top of the kernel in one package. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/), [\[digitalapplied.com\]](https://www.digitalapplied.com/blog/microsoft-agent-framework-1-0-dotnet-python-guide)

* **Languages:** .NET and Python, same concepts, same API shape, first-class support on both runtimes [\[digitalapplied.com\]](https://www.digitalapplied.com/blog/microsoft-agent-framework-1-0-dotnet-python-guide)
* **License:** MIT, open-source monorepo on GitHub (\~10.9K stars as of May 2026) [\[github.com\]](https://github.com/microsoft/agent-framework)
* **Commitment:** Long-term support from Day One with a stable API surface and documented upgrade path [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)

***

## 1. 🧱 The Agent (`AIAgent` / `Agent`)

The fundamental building block. An agent wraps an LLM client with instructions, tools, and session management.

### Key Properties:

* **`client`** — An `IChatClient` (.NET) or chat client instance (Python) pointing to any supported model provider
* **`name`** / **`instructions`** — Identity and system prompt
* **`tools`** — Function tools, MCP tools, or hosted tools
* **`middleware`** — Optional pipeline decorators for logging, governance, validation
* **`context_providers`** — Pluggable providers for memory, dynamic context injection

### Core API:

```python
# Python
agent = Agent(client=my_client, name="MyAgent", instructions="...")
response = await agent.run("Hello")
```

```csharp
// .NET
var agent = chatClient.AsAIAgent(name: "MyAgent", instructions: "...");
var response = await agent.RunAsync("Hello");
```

A single `RunAsync()` / `run()` call flows through the full layered pipeline (middleware → context → chat client → LLM). [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/agent-pipeline)

***

## 2. 🔄 Agent Pipeline Architecture

MAF uses a **layered pipeline** with three main tiers. This is the architectural backbone of the framework. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/agent-pipeline)

### Layer 1: Agent Middleware

* Wraps the **entire agent execution** via `.Use()` / `middleware=[]`
* Intercepts every call to `run()` / `RunAsync()` — can inspect/modify inputs and outputs
* Works with **any agent type** (ChatClientAgent, A2AAgent, GitHubCopilotAgent, etc.)
* Use cases: logging, validation, transformation, governance policy enforcement

### Layer 2: Context Layer

* **`ChatHistoryProvider`** — Manages conversation history persistence (in-memory, Cosmos DB, or custom) [\[medium.com\]](https://medium.com/microsoftazure/chat-history-providers-in-microsoft-agent-framework-making-agents-remember-f99476c88d3f)
* **`AIContextProvider`** — Injects dynamic context before each LLM call and can post-process responses [\[lukaswalter.dev\]](https://www.lukaswalter.dev/posts/agentframework_1_6/)
  * `ProvideAIContextAsync` (pre-call): inject user facts, memory, RAG results, guardrails
  * `StoreAIContextAsync` (post-call): analyze response, extract memory, update state
* Providers execute **in registration order**, allowing predictable layering [\[lukaswalter.dev\]](https://www.lukaswalter.dev/posts/agentframework_1_6/)

### Layer 3: Chat Client Layer

* The `IChatClient` with optional middleware decorators
* **FunctionInvocation** — handles the tool-calling loop
* **RawChatClient** — provider-specific implementation (Azure OpenAI, OpenAI, Anthropic, Bedrock, Gemini, Ollama)

 [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/agent-pipeline)

***

## 3. 💾 Session & State Management (`AgentSession`)

`AgentSession` is the **conversation state container** that carries history across calls, turning stateless `RunAsync()` invocations into coherent multi-turn exchanges. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/conversations/session), [\[devleader.ca\]](https://www.devleader.ca/2026/02/21/agentsession-and-multiturn-conversations-in-microsoft-agent-framework)

### Key Properties:

| Field                | Purpose                                               |
| -------------------- | ----------------------------------------------------- |
| `session_id`         | Unique session identifier                             |
| `service_session_id` | Service-specific conversation ID                      |
| `StateBag`           | Arbitrary key-value state container for provider data |

### Capabilities:

* **Multi-turn conversations:** Pass the same session object across multiple `run()` calls — the agent remembers prior context [\[devleader.ca\]](https://www.devleader.ca/2026/02/21/agentsession-and-multiturn-conversations-in-microsoft-agent-framework)
* **Serialization/restoration:** `SerializeSession()` and `DeserializeSessionAsync()` allow persisting sessions to any store and resuming later [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/conversations/session)
* **Concurrent sessions:** Lightweight objects — create thousands without meaningful resource pressure [\[devleader.ca\]](https://www.devleader.ca/2026/02/21/agentsession-and-multiturn-conversations-in-microsoft-agent-framework)
* **Session portability caveat:** Sessions are agent/service-specific. Reusing a session with a different agent configuration or provider can lead to invalid context [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/conversations/session)

### Chat History Providers:

| Provider                      | Description                                                                                                                                                                                                              |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `InMemoryChatHistoryProvider` | Default, in-process — lost on restart                                                                                                                                                                                    |
| `CosmosChatHistoryProvider`   | Azure Cosmos DB persistence — production-grade [\[medium.com\]](https://medium.com/microsoftazure/chat-history-providers-in-microsoft-agent-framework-making-agents-remember-f99476c88d3f) |
| Custom implementations        | Any backing store via the `ChatHistoryProvider` interface                                                                                                                                                                |

 [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/7.1.3-session-and-state-management)

***

## 4. 🔧 Tools & Function Calling

MAF supports three tool categories:

### 4a. Function Tools (Local)

* Python functions or .NET methods registered via `AIFunctionFactory.Create()` (replaced `[KernelFunction]` from Semantic Kernel era) [\[candede.com\]](https://candede.com/articles/maf-migration-guide/)
* The agent runtime handles the conversation loop: decides when a tool is needed, calls it, feeds the result back into the model context [\[devleader.ca\]](https://www.devleader.ca/2026/03/04/mcp-tool-integration-in-microsoft-agent-framework-in-c)

### 4b. Model Context Protocol (MCP) Tools

* **Open standard** for connecting agents to external tools and data sources through a standardized protocol [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools)
* Two patterns: **local MCP tools** (execute in-process) and **hosted MCP tools** (service-managed execution) [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/3.3.4-model-context-protocol-%28mcp%29)
* Full tool discovery, structured context, and decoupling between model and tools [\[linkedin.com\]](https://www.linkedin.com/pulse/part-1-model-context-protocol-microsoft-agent-framework-zahir-shaikh-uognc?tl=en)
* Headers (auth tokens, API keys) passed per-run and not persisted [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools)
* Official Microsoft MCP server catalog: 3.2K+ GitHub stars, covering Azure services (Cosmos, Monitor, Compute, etc.) [\[github.com\]](https://github.com/microsoft/mcp)

### 4c. Hosted Tools

* Service-managed execution: Code Interpreter, File Search, Web Search (Bing Grounding)
* Run in sandboxed environments managed by the AI service, not in the client application

 [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/agents/tools/local-mcp-tools), [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/3.3.4-model-context-protocol-%28mcp%29)

***

## 5. 🔀 Multi-Agent Workflow Orchestration

The workflow system is built on a **Pregel-style graph execution model** using synchronized **supersteps** (Bulk Synchronous Parallel). [\[github.com\]](https://github.com/microsoft/Agent-Framework-Samples/tree/main/07.Workflow)

### Core Workflow Components:

| Component      | Description                                                                                                                        |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Executors**  | Fundamental processing units — agents, functions, or custom logic. Each can have multiple message handlers invoked by message type |
| **Edges**      | Define message routing between executors. Can have conditions for dynamic routing                                                  |
| **Supersteps** | Synchronized execution rounds: collect messages → route → execute all targets → synchronization barrier → next round               |

### Five Built-in Orchestration Patterns:

| Pattern                     | Description                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sequential**              | Agents execute one after another in a defined order — assembly line [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/)                                                                                                                                                                                                   |
| **Concurrent**              | Agents execute in parallel, results aggregated at the end [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/)                                                                                                                                                                                                             |
| **Handoff**                 | Agents transfer control to each other based on context [\[medium.aks...kokane.com\]](https://medium.akshaykokane.com/creating-multi-agent-workflows-with-microsoft-agent-framework-8c68df1ec0ea)                                                                                                                                                                                 |
| **Group Chat**              | Agents collaborate in a shared conversation, coordinated by a manager for speaker selection [\[medium.aks...kokane.com\]](https://medium.akshaykokane.com/creating-multi-agent-workflows-with-microsoft-agent-framework-8c68df1ec0ea)                                                                                                                                            |
| **Magentic (Magentic-One)** | A manager agent dynamically coordinates specialized agents — creates/modifies task lists and handles subagent coordination (Python only as of May 2026) [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/), [\[azureguru.net\]](https://www.azureguru.net/workflow-orchestration-patterns-in-microsoft-agent-framework) |

All orchestrations support **human-in-the-loop** interactions through tool approval and request-info patterns. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/)

### Programmatic vs. Declarative:

* **Programmatic:** Full Python/C# code using `WorkflowBuilder` with typed edges and executor binding [\[github.com\]](https://github.com/microsoft/Agent-Framework-Samples/tree/main/07.Workflow)
* **Declarative (YAML):** Define workflow logic in YAML config files — easier to read, modify, share. Supports variable management, control flow, agent/tool invocation, HTTP/MCP integration, HITL, and conversation control [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/workflows/declarative)

```yaml
# Example declarative workflow
kind: Workflow
trigger:
  kind: OnConversationStart
  id: my_workflow
  actions:
    - kind: InvokeAgent
      id: writer
      agentName: CopyWriter
    - kind: InvokeAgent
      id: reviewer
      agentName: QualityReviewer
```

The `agent-framework-declarative` Python package adds YAML parsing + **PowerFx expression evaluation** for dynamic values and conditional logic within YAML definitions. [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/4.9-declarative-agents-%28python%29), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/workflows/declarative)

***

## 6. 🌐 Interoperability Protocols

### 6a. Agent-to-Agent (A2A) Protocol

* **Open standard** (originally Google, now Linux Foundation) enabling standardized communication between agents built on different frameworks [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/integrations/a2a), [\[a2a-protocol.org\]](https://a2a-protocol.org/latest/)
* Supports: agent discovery via `AgentCard`, message-based communication, long-running tasks, cross-platform interop (Python ↔ .NET)
* MAF agents can be **exposed as A2A servers** (network-accessible) or **consume remote A2A agents** as executors in local workflows [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/3.5-agent-to-agent-communication-%28a2a%29)
* Packages: `agent-framework-a2a` (Python), `Microsoft.Agents.AI.A2A` (.NET)

### 6b. Model Context Protocol (MCP)

* Standardizes how agents connect to **tools and data sources** — complementary to A2A
* "MCP is for agent-to-tool; A2A is for agent-to-agent" [\[kvassiliou.com\]](https://kvassiliou.com/tech/agent-interoperability-stack-2026-mcp-vs-a2a)

Both ship as **native, first-class** features at 1.0 — not bolt-on integrations. [\[digitalapplied.com\]](https://www.digitalapplied.com/blog/microsoft-agent-framework-1-0-dotnet-python-guide)

***

## 7. 🔌 Provider Matrix (Model Agnosticism)

Six providers at 1.0, swappable with a **one-line change**: [\[digitalapplied.com\]](https://www.digitalapplied.com/blog/microsoft-agent-framework-1-0-dotnet-python-guide)

| Provider         | Package                                                    | Notes |
| ---------------- | ---------------------------------------------------------- | ----- |
| Azure OpenAI     | `Microsoft.Agents.AI.Foundry` / `agent_framework.foundry`  | Requires Azure subscription + Foundry resource |
| OpenAI (direct)  | `Microsoft.Agents.AI.OpenAI` / `agent_framework.openai`    | Plain API key — no Azure required |
| Anthropic Claude | Via `IChatClient` adapter                                  | |
| Amazon Bedrock   | `agent_framework.bedrock`                                  | |
| Google Gemini    | Via OpenAI-compatible endpoint (no extra package needed)   | Use `OpenAIClient` pointed at `generativelanguage.googleapis.com/v1beta/openai/` — confirmed working in .NET with `Microsoft.Agents.AI.OpenAI` only |
| Ollama (local)   | Via OpenAI-compatible endpoint                             | |

The key abstraction is `IChatClient` (.NET) from `Microsoft.Extensions.AI` — any model backend that implements this interface works with MAF agents, workflows, and middleware. [\[devleader.ca\]](https://www.devleader.ca/2026/03/04/mcp-tool-integration-in-microsoft-agent-framework-in-c)

> **Practical note (confirmed hands-on):** Azure/Foundry is NOT required to get started. The `01_Basics` examples all run with a plain `OPENAI_API_KEY` or `GEMINI_API_KEY`. Foundry is only needed for hosted deployment or Azure-specific features. See the [MAF Learning Repo](https://github.com/deployed-in-azure/MicrosoftAgentFramework) for working examples.

***

## 8. 🛡️ Agent Governance Toolkit (AGT) — Companion Framework

AGT is a **separate open-source project** (3.4K GitHub stars) that plugs into MAF's middleware pipeline to provide runtime governance. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/governance-at-the-speed-of-agents-microsoft-agent-framework-and-agent-governance-toolkit-better-together/), [\[github.com\]](https://github.com/microsoft/agent-governance-toolkit)

### Seven Packages:

| Package                                         | Purpose                                                                                                                                                                                                                                                                                      |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Agent OS (agent-os-kernel)**                  | Core policy engine — PEP/PDP pair evaluating YAML, OPA Rego, or Cedar rules. Sub-millisecond, deterministic, hallucination-free enforcement [\[linkedin.com\]](https://www.linkedin.com/pulse/microsoft-agent-governance-toolkit-honest-take-venkat-peri-vwcle) |
| **Agent Mesh (agentmesh-platform)**             | Zero-trust agent identity using DIDs + Ed25519 keys, Inter-Agent Trust Protocol (IATP), behavioral trust scoring (0–1000) [\[linkedin.com\]](https://www.linkedin.com/pulse/microsoft-agent-governance-toolkit-honest-take-venkat-peri-vwcle)                   |
| **Agent Runtime (agent-hypervisor)**            | Privilege rings (CPU ring metaphor), saga orchestration for multi-step transactions, kill switch [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-governance-toolkit)                                                                                    |
| **Agent SRE (agent-sre)**                       | SLOs, error budgets, circuit breakers, chaos engineering, progressive delivery [\[linkedin.com\]](https://www.linkedin.com/pulse/microsoft-agent-governance-toolkit-honest-take-venkat-peri-vwcle)                                                              |
| **Agent Compliance (agent-governance-toolkit)** | Automated compliance grading against EU AI Act, HIPAA, SOC2, OWASP Agentic Top 10 [\[linkedin.com\]](https://www.linkedin.com/pulse/microsoft-agent-governance-toolkit-honest-take-venkat-peri-vwcle)                                                           |
| **Agent Marketplace**                           | Plugin lifecycle management [\[linkedin.com\]](https://www.linkedin.com/pulse/microsoft-agent-governance-toolkit-honest-take-venkat-peri-vwcle)                                                                                                                 |
| **Agent Lightning**                             | RL training governance [\[linkedin.com\]](https://www.linkedin.com/pulse/microsoft-agent-governance-toolkit-honest-take-venkat-peri-vwcle)                                                                                                                      |

### MAF Integration:

AGT middleware plugs directly into MAF's `middleware=[]` parameter: [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/governance-at-the-speed-of-agents-microsoft-agent-framework-and-agent-governance-toolkit-better-together/)

```python
from agent_os.integrations.maf_adapter import (
    GovernancePolicyMiddleware,
    CapabilityGuardMiddleware,
    RogueDetectionMiddleware,
    AuditTrailMiddleware,
)

agent = Agent(
    client=client,
    middleware=[
        AuditTrailMiddleware(audit_log=audit_log),
        GovernancePolicyMiddleware(evaluator=evaluator),
        CapabilityGuardMiddleware(allowed_tools=["check_credit", "get_rates"]),
        RogueDetectionMiddleware(detector=detector),
    ],
)
```

**Key design principle:** MAF handles model input/output safety (content filters, prompt shields). AGT governs **agent actions and tool execution**. Different layers, complete coverage, one middleware pipeline. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/governance-at-the-speed-of-agents-microsoft-agent-framework-and-agent-governance-toolkit-better-together/)

* Polyglot: Python, TypeScript, .NET, Rust, Go [\[github.com\]](https://github.com/microsoft/agent-governance-toolkit)
* Framework-agnostic: also integrates with LangChain, CrewAI, Google ADK, OpenAI Agents [\[microsoft.github.io\]](https://microsoft.github.io/agent-governance-toolkit/)
* 10/10 OWASP Agentic Top 10 coverage, 13,000+ tests [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-governance-toolkit)

***

## 9. 📊 Observability & Telemetry

MAF provides **production-grade observability through OpenTelemetry** instrumentation. [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/3.6-observability-and-monitoring)

### What's Instrumented Automatically:

* **Traces:** Distributed tracing across agent runs, chat completions, tool invocations, workflow executions
* **Metrics:** Token usage, operation duration, function invocation performance
* **Logs:** Structured message events with conversation context and standardized GenAI attributes

### Architecture:

Two telemetry layers wrap execution: [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/3.6-observability-and-monitoring)

* **`AgentTelemetryLayer`** — wraps high-level agent execution
* **`ChatTelemetryLayer`** — wraps underlying chat client operations

### Configuration:

```python
# Python — enabled by default since v1.0
from agent_framework.observability import setup_observability
setup_observability(
    applicationinsights_connection_string=CONNECTION_STRING
)
```

| Setting                  | Env Var                                | Description                                 |
| ------------------------ | -------------------------------------- | ------------------------------------------- |
| `ENABLED`                | `OBSERVABILITY_ENABLED`                | Master switch (defaults to `True`)          |
| `SENSITIVE_DATA_ENABLED` | `OBSERVABILITY_SENSITIVE_DATA_ENABLED` | Controls if prompts/tool outputs are logged |

 [\[deepwiki.com\]](https://deepwiki.com/microsoft/agent-framework/3.6-observability-and-monitoring)

***

## 10. 🖥️ DevUI — Local Development Debugger

DevUI is a **lightweight standalone web-based tool** for running, inspecting, and debugging agents and workflows during development. [\[telerik.com\]](https://www.telerik.com/blogs/from-devui-to-observability-evolving-the-agent-dev-loop-in-microsoft-agent-framework), [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/the-golden-triangle-of-agentic-development-with-microsoft-agent-framework-ag-ui-devui-opentelemetry-deep-dive/)

### Capabilities:

* Interactive web UI for testing agent conversations
* OpenAI-compatible API backend
* Visualization of workflow execution flow
* Immediate visibility into multi-agent interactions
* Bridges the gap between local debugging and production observability

### Getting Started (.NET):

```bash
dotnet new install Microsoft.Agents.AI.ProjectTemplates::1.3.0-preview.1.26251.3
dotnet new aiagent-webapi
```

Part of the **"Golden Triangle"** development stack: DevUI (debugging) + AG-UI (frontend protocol) + OpenTelemetry (observability). [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/agent-framework/the-golden-triangle-of-agentic-development-with-microsoft-agent-framework-ag-ui-devui-opentelemetry-deep-dive/)

***

## 11. ☁️ Deployment: Foundry Agent Service (Hosted Agents)

For production deployment, MAF agents can be hosted on **Microsoft Foundry Agent Service** as containerized hosted agents. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent), [\[ankitbko.github.io\]](https://ankitbko.github.io/blog/2026/05/hosted-agents-part-1/)

### Deployment Lifecycle:

1. **Build & push** — Package agent code into a container image → Azure Container Registry
2. **Create agent version** — Register with Foundry Agent Service. Platform provisions infrastructure + creates dedicated Entra agent identity
3. **Poll for status** — Wait for `active` state
4. **Invoke** — Send requests to the agent's dedicated endpoint

### Key Differentiator — Isolation:

Each request executes in a **new micro-VM**, spawned on the hot path, isolated from all other requests. This prevents cross-request data leakage when agents execute arbitrary code. [\[ankitbko.github.io\]](https://ankitbko.github.io/blog/2026/05/hosted-agents-part-1/)

### Deployment Options:

| Tool                              | Best For                                          |
| --------------------------------- | ------------------------------------------------- |
| `azd` (Azure Developer CLI)       | CLI workflows, CI/CD, scripting                   |
| Foundry Toolkit VS Code Extension | Integrated editor experience with Agent Inspector |
| Source code deploy (preview)      | Upload `.zip` — platform builds and hosts         |

 [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent), [\[github.com\]](https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/csharp/hosted-agents)

**Important:** Hosted Agents are the production path, but MAF's `InProcessExecution` runner works entirely locally for development — no cloud dependency required. [\[medium.com\]](https://medium.com/@arnaud.tincelin/deploy-hosted-agents-on-microsoft-foundry-complete-guide-0de13e4f835f)

***

## 12. 🔄 Migration Path (from Semantic Kernel / AutoGen)

The repo includes dedicated migration guides: [\[candede.com\]](https://candede.com/articles/maf-migration-guide/)

| Change            | Before (RC/Preview)           | After (1.0 GA)                                 |
| ----------------- | ----------------------------- | ---------------------------------------------- |
| Namespace         | `Microsoft.Agents.AI.AzureAI` | `Microsoft.Agents.AI.Foundry`                  |
| Agent management  | `Azure.AI.Projects.Agents`    | Consolidated into `Azure.AI.Projects`          |
| Run method        | `InvokeAsync()`               | `RunAsync()`                                   |
| Response type     | `AgentResponseItem<T>`        | `AgentResponse`                                |
| Tool registration | `[KernelFunction]` attribute  | `AIFunctionFactory.Create()`                   |
| Auth              | Various                       | `DefaultAzureCredential` via `AIProjectClient` |

***

## Summary Architecture Diagram (Conceptual)

```
┌─────────────────────────────────────────────────────┐
│                   YOUR APPLICATION                   │
├─────────────────────────────────────────────────────┤
│  Agent Middleware    (logging, AGT governance, etc.) │
│  ┌───────────────────────────────────────────────┐  │
│  │  Context Layer                                 │  │
│  │  ├─ ChatHistoryProvider (memory/Cosmos/custom) │  │
│  │  └─ AIContextProviders (memory, RAG, guards)   │  │
│  ├───────────────────────────────────────────────┤  │
│  │  Chat Client Layer                             │  │
│  │  ├─ Function Invocation (tool calling loop)    │  │
│  │  ├─ Chat Middleware + Telemetry (OTel)          │  │
│  │  └─ RawChatClient (provider-specific)          │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  PROVIDERS: Azure OpenAI│OpenAI│Claude│Bedrock│     │
│             Gemini│Ollama                            │
├─────────────────────────────────────────────────────┤
│  TOOLS: Function Tools │ MCP Servers │ Hosted Tools │
├─────────────────────────────────────────────────────┤
│  WORKFLOWS: Sequential│Concurrent│Handoff│          │
│             GroupChat│Magentic│Declarative YAML      │
├─────────────────────────────────────────────────────┤
│  INTEROP: A2A Protocol │ MCP Protocol               │
├─────────────────────────────────────────────────────┤
│  GOVERNANCE: AGT (Policy│Identity│Sandbox│SRE│Audit)│
├─────────────────────────────────────────────────────┤
│  HOSTING: Local/InProcess │ Foundry Hosted Agents   │
└─────────────────────────────────────────────────────┘
```

