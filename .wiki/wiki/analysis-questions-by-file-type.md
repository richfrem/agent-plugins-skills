---
concept: analysis-questions-by-file-type
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/analyze-plugin/references/analysis-questions-by-type.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.713905+00:00
cluster: output
content_hash: 4e2a527c7803a65b
---

# Analysis Questions by File Type

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

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
- [ ] Does it output structured data (JSON) that can be parsed by skill

*(content truncated)*

## See Also

- [[canonical-agentic-os-file-structure]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[karpathys-autoresearch-the-3-file-architecture-for-automated-evaluation]]
- [[canonical-file-structure]]
- [[canonical-file-structure]]
- [[karpathy-autoresearch-3-file-eval]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/analyze-plugin/references/analysis-questions-by-type.md`
- **Indexed:** 2026-04-17T06:42:09.713905+00:00
