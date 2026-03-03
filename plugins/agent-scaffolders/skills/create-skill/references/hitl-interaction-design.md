# Human-in-the-Loop (HITL) Interaction Design Guide

A reference for deciding when and how to incorporate human interaction into skills, and how to design outputs for different audiences. Used by `create-skill` during the design phase.

---

## HITL Decision Matrix

Not every skill needs user interaction. Use this table to determine the right interaction level:

| Skill Characteristic | Recommended HITL Level | Example |
|---------------------|----------------------|---------|
| Deterministic, no ambiguity | **None** — fully autonomous | Audit a plugin structure |
| Needs org-specific context | **Discovery interview** before execution | Generate a data analysis skill |
| Makes irreversible changes | **Confirmation gate** before action | Delete files, consume API credits |
| Multiple valid approaches | **Option menu** at decision points | Choose migration strategy |
| Long-running, multi-phase | **Progress indicators** between phases | Analyze 17 plugins |
| Output has multiple audiences | **Format negotiation** before delivery | Report for exec vs engineer |
| Uncertain/ambiguous input | **Clarification questions** inline | Interpret vague user request |

## Question Types Reference

### Type 1: Yes/No Confirmation
**When**: Binary decisions, confirmation gates, proceed/abort.
```
Proceed with the migration? (yes/no)
```
**Design Rule**: Use only when there are exactly 2 options with no nuance.

### Type 2: Numbered Option Menu
**When**: 3-7 discrete, well-defined options.
```
Select an output format:
1. Inline markdown summary
2. Full structured report
3. Interactive HTML dashboard
4. JSON data export
5. CSV spreadsheet
```
**Design Rules**:
- Keep to 3-7 items (fewer = use yes/no; more = group into categories first)
- Always include a default recommendation: "(recommended: 2)"
- Include an escape hatch: "6. Other (describe)"

### Type 3: Open-Ended Question
**When**: Gathering domain knowledge, context, or requirements that can't be predicted.
```
What are the core business entities in your database?
```
**Design Rules**:
- Provide examples to anchor the response: "e.g., Users, Orders, Products"
- Ask one question at a time, not a wall of questions
- Use progressive questioning: start broad, narrow based on answers

### Type 4: Table-Based Comparison
**When**: Options have multiple dimensions the user needs to weigh.
```
| # | Strategy | Risk | Speed | Cost |
|---|----------|------|-------|------|
| 1 | Full rewrite | Low | Slow | High |
| 2 | Strangler fig | Medium | Medium | Medium |
| 3 | Lift and shift | High | Fast | Low |

Which approach fits your situation? (1/2/3)
```
**Design Rule**: Use when each option has 3+ attributes worth comparing.

### Type 5: Smart Default with Override
**When**: There's a clear best practice, but power users may need to deviate.
```
I recommend PostgreSQL dialect based on your stack. Override? (yes/no)
```
**Design Rule**: Always explain WHY the default is recommended.

### Type 6: Recap Confirmation
**When**: After a discovery phase, before executing.
```
## Here's what I gathered:
- Database: PostgreSQL 14
- Target: React frontend
- Migration scope: 47 forms

Does this look right? (yes / adjust)
```
**Design Rule**: Use before any generation or execution phase that consumes significant tokens.

---

## Output Design Guide

### Audience-Aware Output Selection

| Audience | Preferred Format | Characteristics |
|----------|-----------------|----------------|
| **Executive/PM** | Inline summary or HTML dashboard | Visual, concise, metric-focused |
| **Engineer** | Markdown report with code blocks | Detailed, actionable, technical |
| **Compliance/Legal** | Structured report with citations | Formal, traceable, attributed |
| **Data Pipeline** | JSON or CSV | Machine-readable, schema-defined |
| **Cross-Team** | Multi-format (negotiate) | Offer options at runtime |

### Output Template Categories

#### Human-Readable Templates
- **Executive Summary**: 3-5 bullet points, key metrics, next steps
- **Structured Report**: Sections with headers, tables, analysis, recommendations
- **HTML Dashboard**: Self-contained HTML with inline CSS, charts, interactive elements
- **Redline/Diff**: Before → After with rationale (legal, contract, code review)
- **Playbook**: Step-by-step guide with decision trees

#### Machine-Readable Templates
- **JSON**: Structured schema with typed fields, arrays, nested objects
- **CSV**: Tabular data with headers, one record per row
- **YAML**: Configuration output, pipeline definitions
- **Markdown Checklist**: Task lists with `- [ ]` checkboxes

#### Hybrid Templates
- **Annotated JSON**: JSON with comments explaining each section
- **Report + Data**: Markdown narrative with embedded code blocks containing structured data
- **Interactive HTML + Export**: Dashboard with CSV/JSON download buttons

### When to Negotiate Format
Add format negotiation to a skill when:
1. The same analysis serves different audiences (exec vs engineer)
2. The output may feed into another tool (needs JSON) OR be read by humans (needs markdown)
3. The skill handles both exploratory (human reads) and production (pipeline consumes) use cases

### Format Negotiation Pattern
```
How would you like these results?
1. Inline summary (quick overview)
2. Full markdown report (detailed analysis)
3. HTML artifact (visual dashboard)
4. JSON export (for pipeline consumption)
5. CSV export (for spreadsheet analysis)
```

---

## Incorporating HITL into SKILL.md Structure

### Autonomous Skill (No HITL)
```markdown
## Instructions
1. [Step 1]
2. [Step 2]
3. [Output]
```

### Guided Skill (Discovery + Execution)
```markdown
## Discovery Phase
[Progressive questions here]

## Recap
[Confirm understanding]

## Execution Phase
[Steps here]

## Output
[Format template]

## Next Actions
[Numbered options]
```

### Hybrid Skill (Minimal HITL)
```markdown
## Quick Context
[1-2 essential questions with smart defaults]

## Execution
[Steps with confirmation gates at critical points]

## Output
[Default format with override option]
```
