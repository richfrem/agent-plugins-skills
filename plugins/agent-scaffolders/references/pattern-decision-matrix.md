# Architectural Pattern Decision Matrix

A reference for deciding when and how to incorporate advanced L4 architectural and state management patterns into skills. Used by `create-skill` and `create-plugin` during the design phase to selectively load deep context only when needed.

---

## Pattern Decision Tree

Not every skill needs complex architectural patterns. Use this tree during the discovery phase to determine which patterns to inject.

**CRITICAL RULE**: Do not explain the theory of these patterns to the user. Ask the diagnostic question. If the user answers YES, **MUST** load the corresponding markdown definition from `plugins reference/agent-skill-open-specifications/L4-pattern-definitions/`.

### Category 1: Input and Routing
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Does the skill interact with external systems (Jira, Figma, etc.)? | **Connector Placeholders** | `connector-placeholders.md` |
| Should the skill work with limited functionality without tools connected? | **Dual-Mode Degradation** | `dual-mode-degradation.md` |
| Does the skill take complex text, URLs, or files as input context? | **Multi-Modal Routing** | `multi-modal-routing.md` |
| Does the user report surface symptoms that need root-cause diagnosis? | **Anti-Symptom Triage** | `anti-symptom-triage.md` |
| Does the command group several sub-operations that have different outputs? | **Sub-Action Multiplexing** | `sub-action-multiplexing.md` |

### Category 2: Execution and Safety
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Is there a mix of low-risk and high-risk actions in this domain? | **Graduated Autonomy** | `graduated-autonomy.md` |
| Can the workflow trigger potentially dangerous or unrecoverable actions? | **Escalation Taxonomy** | `escalation-taxonomy.md` |
| Are there multiple tools, where failure of one shouldn't crash the workflow? | **Conditional Step Inclusion** | `conditional-step-inclusion.md` |
| Does the agent query multiple systems of differing truthfulness? | **Priority-Ordered Scanning** | `priority-ordered-scanning.md` |
| Does the command analyze or synthesize data across multiple systems? | **Multi-Source Synthesis** | `multi-source-synthesis.md` |
| Is this a meta-skill designed to bootstrap or append to other skills? | **Dual-Mode Meta-Skill** | `dual-mode-meta-skill.md` |

### Category 3: Output and Contracts
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Does the command generate a report, audit, or synthesis? | **Structured Output Contracts** | `structured-output-contracts.md` |
| Does the command output differ vastly based on complex vs simple requests? | **Complexity-Tiered Output** | `complexity-tiered-output.md` |
| Could the agent hallucinate claims from vague qualitative data? | **Quantification Enforcement** | `quantification-enforcement.md` |
| Does the command output a list of issues or audit findings? | **Severity-Stratified Output** | `severity-stratified-output.md` |
| Does the agent need to express exactly where it looked vs where it didn't? | **Source Transparency** | `source-transparency.md` |
| Does the output need special handling (e.g., privileged, confidential)?| **Output Classification** | `output-classification.md` |
| Does the command produce written communications (emails, chat)? | **Multi-Dimensional Tone** | `multi-dimensional-tone.md` |

### Category 4: State and Knowledge
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Is there a massive amount of rules/rubrics separate from workflow logic? | **Skill-Command Two-Tier** | `skill-command-two-tier.md` |
| Does the feedback change based on whether the artifact is a Draft vs Final? | **Stage-Aware Feedback** | `stage-aware-feedback.md` |
| Is the domain highly regulated (laws, specific numeric thresholds)? | **Temporal Anchoring** | `temporal-anchoring.md` |
| Does the skill generate living documents (e.g., KBs, playbooks)? | **Lifecycle-Aware Knowledge** | `lifecycle-aware-knowledge.md` |
| Does the skill create artifact files? | **Artifact Lifecycle** | `artifact-lifecycle.md` |
| Does the skill synthesize an answer based on multiple competing sources?| **Tiered Source Authority**| `tiered-source-authority.md` |
| Should the command point the user to the next logical step in a workflow?| **Chained Command Invocation**| `chained-command-invocation.md` |

---

## How to Apply Loaded Patterns (JIT Injection)

If a pattern is triggered and loaded, you must perform **Progressive Disclosure Injection** into the generated skill:

1. **Do not bloat the `SKILL.md`** with the full theory of the pattern.
2. Create a lean reference file in the new skill's `references/` directory (e.g. `references/escalation-rules.md`).
3. Populate that new reference file with ONLY the concrete, domain-specific tables and rules requested by the pattern definition.
4. Add a markdown link in the new `SKILL.md` pointing to this newly generated reference file so the runtime agent knows to load it when executing.

This mechanism ensures that new skills possess L4 statefulness and safety boundaries without violating the 500-line `SKILL.md` context constraint.
## L4 Pattern Reference Catalog

