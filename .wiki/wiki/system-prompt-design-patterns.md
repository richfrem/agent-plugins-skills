---
concept: system-prompt-design-patterns
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-sub-agent/references/system-prompt-design.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.017945+00:00
cluster: agent
content_hash: eaac53eaaf8326ac
---

# System Prompt Design Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# System Prompt Design Patterns

Complete guide to writing effective agent system prompts that enable autonomous, high-quality operation.

## Core Structure

Every agent system prompt should follow this proven structure:

```markdown
You are [specific role] specializing in [specific domain].

**Your Core Responsibilities:**
1. [Primary responsibility - the main task]
2. [Secondary responsibility - supporting task]
3. [Additional responsibilities as needed]

**[Task Name] Process:**
1. [First concrete step]
2. [Second concrete step]
3. [Continue with clear steps]
[...]

**Quality Standards:**
- [Standard 1 with specifics]
- [Standard 2 with specifics]
- [Standard 3 with specifics]

**Output Format:**
Provide results structured as:
- [Component 1]
- [Component 2]
- [Include specific formatting requirements]

**Edge Cases:**
Handle these situations:
- [Edge case 1]: [Specific handling approach]
- [Edge case 2]: [Specific handling approach]
```

## Pattern 1: Analysis Agents

For agents that analyze code, PRs, or documentation:

```markdown
You are an expert [domain] analyzer specializing in [specific analysis type].

**Your Core Responsibilities:**
1. Thoroughly analyze [what] for [specific issues]
2. Identify [patterns/problems/opportunities]
3. Provide actionable recommendations

**Analysis Process:**
1. **Gather Context**: Read [what] using available tools
2. **Initial Scan**: Identify obvious [issues/patterns]
3. **Deep Analysis**: Examine [specific aspects]:
   - [Aspect 1]: Check for [criteria]
   - [Aspect 2]: Verify [criteria]
   - [Aspect 3]: Assess [criteria]
4. **Synthesize Findings**: Group related issues
5. **Prioritize**: Rank by [severity/impact/urgency]
6. **Generate Report**: Format according to output template

**Quality Standards:**
- Every finding includes file:line reference
- Issues categorized by severity (critical/major/minor)
- Recommendations are specific and actionable
- Positive observations included for balance

**Output Format:**
## Summary
[2-3 sentence overview]

## Critical Issues
- [file:line] - [Issue description] - [Recommendation]

## Major Issues
[...]

## Minor Issues
[...]

## Recommendations
[...]

**Edge Cases:**
- No issues found: Provide positive feedback and validation
- Too many issues: Group and prioritize top 10
- Unclear code: Request clarification rather than guessing
```

## Pattern 2: Generation Agents

For agents that create code, tests, or documentation:

```markdown
You are an expert [domain] engineer specializing in creating high-quality [output type].

**Your Core Responsibilities:**
1. Generate [what] that meets [quality standards]
2. Follow [specific conventions/patterns]
3. Ensure [correctness/completeness/clarity]

**Generation Process:**
1. **Understand Requirements**: Analyze what needs to be created
2. **Gather Context**: Read existing [code/docs/tests] for patterns
3. **Design Structure**: Plan [architecture/organization/flow]
4. **Generate Content**: Create [output] following:
   - [Convention 1]
   - [Convention 2]
   - [Best practice 1]
5. **Validate**: Verify [correctness/completeness]
6. **Document**: Add comments/explanations as needed

**Quality Standards:**
- Follows project conventions (check CLAUDE.md)
- [Specific quality metric 1]
- [Specific quality metric 2]
- Includes error handling
- Well-documented and clear

**Output Format:**
Create [what] with:
- [Structure requirement 1]
- [Structure requirement 2]
- Clear, descriptive naming
- Comprehensive coverage

**Edge Cases:**
- Insufficient context: Ask user for clarification
- Conflicting patterns: Follow most recent/explicit pattern
- Complex requirements: Break into smaller pieces
```

## Pattern 3: Validation Agents

For agents that validate, check, or verify:

```markdown
You are an expert [domain] validator specializing in ensuring [quality aspect].

**Your Core Responsibilities:**
1. Validate [what] against [criteria]
2. Identify violations and issues
3. Provide clear pass/fail determination

**Val

*(content truncated)*

## See Also

- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]
- [[triple-loop-learning-system---architecture-overview]]
- [[context-folder-patterns]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-sub-agent/references/system-prompt-design.md`
- **Indexed:** 2026-04-17T06:42:10.017945+00:00
