# Pattern Catalog

A living catalog of reusable design patterns extracted from plugin and skill analyses. This catalog grows with every analysis — new patterns are appended by the `synthesize-learnings` skill.

## Governance Model

### Pattern Lifecycle States
| State | Meaning | Criteria to Advance |
|-------|---------|-------------------|
| `proposed` | Observed in a single analysis, not yet validated | Must be found in ≥1 plugin |
| `validated` | Confirmed across ≥2 independent plugins | Quality rated "good" or better in both |
| `canonical` | Recommended best practice, embedded in scaffolders | Adopted into `create-skill` or `create-plugin` templates |
| `deprecated` | Superseded or no longer aligned with ecosystem standards | Marked with replacement pattern reference |

### Required Fields Per Pattern
Every pattern entry MUST include:
- **Category**: Architectural / Execution / Content / Knowledge / Interaction / Integration
- **Lifecycle**: `proposed` / `validated` / `canonical` / `deprecated`
- **Confidence**: High (≥3 plugins) / Medium (2 plugins) / Low (1 plugin)
- **First Seen In**: Plugin name and analysis date
- **Frequency**: Count of plugins observed using this pattern
- **Description**: What it is and how it works
- **When to Use**: Conditions where this pattern applies
- **Example**: Concrete implementation reference

### Deduplication Rules
Before adding a new pattern:
1. Check if an existing pattern covers ≥80% of the same behavior
2. If so, update the existing pattern's frequency and add the new source
3. If the new pattern is a meaningful variant, add it as a sub-entry under the parent
4. Never add near-duplicates as separate top-level patterns

### Provenance Tracking
The changelog at the bottom of this file tracks when patterns were added, promoted, or deprecated.

---

## Architectural Patterns

### Standalone vs Supercharged
- **Category**: Architectural
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 5+ plugins
- **First Seen In**: Anthropic sales, customer-support, engineering plugins
- **Description**: Every command and skill works without any MCP integrations (standalone mode), but becomes dramatically more powerful when tools are connected (supercharged). The README documents both paths in a comparison table.
- **When to Use**: Any plugin that can optionally integrate with external tools
- **Example**: Sales `call-prep` skill works with user-provided context, but auto-pulls CRM data when Salesforce connector is available

### Connector Abstraction (`~~category`)
- **Category**: Architectural
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 5+ plugins
- **First Seen In**: Anthropic sales, customer-support, engineering plugins
- **Description**: Use `~~category` placeholders (e.g., `~~project tracker`, `~~chat`, `~~source control`) instead of hardcoding specific tool names. A `CONNECTORS.md` file maps categories to concrete tool options. Makes plugins tool-agnostic.
- **When to Use**: Any plugin intended for distribution across organizations using different tool stacks
- **Example**: `~~project tracker` could be Linear, Jira, or Asana depending on the user's setup

### Meta-Skills (Skills That Generate Skills)
- **Category**: Architectural / Meta
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic `data-context-extractor`, `create-cowork-plugin`
- **Description**: A skill whose primary output is another skill. Follows a guided interview process to extract domain knowledge, then generates a complete skill directory (SKILL.md + references + scripts).
- **When to Use**: When the same skill structure needs to be customized per organization/domain
- **Example**: `data-context-extractor` interviews analysts about their data warehouse, then generates a customized `[company]-data-analyst` skill with entity definitions, metrics, and SQL patterns

### Modular Building Blocks
- **Category**: Architectural / Structural
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic bio-research `single-cell-rna-qc`
- **Description**: Providing a "complete pipeline" convenience CLI wrapper script for standard/default executions, alongside separated "modular building block" Python APIs in a core module. The skill explicitly delegates standard requests to the CLI and edge-case/custom requests to chaining the Python APIs natively.
- **When to Use**: High-variability computational pipelines where a standard CLI covers 80% of use cases but fails on 20% edge cases that require power-user composability.
- **Example**: Supplying `scripts/qc_analysis.py` for default executions and `scripts/qc_core.py` for custom Python chains in the environment.

