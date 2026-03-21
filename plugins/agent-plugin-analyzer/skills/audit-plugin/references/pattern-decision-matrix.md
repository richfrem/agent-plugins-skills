# 39-Pattern L4 Architectural Decision Matrix
> **Standard Last Validated:** 2026-03-03

A reference for deciding when and how to incorporate advanced L4 architectural and state management patterns into skills. Used by `create-skill` and `create-plugin` during the design phase to selectively load deep context only when needed.

---

## Pattern Decision Tree

Not every skill needs complex architectural patterns. Use this tree during the discovery phase to determine which patterns to inject.

**CRITICAL RULE**: Do not explain the theory of these patterns to the user. Ask the diagnostic question. If the user answers YES, **MUST** load the corresponding markdown definition from `~~l4-pattern-catalog` (see ./CONNECTORS.md).

### Category 1: Input and Routing
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Does the skill interact with external systems (Jira, Figma, etc.)? | **Connector Placeholders** | `connector-placeholders.md` |
| Should the skill work with limited functionality without tools connected? | **Dual-Mode Degradation** | `dual-mode-degradation.md` |
| Does the skill take complex text, URLs, or files as input context? | **Multi-Modal Routing** | `multi-modal-routing.md` |
| Does the user report surface symptoms that need root-cause diagnosis? | **Anti-Symptom Triage** | `anti-symptom-triage.md` |
| Does the command group several sub-operations that have different outputs? | **Sub-Action Multiplexing** | `sub-action-multiplexing.md` |
| Does the command require user input upstream where asking questions mid-flight hurts UX? | **Pre-Execution Input Manifest** | `pre-execution-input-manifest.md` |
| Does the skill share overlapping keywords with generic tools, potentially causing discoverability issues? | **Multi-Variant Trigger Optimizer** | `multi-variant-trigger-optimizer.md` |
| Does the skill inherently struggle with undertriggering due to generic namespace intent vs actual semantic queries? | **Trigger Description Optimization Loop** | `../scripts/improve_description.py` (Source: Anthropic `skill-creator`) |

### Category 2: Execution and Safety
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Is there a mix of low-risk and high-risk actions in this domain? | **Graduated Autonomy** | `graduated-autonomy.md` |
| Can the workflow trigger potentially dangerous or unrecoverable actions? | **Escalation Taxonomy** | `escalation-taxonomy.md` |
| Are there multiple tools, where failure of one shouldn't crash the workflow? | **Conditional Step Inclusion** | `conditional-step-inclusion.md` |
| Does the agent query multiple systems of differing truthfulness? | **Priority-Ordered Scanning** | `priority-ordered-scanning.md` |
| Does the command analyze or synthesize data across multiple systems? | **Multi-Source Synthesis** | `multi-source-synthesis.md` |
| Is this a meta-skill designed to bootstrap or append to other skills? | **Dual-Mode Meta-Skill** | `dual-mode-meta-skill.md` |
| Are we executing an irreversible workflow where failure under stress is fatal? | **Pre-Committed Rollback Contract** | `pre-committed-rollback-contract.md` |
| Is the sequence of execution critical, but prone to human error? | **Pre-Execution Workflow Commitment Diagram** | `pre-execution-workflow-commitment-diagram.md` |
| Does the resulting artifact govern an ongoing workflow spanning multiple organizational roles? | **Multi-Actor Operational Coordination Manifest** | `multi-actor-operational-coordination-manifest.md` |
| Will the agent's natural sycophancy (agreeableness) ruin the analysis? | **Adversarial Objectivity Constraint** | `adversarial-objectivity-constraint.md` |
| Is the command modifying constrained additive resources (dashboards, capacity)? | **Zero-Sum Addition Gate** | `zero-sum-addition-gate.md` |
| Is there a minimum compliance safety standard that must never be bypassed regardless of the execution path or tool availability? | **Mode-Invariant Compliance Gate** | `mode-invariant-compliance-gate.md` |
| Is the primary method for the task highly brittle or prone to edge-case failures (e.g. math, geometric extraction)? | **Highly Procedural Fallback Trees** | `highly-procedural-fallback-trees.md` |
| Does the skill write code, configurations, or formulas that can be definitively proven broken by a compiler or engine evaluation? | **Delegated Constraint Verification Loop** | `delegated-constraint-verification-loop.md` |
| Does the skill write executable code or loops destined to run directly on the client/browser? | **Client-Side Compute Sandbox Constraint** | `client-side-compute-sandbox-constraint.md` |
| Does the generation output directly to a working directory where mistaken rollback is impossible without git reset? | **Iteration Directory Isolation** | `iteration-directory-isolation.md` (Source: Anthropic `skill-creator`) |
| Is critical timing or token benchmark data emitted asynchronously via system notifications rather than final outputs? | **Asynchronous Benchmark Metric Capture** | `asynchronous-benchmark-metric-capture.md` (Source: Anthropic `skill-creator`) |

