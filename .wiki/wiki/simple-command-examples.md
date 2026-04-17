---
concept: simple-command-examples
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/references/simple-commands.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.826733+00:00
cluster: file
content_hash: f2533ed834305166
---

# Simple Command Examples

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Simple Command Examples

Basic slash command patterns for common use cases.

**Important:** All examples below are written as instructions FOR Claude (agent consumption), not messages TO users. Commands tell Claude what to do, not tell users what will happen.

## Example 1: Code Review Command

**File:** `.claude/commands/review.md`

```markdown
---
description: Review code for quality and issues
allowed-tools: Read, Bash(git:*)
---

Review the code in this repository for:

1. **Code Quality:**
   - Readability and maintainability
   - Consistent style and formatting
   - Appropriate abstraction levels

2. **Potential Issues:**
   - Logic errors or bugs
   - Edge cases not handled
   - Performance concerns

3. **Best Practices:**
   - Design patterns used correctly
   - Error handling present
   - Documentation adequate

Provide specific feedback with file and line references.
```

**Usage:**
```
> /review
```

---

## Example 2: Security Review Command

**File:** `.claude/commands/security-review.md`

```markdown
---
description: Review code for security vulnerabilities
allowed-tools: Read, Grep
model: sonnet
---

Perform comprehensive security review checking for:

**Common Vulnerabilities:**
- SQL injection risks
- Cross-site scripting (XSS)
- Authentication/authorization issues
- Insecure data handling
- Hardcoded secrets or credentials

**Security Best Practices:**
- Input validation present
- Output encoding correct
- Secure defaults used
- Error messages safe
- Logging appropriate (no sensitive data)

For each issue found:
- File and line number
- Severity (Critical/High/Medium/Low)
- Description of vulnerability
- Recommended fix

Prioritize issues by severity.
```

**Usage:**
```
> /security-review
```

---

## Example 3: Test Command with File Argument

**File:** `.claude/commands/test-file.md`

```markdown
---
description: Run tests for specific file
argument-hint: [test-file]
allowed-tools: Bash(npm:*), Bash(jest:*)
---

Run tests for $1:

Test execution: !`npm test $1`

Analyze results:
- Tests passed/failed
- Code coverage
- Performance issues
- Flaky tests

If failures found, suggest fixes based on error messages.
```

**Usage:**
```
> /test-file src/utils/helpers.test.ts
```

---

## Example 4: Documentation Generator

**File:** `.claude/commands/document.md`

```markdown
---
description: Generate documentation for file
argument-hint: [source-file]
---

Generate comprehensive documentation for @$1

Include:

**Overview:**
- Purpose and responsibility
- Main functionality
- Dependencies

**API Documentation:**
- Function/method signatures
- Parameter descriptions with types
- Return values with types
- Exceptions/errors thrown

**Usage Examples:**
- Basic usage
- Common patterns
- Edge cases

**Implementation Notes:**
- Algorithm complexity
- Performance considerations
- Known limitations

Format as Markdown suitable for project documentation.
```

**Usage:**
```
> /document src/api/users.ts
```

---

## Example 5: Git Status Summary

**File:** `.claude/commands/git-status.md`

```markdown
---
description: Summarize Git repository status
allowed-tools: Bash(git:*)
---

Repository Status Summary:

**Current Branch:** !`git branch --show-current`

**Status:** !`git status --short`

**Recent Commits:** !`git log --oneline -5`

**Remote Status:** !`git fetch && git status -sb`

Provide:
- Summary of changes
- Suggested next actions
- Any warnings or issues
```

**Usage:**
```
> /git-status
```

---

## Example 6: Deployment Command

**File:** `.claude/commands/deploy.md`

```markdown
---
description: Deploy to specified environment
argument-hint: [environment] [version]
allowed-tools: Bash(kubectl:*), Read
---

Deploy to $1 environment using version $2

**Pre-deployment Checks:**
1. Verify $1 configuration exists
2. Check version $2 is valid
3. Verify cluster accessibility: !`kubectl cluster-info`

**Deployment Steps:**
1. Update deployment manifest with version $2
2. Apply configuration to $1
3. Monitor rollout s

*(content truncated)*

## See Also

- [[plugin-command-examples]]
- [[plugin-command-examples]]
- [[plugin-command-examples]]
- [[os-init-command]]
- [[os-loop-command]]
- [[os-memory-command]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/references/simple-commands.md`
- **Indexed:** 2026-04-17T06:42:09.826733+00:00