### Multi-Mode Commands with Mode Dispatch
- **Category**: Architectural
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `brief`
- **Description**: A single command implements completely distinct workflows dispatched by a simple argument (`daily | topic | incident`). Each mode changes not just the template, but the agent's temporal execution posture (speed vs thoroughness).
- **When to Use**: When a skill covers distinct but highly related use cases that differ in urgency or scope.
- **Example**: `/brief incident` values speed and available data; `/brief topic` defaults to thorough research and external counsel recommendation.

---

## Execution Patterns

### Phase-Based Workflows
- **Category**: Execution
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 5+ plugins
- **First Seen In**: Universal across Anthropic plugins
- **Description**: Skills define numbered phases executed sequentially. Each phase has clear inputs, actions, and outputs. Common pattern: Discovery → Planning → Execution → Delivery.
- **When to Use**: Any multi-step workflow that benefits from structure
- **Example**: `create-cowork-plugin` uses 5 phases: Discovery → Component Planning → Design → Implementation → Package

### Bootstrap + Iteration Dual-Mode
- **Category**: Execution
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic `data-context-extractor`
- **Description**: Skill has two distinct modes: Bootstrap (create from scratch) and Iteration (enhance existing). The trigger description specifies both modes with separate trigger phrases.
- **When to Use**: Any skill that both creates new artifacts AND improves existing ones
- **Example**: Bootstrap mode creates a new data skill; Iteration mode adds domain-specific reference files to an existing one

### Tiered Execution Strategies
- **Category**: Execution
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic bio-research `scvi-tools`
- **Description**: Multiple execution tiers based on complexity or data availability. Basic tier uses defaults, intermediate tier requires user input, advanced tier uses full customization.
- **When to Use**: When the same process has varying complexity levels
- **Example**: scRNA-seq analysis with basic QC, standard integration, and advanced batch correction tiers

### Fallback Chains
- **Category**: Execution
- **Lifecycle**: `validated`
- **Confidence**: High
- **Frequency**: 3+ plugins
- **First Seen In**: Anthropic sales, customer-support plugins
- **Description**: Try the ideal approach first (MCP tool), fall back to alternatives (manual input), and clearly communicate which path is being taken.
- **When to Use**: When MCP tools may or may not be available
- **Example**: Try `~~CRM` to pull contact data → fall back to asking user to paste it

---


### Graduated Autonomy Routing
- **Category**: Execution / Autonomy
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `contract-review`
- **Description**: Defines different behavioral bounds (auto-approve vs flag vs escalate) based on the classification severity, rather than just classifying and stopping. Shrinks the agent's autonomy as risk increases.
- **When to Use**: When dealing with variable risk-levels that define whether the agent can act independently.
- **Example**: GREEN = execute; YELLOW = ask for permission; RED = halt and inform user.

### Escalation Trigger Taxonomy
- **Category**: Execution / Safety
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `canned-responses`
- **Description**: A two-level trigger system (universal + category-specific) that interrupts a workflow with a 5-step response protocol (Stop, Alert, Explain, Recommend, Offer Draft).
- **When to Use**: Workflows that generate external-facing outputs.
- **Example**: Before generating a response, check if matter involves litigation; if so, Stop, Alert user, Explain risk, Recommend counsel, Offer draft.

### Conditional Step Inclusion
- **Category**: Execution / Flow
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `vendor-check`
- **Description**: Workflow steps explicitly state "If Connected" in their headers to gracefully degrade when tools (like CLMs or MCP servers) are missing, instead of using buried if/else conditionals or fallback chains.
- **When to Use**: Workflows dependent on multiple external tools.
- **Example**: `### Step 2: CLM Routing (If Connected)`