### Category 3: Output and Contracts
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Does the command generate a report, audit, or synthesis? | **Structured Output Contracts** | `structured-output-contracts.md` |
| Does the command output differ vastly based on complex vs simple requests? | **Complexity-Tiered Output** | `complexity-tiered-output.md` |
| Could the agent hallucinate claims from vague qualitative data? | **Quantification Enforcement** | `quantification-enforcement.md` |
| Does the command output a list of issues or audit findings? | **Severity-Stratified Output** | `severity-stratified-output.md` |
| Does the agent need to understand context incrementally rather than dumping 50 files into memory at once? | **Progressive Disclosure** | `progressive-disclosure.md` |
| Does the plugin use placeholders that need to be universally understood by distributed users? | **Category-Semantic Deferred Tool Binding** | `category-semantic-deferred-tool-binding.md` |
| Does the artifact's existing configuration state determine what the workflow should do? | **Artifact-State-Interrogative Routing** | `artifact-state-interrogative-routing.md` |
| Does the output need special handling (e.g., privileged, confidential)?| **Output Classification** | `output-classification.md` |
| Does the command produce written communications (emails, chat)? | **Multi-Dimensional Tone** | `multi-dimensional-tone.md` |
| Is the output a priority ranking that requires mathematical determinism? | **Embedded Deterministic Scoring Formula** | `embedded-deterministic-scoring-formula.md` |
| Will different audiences downstream need different facts omitted entirely? | **Audience-Segmented Information Filtering** | `audience-segmented-information-filtering.md` |
| Are there known failure modes (anti-patterns) practitioners make in this domain? | **Anti-Pattern Vaccination** | `anti-pattern-vaccination.md` |
| Does the tool produce a strategic analysis that requires the user to decide? | **Mandatory Counterfactual Scenario Templating** | `mandatory-counterfactual-scenario-templating.md` |
| Does the primary stakeholder lack context needed to understand raw metrics? | **Impact-Translated Status** | `impact-translated-status.md` |
| Does the organization have an expected statistical distribution or budget curve for these entities? | **Population-Normative Distribution Constraint** | `population-normative-distribution-constraint.md` |
| Does the LLM have a strong innate bias to solve the problem the "wrong" way (e.g., calculating math in Python instead of writing a formula)? | **Negative Instruction Constraint** | `negative-instruction-constraint.md` |
| Does the skill evaluate metrics that require external industry benchmarks rather than the agent's subjective judgment? | **Category-Calibrated Benchmark Anchoring** | `category-calibrated-benchmark-anchoring.md` |
| Will the generated output be consumed by fresh readers lacking the agent's conversational context? | **Tainted Context Cleanser** | `tainted-context-cleanser.md` |
| Does the output's quality or performance need to be provably benchmarked against baselines? | **Rigorous Benchmarking & Grading Loop** | `../scripts/run_loop.py` |
| Does the command generate full UI artifacts (HTML/SVG) where external asset injection poses a security risk? | **Artifact Generation XSS Compliance Gate** | `artifact-generation-xss-compliance-gate.md` |
| Are generated UI artifacts or whole file hierarchies difficult for the user to review purely in code before saving? | **Local Interactive Output Viewer Loop** | `../scripts/generate_review.py` (Source: Anthropic `skill-creator`) |
| Does the interaction pop local browsers or servers that will crash in remote VMs or headless subagent loops? | **UI Degradation Constraint** | `ui-degradation-constraint.md` (Source: Anthropic `skill-creator`) |