Once a pattern is triggered by the decision tree above, load the corresponding file from `plugins reference/agent-skill-open-specifications/L4-pattern-definitions/` to learn how to explicitly construct the logic in the new skill.

### Root-Cause Category Selection (Anti-Symptom Triage)
- **File:** `anti-symptom-triage.md`
- **Use Case:** Triage, routing, and classification skills (support tickets, bug reports, feature requests).
- **Core Mechanic:** Agents naturally classify based on semantic similarity to user input (e.g., User says "Login button is broken" -> Agent classifies as "Account Issue")...

### L4 Artifact Lifecycle State Machine
- **File:** `artifact-lifecycle.md`
- **Use Case:** N/A
- **Core Mechanic:** N/A

### Chained Command Invocation via Offer-Next-Steps Blocks
- **File:** `chained-command-invocation.md`
- **Use Case:** Any plugin with multiple commands that logically connect (e.g., triage -> escalate, or research -> document).
- **Core Mechanic:** Commands should not be dead ends. Instead of presenting the output and stopping, every command should act as a node in a workflow graph, explicitly su...

### L4 Chained Commands / Workflow Graphs
- **File:** `chained-commands.md`
- **Use Case:** N/A
- **Core Mechanic:** N/A

### Complexity-Tiered Output Templating
- **File:** `complexity-tiered-output.md`
- **Use Case:** Analytical commands, code generation, or query responses where the user might ask a simple question ("How many rows?") or a complex one ("What is the weekly revenue trend over the past year?").
- **Core Mechanic:** Proactively classify the query complexity *before* generating output, and select a fundamentally different output structure (template) based on that t...

### Conditional Step Inclusion
- **File:** `conditional-step-inclusion.md`
- **Use Case:** Multi-step workflows that can be optionally "supercharged" with extra tool integrations, but must run successfully even if those tools are missing.
- **Core Mechanic:** Rather than embedding messy `if/else` logic deep inside workflow steps, evaluate tool availability at the **Step Header** level. If the required tool ...

### Tool-Agnostic Connector Placeholders (`~~category`)
- **File:** `connector-placeholders.md`
- **Use Case:** When a skill needs to interact with external systems (like Figma, Linear, Notion, etc.) but must remain portable and decoupled from specific enterprise tooling choices.
- **Core Mechanic:** Never hardcode specific application names (e.g., "Pull from Figma", "Search Confluence") inside a command's workflow logic. Instead, abstract the tool...

### Standalone + Supercharged Dual-Mode Degradation
- **File:** `dual-mode-degradation.md`
- **Use Case:** Ensuring a plugin remains fully functional and useful even if the user operates in an environment with no MCP tool connections, while explicitly surface "power user" capabilities if tools *are* connected.
- **Core Mechanic:** Agent workflows should never be binary (either requiring a tool or ignoring tools entirely). Every command must be designed to gracefully degrade by o...

### The Dual-Mode Meta-Skill (Bootstrap → Iteration)
- **File:** `dual-mode-meta-skill.md`
- **Use Case:** Complex domains where the agent needs to generate its own contextual reference files or even scaffold out entirely new skills dynamically.
- **Core Mechanic:** A tool that doesn't just execute logic, but *manages the creation of other tools and skills*. It operates in two explicit lifecycle modes declared in ...

### L4 Escalation Taxonomy
- **File:** `escalation-taxonomy.md`
- **Use Case:** N/A
- **Core Mechanic:** N/A

### Graduated Autonomy Routing
- **File:** `graduated-autonomy.md`
- **Use Case:** Any workflow that handles tasks of varying risk levels, where low-risk actions can be fully automated but high-risk actions require human oversight.
- **Core Mechanic:** Do not simply classify issues (e.g., High vs. Low priority). Classification without action is incomplete. Instead, map the risk classification directl...

### Lifecycle-Aware Knowledge Management
- **File:** `lifecycle-aware-knowledge.md`
- **Use Case:** Skills that produce durable artifacts like documentation, runbooks, templates, or knowledge base articles.
- **Core Mechanic:** Treat artifacts not as static files, but as living documents with an explicit state machine and scheduled maintenance. This prevents documentation rot...

### Multi-Dimensional Tone Configuration
- **File:** `multi-dimensional-tone.md`
- **Use Case:** Skills that draft communications on behalf of the user (emails, PRs, support responses, public statements).
- **Core Mechanic:** "Be empathetic and professional" is too vague. Tone should be configured as a multi-dimensional matrix, typically intersecting *Situation Type* with *...

### Multi-Modal Input Normalization
- **File:** `multi-modal-routing.md`
- **Use Case:** Commands that accept external context (images, code files, design URLs, database schemas) and must deterministically route the input based on what the user provided.
- **Core Mechanic:** Agents natively struggle with input ambiguity. If a command simply says "Review the design", the agent might hallucinate a design, politely decline, o...