### Self-Improving Workflow Loop
- **Category**: Execution / Evolution
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 2+ plugins
- **First Seen In**: Oracle Legacy `curate-inventories`, Anthropic legal `canned-responses`
- **Description**: Every execution of the workflow ends with a mandatory step requiring the agent to either fix a bug in a target script, clarify a confusing step in the workflow documentation, or create a ticket for a larger issue.
- **When to Use**: All complex orchestrations.
- **Example**: `You MUST strictly choose one action: Fix Code, Fix Docs, New Task, No Issues.`

## Content Patterns

### Severity/Classification Frameworks
- **Category**: Content
- **Lifecycle**: `validated`
- **Confidence**: High
- **Frequency**: 3+ plugins
- **First Seen In**: Anthropic customer-support `ticket-triage`, legal `contract-review`
- **Description**: Structured classification systems with clear criteria and response expectations per level. Visual aids like tables or color coding.
- **When to Use**: Any analysis or triage process requiring consistent categorization
- **Variants**:
  - Priority levels: P1 (critical) → P4 (low) with response time SLAs
  - Deviation severity: GREEN (acceptable) → YELLOW (negotiate) → RED (escalate)
  - SEV levels: SEV1 (all-hands) → SEV4 (next business day)
  - Confidence scores: High → Moderate → Low with hedging language

### Decision Tables
- **Category**: Content
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic data `data-visualization`
- **Description**: Tables mapping inputs to recommended outputs. Rows = scenarios/data types, columns = recommended approaches.
- **When to Use**: When selection logic can be captured in a matrix
- **Example**: Chart selection guide: "Trend over time → Line chart | Comparison across categories → Bar chart"

### Output Templates
- **Category**: Content
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 4+ plugins
- **First Seen In**: Anthropic sales `create-an-asset`, customer-support `knowledge-management`
- **Description**: Specific format templates for skill outputs. May include HTML for rich artifacts, markdown for reports, or structured formats for data.
- **When to Use**: When output consistency matters across invocations
- **Variants**:
  - HTML artifact templates (self-contained, inline CSS)
  - Markdown report templates with sections and tables
  - Redline format (Clause → Current → Proposed → Rationale → Priority → Fallback)
  - KB article templates (type-specific: troubleshooting, how-to, FAQ)

### Quality/Compliance Checklists
- **Category**: Content
- **Lifecycle**: `validated`
- **Confidence**: High
- **Frequency**: 3+ plugins
- **First Seen In**: Anthropic bio-research `instrument-data-to-allotrope`, data `data-visualization`
- **Description**: Checkbox lists at the end of skills ensuring completeness. Each check is specific and testable.
- **When to Use**: Any skill where output quality needs verification
- **Example**: "Before sharing visualization: Chart works without color, Text readable at standard zoom, Title describes insight"

### Negotiation Priority Tiers
- **Category**: Content
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `contract-review`
- **Description**: Three-tier prioritization: Must-Haves (deal breakers) → Should-Haves (strong preferences) → Nice-to-Haves (concession candidates). Strategy: lead with Tier 1, trade Tier 3 to win Tier 2.
- **When to Use**: Any analysis that requires prioritized recommendations
- **Example**: Contract redlines organized by negotiation priority with explicit concession strategy

### Confidence-Scored Answers
- **Category**: Content
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic enterprise-search `knowledge-synthesis`
- **Description**: Answers include confidence levels based on source freshness and authority. Language adjusts: direct statements for high confidence, hedged language for moderate, explicit caveats for low.
- **When to Use**: Any knowledge retrieval or analysis with varying certainty
- **Example**: "The team decided to use REST" (high) vs "Based on last month's discussion, the team was leaning toward REST" (moderate)

### Privilege / Confidentiality Marking Protocol
- **Category**: Content
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `legal-risk-assessment`
- **Description**: The agent automatically appends and evaluates metadata about how the output should be treated regarding sensitivity, distribution restrictions, and temporal validity.
- **When to Use**: Workflows handling PII, legal documentation, or infosec analysis.
- **Example**: `**Privileged**: [Yes/No - mark as attorney-client privileged if applicable]`