### Category 4: State and Knowledge
| Diagnostic Question | Required Pattern | File |
|---------------------|------------------|------|
| Is there a massive amount of rules/rubrics separate from workflow logic? | **Skill-Command Two-Tier** | `skill-command-two-tier.md` |
| Does the feedback change based on whether the artifact is a Draft vs Final? | **Stage-Aware Feedback** | `stage-aware-feedback.md` |
| Is the domain highly regulated (laws, specific numeric thresholds)? | **Temporal Anchoring** | `temporal-anchoring.md` |
| Does the skill generate living documents (e.g., KBs, playbooks)? | **Lifecycle-Aware Knowledge** | `lifecycle-aware-knowledge.md` |
| Does the skill create artifact files? | **Artifact Lifecycle** | `artifact-lifecycle.md` |
| Should branding, styling, or tone rules be shared globally across multiple distinct generation skills? | **Passive Style Injection Payload** | `passive-style-injection-payload.md` |
| Does the workflow require complex knowledge gathering from multiple sources? | **Graduated Source-Attributed Knowledge Elicitation** | `graduated-source-attributed-elicitation.md` |
| Is there a risk that the user will be overwhelmed by technical file-path/YAML minutiae? | **Dual-Register Communication Enforcement** | `dual-register-communication-enforcement.md` |
| Should the command point the user to the next logical step in a workflow?| **Chained Command Invocation**| `chained-command-invocation.md` |
| Do the commands require configuration that is tedious to supply on every run? | [Persistent Plugin Configuration](persistent-plugin-configuration.md) |
| Does the workflow happen in recurring, time-bounded periods where the previous output is the next input? | [Cyclical State Propagation Contract](cyclical-state-propagation-contract.md) |
| Should the generated artifact structurally record its own procedural history? | **Artifact-Embedded Execution Audit Trail** | `artifact-embedded-execution-audit-trail.md` |
| Does the skill require orchestrating against an external SDK or schema that updates frequently? | **Dynamic Specification Fetching** | `dynamic-specification-fetching.md` |
| Does the command generate randomized or chaotic output that a user might want to exactly replicate later? | **Explicit Seed-Anchored Determinism** | `explicit-seed-anchored-determinism.md` |

---

## How to Apply Loaded Patterns (JIT Injection)

If a pattern is triggered and loaded, you must perform **Progressive Disclosure Injection** into the generated skill:

1.  **Do not bloat the `./SKILL.md`** with the full theory of the pattern.
2.  Create a lean reference file in the new skill's `references/` directory (e.g. `references/escalation-rules.md`).
3.  Populate that new reference file with ONLY the concrete, domain-specific tables and rules requested by the pattern definition.
4.  Add a markdown link in the new `./SKILL.md` pointing to this newly generated reference file so the runtime agent knows to load it when executing.

This mechanism ensures that new skills possess L4 statefulness and safety boundaries without violating the 500-line `./SKILL.md` context constraint.
## L4 Pattern Reference Catalog

Once a pattern is triggered by the decision tree above, load the corresponding file from `~~l4-pattern-catalog` (see ./CONNECTORS.md) to learn how to explicitly construct the logic in the new skill.

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
- **Core Mechanic:** Commands should not be dead ends. Instead of presenting the output and stopping, every command should act as a node in a workflow graph, explicitly suggesting the next logical steps.
- **Evolution:** *Artifact-Type Expansion* — The chain branches out laterally into a new artifact domain entirely.

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
- **Core Mechanic:** Instead of creating `/audit-design-system`, `/document-component`, and `/extend-pattern`, create a single command namespace (`/design-system`) that multiplexes sub-actions based on arguments.
- **Evolution:** *Hierarchical Default Composition* — The sub-actions are both independently addressable and collectively composable into a super-action defaulting route.

### Statutory Temporal Anchoring
- **File:** `temporal-anchoring.md`
- **Use Case:** Compliance, Legal, Security, or heavily regulated domains where the "truth" changes over time based on external regulations.
- **Core Mechanic:** Domain knowledge codified in a `./SKILL.md` degrades over time. If a skill states "Breach notification is required within 72 hours," it becomes silently...

### Tiered Source Authority with Propagated Confidence
- **File:** `tiered-source-authority.md`
- **Use Case:** Research, analysis, or synthesis skills where the agent must evaluate the trustworthiness of evidence before presenting an answer.
- **Core Mechanic:** This is an evolution of Priority-Ordered Source Scanning. It doesn't just dictate search order; it mathematically links the **quality of the source** to the **confidence of the claim**.

