# Analysis Questions by File Type

Structured self-prompt templates for the analyzer to use when examining each type of file. These evolve as we discover new questions through analysis runs.

---

## SKILL.md Analysis Questions

### Frontmatter
- [ ] Is `name` kebab-case, ≤64 characters, matches directory name?
- [ ] Is `description` in third person and ≤1024 characters?
- [ ] Does the description clearly state WHEN to trigger this skill?
- [ ] Are there specific trigger phrases embedded in the description?

### Structure
- [ ] Total line count — is it under 500?
- [ ] Does it have numbered phases or steps?
- [ ] Does it link to `references/` for deep content?
- [ ] Is there a clear separation between discovery and execution?

### Interaction Design
- [ ] What HITL level does this use? (None / Guided / Hybrid)
- [ ] If guided: does it use progressive questioning (not question walls)?
- [ ] What question types are present? (yes/no, numbered options, open-ended, table comparison, smart defaults)
- [ ] Are there confirmation gates before expensive/irreversible operations?
- [ ] Is there a recap-before-execute pattern?
- [ ] Does it end with next-action options?

### Output Design
- [ ] Does it define an output format or template?
- [ ] Does it negotiate format with the user?
- [ ] Is the output audience-appropriate? (human-readable vs machine-readable)
- [ ] Does it use any self-contained artifacts (HTML, structured reports)?

### Execution Patterns
- [ ] Is there a dual-mode structure (Bootstrap vs Iteration)?
- [ ] Are there fallback chains for when tools aren't available?
- [ ] Are there tiered execution strategies (basic/intermediate/advanced)?
- [ ] Does it use decision tables or trees for branching logic?

### Knowledge Architecture
- [ ] What ratio of content is in SKILL.md vs references?
- [ ] Are domain-specific details properly extracted to references?
- [ ] Does it use dialect/variant tables for multi-platform support?

---

## Command Analysis Questions

### Purpose
- [ ] Is this command written as instructions FOR the agent (imperative voice)?
- [ ] Does it clearly state what it produces?
- [ ] Is the argument-hint useful and descriptive?

### Workflow
- [ ] Does it chain to specific skills?
- [ ] Does it specify a standalone vs supercharged path?
- [ ] Does it handle missing arguments gracefully?

### Interaction
- [ ] Does it present options if the scope is ambiguous?
- [ ] Does it confirm destructive actions?
- [ ] Does it end with follow-up suggestions?

---

## Sub-Agent Analysis Questions

### Architecture
- [ ] What is its specialized role? (Exploration, Planning, Execution, QA)
- [ ] Does it have appropriate tool permissions?
- [ ] Is there a clear boundary between parent and sub-agent responsibilities?

### Communication
- [ ] How does it report results back to the parent?
- [ ] Does it have a defined output format?
- [ ] Does it handle errors and communicate them upstream?

---

## Reference File Analysis Questions

### Content Quality
- [ ] Does it contain deep domain knowledge not duplicated in SKILL.md?
- [ ] Is it organized by topic, not by arbitrary sections?
- [ ] Does it have a table of contents (if >100 lines)?
- [ ] Are there concrete examples alongside abstract principles?

### Reusability
- [ ] Could this reference be useful to other skills?
- [ ] Does it avoid referencing other reference files (no nested chains)?
- [ ] Is terminology consistent with the parent SKILL.md?

---

## Script Analysis Questions

### Compliance
- [ ] Is it Python-only (.py)? No .sh or .ps1?
- [ ] Does it have a docstring header with Purpose, Usage, Arguments, Output?
- [ ] Does `--help` work and describe all arguments?

### Quality
- [ ] Does it handle errors with explicit messages (not silent failures)?
- [ ] Is it cross-platform compatible (no Windows-specific or macOS-specific paths)?
- [ ] Are there magic numbers/constants without documentation?
- [ ] Does it output structured data (JSON) that can be parsed by skills?

### Design
- [ ] Is the script a "black box" — can the agent just run it without reading the source?
- [ ] Does it follow the single-responsibility principle?
- [ ] Could it be composed with other scripts?

---

## README Analysis Questions

### Completeness
- [ ] Does it have a file tree using `├──` / `└──` characters?
- [ ] Does it explain the plugin/skill purpose in 1-2 paragraphs?
- [ ] Does it list available skills, commands, and scripts in tables?
- [ ] Does it include usage examples?

### Architecture Documentation
- [ ] Does it document standalone vs supercharged capabilities?
- [ ] Is there an architecture diagram (mermaid, ASCII, or .mmd)?
- [ ] Are external dependencies documented?

---

## CONNECTORS.md Analysis Questions

### Abstraction Quality
- [ ] Does it use `~~category` placeholders instead of hardcoded tool names?
- [ ] Does it list multiple concrete tool options per category?
- [ ] Does it map categories to which skills use them?
- [ ] Is it formatted as a scannable table?

---

## Config File Analysis Questions (.mcp.json, hooks.json, etc.)

### Schema
- [ ] Does the config follow the expected JSON schema?
- [ ] Are there hardcoded paths that should use environment variables?
- [ ] Are credentials absent (no API keys in config files)?
- [ ] Is the config documented with comments or a companion reference file?

---

*This reference evolves. After each analysis run, if a question would have been valuable but wasn't in this list, add it to the appropriate section.*

---

## Holistic Agent Design Considerations

These higher-level questions apply across all file types in a plugin/skill. Ask these after completing the per-file analysis to assess the overall design maturity.

### HITL Strategy
- [ ] What is the overall HITL approach? (Fully autonomous / Guided discovery / Hybrid)
- [ ] Is the HITL level appropriate for the task complexity?
- [ ] Are question types varied and well-chosen? (Not all yes/no, not all open-ended)
- [ ] Are interactions efficient? (No redundant questions, no question walls)
- [ ] Does the flow feel conversational or robotic?

### Input Design
- [ ] How does the skill gather the context it needs? (User interview / File system scan / MCP tools / Arguments)
- [ ] Are inputs validated before proceeding?
- [ ] Are smart defaults provided to reduce user burden?
- [ ] Is there a recap step to confirm understanding before execution?
- [ ] Could any user inputs be inferred automatically instead of asked?

### Output Design
- [ ] Who/what consumes the output? (Human reader / Another skill / Pipeline / API)
- [ ] Is the output format matched to its consumer?
- [ ] Are there output templates ensuring consistency across invocations?
- [ ] Does the skill negotiate format with the user when appropriate?
- [ ] Is the output self-contained (no broken links, missing context)?

### Script Usage Philosophy
- [ ] Is deterministic logic delegated to scripts (not LLM-generated bash)?
- [ ] Are scripts designed as black boxes (run with --help, don't read source)?
- [ ] Do scripts output structured data (JSON) parseable by the LLM?
- [ ] Is there a single script trying to do too much, vs. composable scripts?

### Repeatability & Consistency
- [ ] Would two different agents produce the same output from the same input?
- [ ] Are workflows deterministic where they should be, creative where appropriate?
- [ ] Are there quality checklists ensuring output completeness?
- [ ] Is there a verification/audit step at the end?

### Composability
- [ ] Can this skill be chained with other skills?
- [ ] Does it produce outputs that other skills can consume?
- [ ] Is it properly scoped (single responsibility) or is it trying to do too much?
- [ ] Could parts of this skill be extracted into reusable sub-skills?

### Evolution & Maintainability
- [ ] Does the skill have acceptance criteria for testing?
- [ ] Is it easy to add new capabilities without rewriting?
- [ ] Are there clear extension points (new reference files, script flags)?
- [ ] Does it self-document its limitations and assumptions?