---

## Knowledge Patterns

### Progressive Disclosure via References
- **Category**: Knowledge
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 5+ plugins
- **First Seen In**: Universal across well-designed plugins
- **Description**: SKILL.md stays lean (<500 lines) with high-level guidance. Deep domain content lives in `references/` files loaded on-demand. References are one-level deep (never reference → sub-reference chains).
- **When to Use**: Always — this is a core Open Standards best practice
- **Example**: bio-research `scvi-tools` has 12 reference files covering different analysis types, each loaded only when relevant

### Dialect/Variant Reference Tables
- **Category**: Knowledge
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic data `sql-queries`
- **Description**: When a skill covers multiple variants of a tool/language/system, organize reference material by variant with consistent sections per variant.
- **When to Use**: Skills covering tools with multiple dialects or implementations
- **Example**: SQL queries skill has PostgreSQL, Snowflake, BigQuery, Redshift, and Databricks sections with matching subsections

### Playbook-Based Review
- **Category**: Knowledge
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `contract-review`
- **Description**: Review methodology based on a configurable playbook defining standard positions, acceptable ranges, and escalation triggers. Without a playbook, falls back to industry standards with clear labeling.
- **When to Use**: Any review/audit process where organizational standards vary
- **Example**: Contract review checks each clause against the org's negotiation playbook, classifying deviations as GREEN/YELLOW/RED

### Statutory Temporal Anchoring
- **Category**: Knowledge
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `compliance`
- **Description**: Explicitly pinning regulatory knowledge to specific versions, dates, and rule numbers (e.g. EU SCCs June 2021) directly within the SKILL instructions to prevent hallucination drift and make knowledge freshness auditable over time.
- **When to Use**: Skills making programmatic decisions based on versioned human laws, policies, or SLAs.
- **Example**: `Using current EU SCCs (**June 2021 version**) if applicable.`

---

## Interaction Design Patterns

### Guided Discovery Interview
- **Category**: Interaction
- **Lifecycle**: `canonical`
- **Confidence**: High
- **Frequency**: 4+ plugins
- **First Seen In**: Anthropic `data-context-extractor`, `create-cowork-plugin`
- **Description**: Before executing, the skill runs a structured interview to gather context. Questions follow a logical sequence: broad context → specific requirements → edge cases → confirmation. The skill does NOT proceed until the discovery is complete.
- **When to Use**: Any skill that needs to understand organizational context before generating outputs (meta-skills, config generators, domain-specific tools)
- **Example**: `data-context-extractor` asks: "What database platform?" → "What are the core entities?" → "What metrics matter most?" → "Any special naming?"
- **Question Types Used**: Open-ended, multiple-choice, yes/no confirmation

### Numbered Option Menus
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: High
- **Frequency**: 3+ plugins
- **First Seen In**: Anthropic partner-built/apollo `prospect`, engineering `code-review`
- **Description**: Present the user with clearly numbered options to choose from. Each option has a brief label and description. The user replies with just the number. Reduces ambiguity and speeds up interaction.
- **When to Use**: Any decision point where there are 3-7 discrete options
- **Example**:
  ```
  Choose an action:
  1. Deep-dive a specific company
  2. Export the full list as CSV
  3. Refine the search criteria
  4. Load leads into outreach sequence
  ```
- **Design Rules**: Keep to 3-7 options. Always include an "Other" or "Skip" escape hatch. Use consistent formatting across invocations.