### Action-Forcing Output with Deadline Attribution
- **File:** `action-forcing-output-with-deadline-attribution.md`
- **Use Case:** Status reports, cross-functional readouts, or technical reviews delivered to stakeholders who possess unblocking authority.
- **Core Mechanic:** The output template includes a mandatory `### Decisions Needed` table, separated from Risks, enforcing deadlines and pre-loaded agent recommendations.

### Adversarial Objectivity Constraint
- **File:** `adversarial-objectivity-constraint.md`
- **Use Case:** Competitive analysis, risk assessment, performance reviews, or code review where an overly positive/agreeable response destroys analytical utility.
- **Core Mechanic:** Explicitly instructing the agent to counteract its natural bias toward sycophancy (e.g., forcing it to seek disconfirming evidence or acknowledge competitor strengths).

### Anti-Pattern Vaccination
- **File:** `anti-pattern-vaccination.md`
- **Use Case:** Any generation domain with well-documented, recurring practitioner mistakes (e.g., writing requirements, API schemas).
- **Core Mechanic:** Embedding an explicit list of known failure modes directly into the prompt logic, forcing the agent to screen its draft against those specific errors before outputting.

### Artifact-Embedded Execution Audit Trail
- **File:** `artifact-embedded-execution-audit-trail.md`
- **Use Case:** Recurring procedures or operational processes (runbooks, playbooks, SOPs) where capturing operational intelligence across multiple runs is as important as the procedure itself.
- **Core Mechanic:** Generating an empty `### Execution Log` table at the bottom of the artifact designed to be appended to by operators on future runs.

### Audience-Segmented Information Filtering
- **File:** `audience-segmented-information-filtering.md`
- **Use Case:** Stakeholder updates, release notes, and status reports distributed to varied audiences.
- **Core Mechanic:** An `Audience Policy Matrix` establishing what facts are explicitly disclosed or withheld per audience type, acting as an information checkpoint rather than a stylistic formatter.

### Cyclical State Propagation Contract
- **File:** `cyclical-state-propagation-contract.md`
- **Use Case:** Workflows occurring in recurring, time-bounded periods (performance reviews, OKRs, multi-stage audits).
- **Core Mechanic:** The final output of computing cycle N is geometrically structured to be the precise, required input for computing cycle N+1, explicitly linking asynchronous workflows over time.

### Embedded Deterministic Scoring Formula
- **File:** `embedded-deterministic-scoring-formula.md`
- **Use Case:** Backlog grooming, tech debt prioritization, lead qualification, or any output where independent runs must produce the exact same relative ranking.
- **Core Mechanic:** Hardcoding a strict mathematical formula (e.g., `Priority = (Impact + Risk) x (6 - Effort)`) directly into the skill to eliminate subjective priority sorting.

### Mandatory Counterfactual Scenario Templating
- **File:** `mandatory-counterfactual-scenario-templating.md`
- **Use Case:** Planning, triage, and strategic analysis commands where the user expects to make a decision based on the output.
- **Core Mechanic:** Mandating a `### Scenarios` tabular section as a top-level requirement that defines exactly which futures must be calculated (forcing a "Do nothing" vs additive/subtractive options).

### Multi-Actor Operational Coordination Manifest
- **File:** `multi-actor-operational-coordination-manifest.md`
- **Use Case:** Cross-functional workflows where different teams must execute distinct actions in sequence (e.g., onboarding, go-to-market string, deployments).
- **Core Mechanic:** A single document structurally labelled with distinct organizational action roles so that the artifact itself acts as the localized distribution pipeline downstream.

### Persistent Plugin Configuration
- **File:** `persistent-plugin-configuration.md`
- **Use Case:** Plugins whose commands require stable, personalized context (org structure, tech stack) that is tedious to supply on every run.
- **Core Mechanic:** Commands depend on a local JSON settings file. Rather than a purely stateless HITL tax via questions, the missing config triggers a one-time onboarding interview that saves to disk for future sessions.

### Population-Normative Distribution Constraint
- **File:** `population-normative-distribution-constraint.md`
- **Use Case:** Tasks collecting evaluations, ratings, or resource requests over large population scales where human optimization biases deviate from aggregate organizational capacities.
- **Core Mechanic:** Embedding statistical top-down expected distributions alongside user-provided values in the actual generated template to create a macro-calibration check.