### Cross-Tool Evidence Enrichment (Multi-Source Synthesis)
- **File:** `multi-source-synthesis.md`
- **Use Case:** Complex analysis commands that can pull context from multiple upstream systems and push outputs to multiple downstream systems simultaneously.
- **Core Mechanic:** When defining the `## If Connectors Available` section, do not write generic "use tools if available" blocks. Instead, explicitly assign one of three ...

### Output Classification Tagging
- **File:** `output-classification.md`
- **Use Case:** Plugins that generate sensitive content, legal drafts, security audits, or any artifact that requires special handling by downstream systems or users.
- **Core Mechanic:** Do not assume the user will remember how to handle the artifact the agent generates. The agent should explicitly tag its own output with handling meta...

### Priority-Ordered Source Scanning
- **File:** `priority-ordered-scanning.md`
- **Use Case:** Commands that search for entities across multiple systems (e.g., searching for a "Customer" in CRM, Billing, Support, and Email).
- **Core Mechanic:** When querying multiple systems, do not treat all systems as equally authoritative. A contract in a CLM system supersedes an off-hand mention in a Slac...

### Quantification Enforcement in Analysis
- **File:** `quantification-enforcement.md`
- **Use Case:** Research synthesis, data analysis, user feedback processing, or any command where the agent summarizes qualitative or quantitative data.
- **Core Mechanic:** Agents tend to generate confident-sounding prose that conflates observation with interpretation ("The button is confusing" vs "5 users clicked the wro...

### Severity-Stratified Output Schema with Emoji Triage
- **File:** `severity-stratified-output.md`
- **Use Case:** Review, audit, compliance, or critique commands that produce a list of findings or issues for a human to action.
- **Core Mechanic:** Never output a flat list of issues. Instead, embed a strict, three-tier triage system directly into the markdown output template, using emoji to creat...

### Skill–Command Two-Tier Knowledge Architecture
- **File:** `skill-command-two-tier.md`
- **Use Case:** Large domains (e.g., UX Design, Legal Compliance, Security Auditing) where complex declarative knowledge (rubrics, principles, laws) needs to be separated from procedural workflow logic (slash commands, input routing).
- **Core Mechanic:** Do not conflate "what the agent knows" with "what the agent does." Separate the bundle into two distinct tiers:

### L4 Tiered Source Authority
- **File:** `source-authority.md`
- **Use Case:** N/A
- **Core Mechanic:** N/A

### Source Transparency Declaration
- **File:** `source-transparency.md`
- **Use Case:** Any command that performs research, dependency analysis, or synthesis across multiple systems or files.
- **Core Mechanic:** When an agent returns a "Not Found" result, the user does not know if the artifact actually doesn't exist, or if the agent simply failed to check the ...

### Stage-Aware Feedback Modulation
- **File:** `stage-aware-feedback.md`
- **Use Case:** Any evaluation, review, or critique skill where the utility of the feedback depends heavily on *when* the artifact is being reviewed (e.g., Early Draft vs. Final Polish).
- **Core Mechanic:** Instruct the agent to modulate its cognitive evaluation mode by adding a temporal dimension to the input context. The agent must first classify the "l...

### Structured Output Templates as Agent Contracts
- **File:** `structured-output-contracts.md`
- **Use Case:** Every agent command that produces an artifact or report for a user to read.
- **Core Mechanic:** Prose instructions like "give me a thorough report with sections" produce wildly inconsistent outputs across different LLM runs. To guarantee determin...

### Sub-Action Command Multiplexing
- **File:** `sub-action-multiplexing.md`
- **Use Case:** A unified domain (e.g., "Design Systems" or "Database Migrations") that requires multiple distinct operations, each with totally different output structures, but which shouldn't pollute the global namespace with a dozen separate slash commands.
- **Core Mechanic:** Instead of creating `/audit-design-system`, `/document-component`, and `/extend-pattern`, create a single command namespace (`/design-system`) that mu...

### Statutory Temporal Anchoring
- **File:** `temporal-anchoring.md`
- **Use Case:** Compliance, Legal, Security, or heavily regulated domains where the "truth" changes over time based on external regulations.
- **Core Mechanic:** Domain knowledge codified in a `SKILL.md` degrades over time. If a skill states "Breach notification is required within 72 hours," it becomes silently...

### Tiered Source Authority with Propagated Confidence
- **File:** `tiered-source-authority.md`
- **Use Case:** Research, analysis, or synthesis skills where the agent must evaluate the trustworthiness of evidence before presenting an answer.
- **Core Mechanic:** This is an evolution of Priority-Ordered Source Scanning. It doesn't just dictate search order; it mathematically links the **quality of the source** ...