### Progressive Questioning (Funnel)
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic `data-context-extractor`, customer-support `ticket-routing`
- **Description**: Start with broad, easy questions to build context, then progressively narrow to specific details. Each question informs which follow-up question is appropriate. Never ask a question whose answer could be inferred from a previous answer.
- **When to Use**: When the skill needs 5+ pieces of information from the user
- **Funnel Structure**:
  1. **Context** (broad): "What domain is this for?"
  2. **Scope** (medium): "Which systems are involved?"
  3. **Detail** (narrow): "What specific edge cases should we handle?"
  4. **Confirmation** (verify): "Here's what I understood — correct?"
- **Anti-Pattern**: Asking all questions at once in a wall of text

### Table-Based Option Presentation
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic engineering `system-design`, sales `competitive-intelligence`
- **Description**: When options have multiple dimensions (e.g., name + description + trade-offs), present them in a table rather than a flat list. Enables quick scanning and comparison.
- **When to Use**: When each option has 3+ attributes the user needs to compare
- **Example**:
  ```
  | # | Approach | Complexity | Risk | Speed |
  |---|----------|-----------|------|-------|
  | 1 | Full rewrite | High | Low | Slow |
  | 2 | Incremental migration | Medium | Medium | Medium |
  | 3 | Strangler fig pattern | Low | Low | Fast |
  ```

### Confirmation Gates
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: High
- **Frequency**: 3+ plugins
- **First Seen In**: Anthropic partner-built/apollo `prospect`, legal `contract-review`
- **Description**: Before executing irreversible or expensive operations, present a summary of what will happen and explicitly ask for confirmation. The gate includes: what will be done, the scope/cost, and a clear yes/no prompt.
- **When to Use**: Before API calls that consume credits, file modifications, bulk operations, or any action with side effects
- **Example**: "This will enrich 47 leads using 94 Apollo credits. Proceed? (yes/no)"

### Contextual Follow-Up Questions
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic `data-context-extractor`, sales `call-prep`
- **Description**: The next question dynamically adapts based on the previous answer. If the user says "PostgreSQL", ask about PostgreSQL-specific features. If the user says "Snowflake", ask about Snowflake-specific features. Branching logic is documented as decision trees in the SKILL.md.
- **When to Use**: When the skill covers multiple variants/paths and the questions differ per path
- **Example**: User picks "time series data" → skill asks about seasonality; User picks "categorical data" → skill asks about cardinality

### Smart Defaults with Override
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic `create-cowork-plugin`, bio-research `scvi-tools`
- **Description**: Suggest a recommended default for each parameter, but allow the user to override. Presents as: "I recommend X because Y. Would you like to go with X, or specify something different?"
- **When to Use**: When most users will want the same thing, but power users need customization
- **Example**: "I recommend using the standard QC thresholds (min_genes=200, min_cells=3). Override? (yes/no)"

### Inline Progress Indicators
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic engineering `standup`, productivity `task-management`
- **Description**: During multi-step workflows, emit brief status updates between phases so the user knows the skill is progressing. Uses emoji or formatted markers.
- **When to Use**: Any workflow with 3+ sequential phases that take time
- **Example**:
  ```
  ✅ Phase 1: Data loaded (47 records)
  ⏳ Phase 2: Enriching contacts...
  ✅ Phase 2: Enrichment complete (94 credits used)
  ⏳ Phase 3: Generating report...
  ```

### Output Format Negotiation
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic data `data-visualization`, sales `create-an-asset`
- **Description**: Before generating output, ask the user what format they want. Different formats serve different audiences. Options typically include: markdown report, HTML artifact, structured data (JSON/CSV), presentation slides, or inline summary.
- **When to Use**: When the same analysis can be consumed in multiple formats
- **Example**: "How would you like this delivered? (1) Inline summary (2) Full markdown report (3) Interactive HTML dashboard (4) CSV export"