### Pre-Committed Rollback Contract
- **File:** `pre-committed-rollback-contract.md`
- **Use Case:** Any command where failure carries high consequences and real-time human judgment under stress is dangerous (deployments, migrations).
- **Core Mechanic:** Generating a mandatory `### Rollback Triggers` block with placeholder thresholds that the user must fill in, pre-defining explicit abort criteria *before* the action begins.

### Pre-Execution Input Manifest
- **File:** `pre-execution-input-manifest.md`
- **Use Case:** Data-heavy commands where interactive piecemeal generation of missing data hurts UX for power users.
- **Core Mechanic:** A declarative checklist presented *before* the output template that explicitly tells the user what data is required, shifting cognitive load upstream so users can prep in one shot.

### Pre-Execution Workflow Commitment Diagram
- **File:** `pre-execution-workflow-commitment-diagram.md`
- **Use Case:** Multi-phase commands where users benefit from understanding the whole process upfront or where the agent proves prone to skipping steps.
- **Core Mechanic:** Every command opens with an ASCII flowchart visual diagram mapping the process steps before any logic evaluates, committing the agent structurally to that process.

### Concept-Dialect Translation Table
- **File:** `concept-dialect-translation-table.md`
- **Use Case:** Integrating external systems (like Notion or Jira) whose internal terminology differs from your domain terminology.
- **Core Mechanic:** A literal Markdown table in `./CONNECTORS.md` that maps internal domain concepts to external system equivalents, so the agent can naturally "speak" the target API's dialect.

### Category-Semantic Deferred Tool Binding
- **File:** `category-semantic-deferred-tool-binding.md`
- **Use Case:** Writing portable templates expected to be deployed across vastly different technical ecosystems.
- **Core Mechanic:** Using human-readable categories as `~~` placeholder tokens, effectively turning the placeholder itself into the discovery keyword for registry lookups.

### Artifact-State-Interrogative Routing
- **File:** `artifact-state-interrogative-routing.md`
- **Use Case:** Workflows that modify existing plugins or configurations that may exist in various lifecycles.
- **Core Mechanic:** Executing a fast read-only inspection command against the artifact before user interaction to determine its lifecycle state and hard-route the workflow mode.

### Dual-Register Communication Enforcement
- **File:** `dual-register-communication-enforcement.md`
- **Use Case:** Technical manipulation workflows for non-technical users.
- **Core Mechanic:** Forcing a strict boundary where the agent uses technical paths/tokens internally, but ONLY ever emits semantic, capability-framed language in user-facing artifacts and summaries.

### Graduated Source-Attributed Knowledge Elicitation
- **File:** `graduated-source-attributed-elicitation.md`
- **Use Case:** Multi-step knowledge gathering processes.
- **Core Mechanic:** Searching systems in priority order to minimize questioning, and tracking exact provenance of every variable so the final summary proves *where* the agent learned the fact, guaranteeing transparency.

### Progressive Disclosure
- **File:** `progressive-disclosure.md`
- **Use Case:** Coping with large architectures or domain rules.
- **Core Mechanic:** Splitting knowledge out of the primary `./SKILL.md` (which is always loaded into context window) into `references/*.md`, mapped to specific triggers so they only load when strictly necessary.
- **Evolution:** *Tiered Progressive Disclosure with Explicit Budget Constraints* — Implementing hard token/word count budgets per progressive disclosure tier.

### Zero-Sum Addition Gate
- **File:** `zero-sum-addition-gate.md`
- **Use Case:** Sprint planning, roadmap management, staffing changes, or any system where resources are finite.
- **Core Mechanic:** A pre-action capacity constraint that evaluates resource limits and forbids the agent from blindly executing an additive operation without forcing a subtractive trade-off decision from the user.

### Mode-Invariant Compliance Gate
- **File:** `mode-invariant-compliance-gate.md`
- **Use Case:** Domains where missing a safety/compliance step due to a conditional logic skip is unacceptable.
- **Core Mechanic:** A structurally isolated block of mandatory checks that are declared immune to all conditional execution pathways, forming a compliance floor that runs on every invocation.

### Category-Calibrated Benchmark Anchoring
- **File:** `category-calibrated-benchmark-anchoring.md`
- **Use Case:** Evaluating metrics against industry-standard categories rather than relying on generative AI hallucination.
- **Core Mechanic:** Providing a hardcoded tabular lookup matrix of industry benchmarks. The agent's task shifts from subjective evaluation to matrix lookup and comparison.