### Recap-Before-Execute
- **Category**: Interaction
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic `create-cowork-plugin`, `data-context-extractor`
- **Description**: After the discovery phase, present a structured summary of everything gathered and ask the user to confirm before proceeding to execution. This catches misunderstandings before they cost tokens. Uses a clear "Here's what I heard" format.
- **When to Use**: Any skill with a discovery phase followed by a generation/execution phase
- **Example**:
  ```
  ## Recap
  - **Database**: PostgreSQL 14
  - **Core entities**: Users, Orders, Products
  - **Key metrics**: Revenue, DAU, Conversion Rate
  - **Naming convention**: snake_case

  Does this look right? (yes / adjust)
  ```

### Document-as-Input with Format Agnosticism
- **Category**: Interaction
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `review-contract`
- **Description**: Input blocks explicitly support fallback format modalities (File upload, URL link to cloud storage, or pasted text) and include a behavioral advisory for handling "long documents" (chunking) to protect context limits.
- **When to Use**: Skills that process large user-supplied documents.
- **Example**: `Accept the contract in: - File upload - URL - Pasted text. For very long contracts (50+ pages), offer to focus on material sections first.`

---

## Integration Patterns

### Credit/Cost Warnings
- **Category**: Integration
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic partner-built/apollo `prospect`
- **Description**: Before executing expensive operations (API calls that consume credits, bulk enrichments), explicitly warn the user about costs and get confirmation.
- **When to Use**: Any skill that triggers paid API calls or resource-intensive operations
- **Example**: "Tell the user exactly how many credits will be consumed before proceeding"

### Next Actions Menu
- **Category**: Integration
- **Lifecycle**: `validated`
- **Confidence**: Medium
- **Frequency**: 2 plugins
- **First Seen In**: Anthropic partner-built/apollo `prospect`, sales `call-prep`
- **Description**: End workflows with a numbered list of possible next actions. Enables natural conversation flow and prevents dead ends.
- **When to Use**: Any skill where the output can naturally lead to multiple follow-up actions
- **Example**: "1. Save all to Apollo  2. Load into sequence  3. Deep-dive a company  4. Refine search  5. Export"

### Source Attribution
- **Category**: Integration
- **Lifecycle**: `proposed`
- **Confidence**: Low
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic enterprise-search `knowledge-synthesis`
- **Description**: Every claim in synthesized output is attributed to a source with type, location, date, and author. Sources listed inline and as a summary list.
- **When to Use**: Any skill that synthesizes information from multiple sources
- **Example**: Inline: "Sarah confirmed REST (~~email, Jan 15)" + Source list at bottom

---


### Priority-Ordered Source Scanning
- **Category**: Integration
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `vendor-check`
- **Description**: Defining an explicit authority hierarchy (priority order) for multi-source queries, preventing the agent from treating informal signal sources identically to canonical system-of-record sources.
- **When to Use**: Multi-system data enrichment workflows.
- **Example**: `Search for the vendor across all available systems, in priority order: CLM -> CRM -> Email -> Documents -> Chat.`

### Source Transparency Declaration
- **Category**: Integration / Trust
- **Lifecycle**: `proposed`
- **Confidence**: Medium
- **Frequency**: 1 plugin
- **First Seen In**: Anthropic legal `brief`
- **Description**: Every workflow output explicitly lists what was successfully searched versus what was unavailable or skipped. Guarantees the user knows the limits of the generated output.
- **When to Use**: Any agent synthesizing data from multiple sources.
- **Example**: `**Sources Checked**: [list] | **Sources Unavailable**: [list]`

## Changelog

| Date | Action | Pattern(s) | Notes |
|------|--------|-----------|-------|
| 2026-03-03 | Governance backfill | All 28 patterns | Added Lifecycle, Confidence, Frequency fields to all existing patterns |
| 2026-03-03 | Initial catalog | 18 core patterns | Architectural (3), Execution (4), Content (6), Knowledge (3), Integration (2) |
| 2026-03-03 | Expansion | 10 Interaction patterns | Added Interaction Design Patterns category |

---

*Last updated: Governance backfilled 2026-03-03*
*Total patterns: 28 (governance fields backfilled 2026-03-03)*
