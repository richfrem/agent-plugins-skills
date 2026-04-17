---
concept: advanced-workflow-patterns
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/references/advanced-workflows.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.799782+00:00
cluster: state
content_hash: eb258095b5a411b6
---

# Advanced Workflow Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Advanced Workflow Patterns

Multi-step command sequences and composition patterns for complex workflows.

## Overview

Advanced workflows combine multiple commands, coordinate state across invocations, and create sophisticated automation sequences. These patterns enable building complex functionality from simple command building blocks.

## Multi-Step Command Patterns

### Sequential Workflow Command

Commands that guide users through multi-step processes:

```markdown
---
description: Complete PR review workflow
argument-hint: [pr-number]
allowed-tools: Bash(gh:*), Read, Grep
---

# PR Review Workflow for #$1

## Step 1: Fetch PR Details
!`gh pr view $1 --json title,body,author,files`

## Step 2: Review Files
Files changed: !`gh pr diff $1 --name-only`

For each file:
- Check code quality
- Verify tests exist
- Review documentation

## Step 3: Run Checks
Test status: !`gh pr checks $1`

Verify:
- All tests passing
- No merge conflicts
- CI/CD successful

## Step 4: Provide Feedback

Summarize:
- Issues found (critical/minor)
- Suggestions for improvement
- Approval recommendation

Would you like to:
1. Approve PR
2. Request changes
3. Leave comments only

Reply with your choice and I'll help complete the action.
```

**Key features:**
- Numbered steps for clarity
- Bash execution for context
- Decision points for user input
- Next action suggestions

### State-Carrying Workflow

Commands that maintain state between invocations:

```markdown
---
description: Initialize deployment workflow
allowed-tools: Write, Bash(git:*)
---

# Initialize Deployment

Creating deployment tracking file...

Current branch: !`git branch --show-current`
Latest commit: !`git log -1 --format=%H`

Deployment state saved to `.claude/deployment-state.local.md`:

\`\`\`markdown
---
initialized: true
branch: $(git branch --show-current)
commit: $(git log -1 --format=%H)
timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
status: initialized
---

# Deployment Tracking

Branch: $(git branch --show-current)
Started: $(date)

Next steps:
1. Run tests: /deploy-test
2. Build: /deploy-build
3. Deploy: /deploy-execute
\`\`\`

State saved. Run `/deploy-test` to continue.
```

**Next command** (`/deploy-test`):
```markdown
---
description: Run deployment tests
allowed-tools: Read, Bash(npm:*)
---

Reading deployment state from `.claude/deployment-state.local.md`...

Running tests: !`npm test`

Updating state to 'tested'...

Tests complete. Run `/deploy-build` to continue.
```

**Pattern benefits:**
- Persistent state across commands
- Clear workflow progression
- Safety checkpoints
- Resume capability

### Conditional Workflow Branching

Commands that adapt based on conditions:

```markdown
---
description: Smart deployment workflow
argument-hint: [environment]
allowed-tools: Bash(git:*), Bash(npm:*), Read
---

# Deploy to $1

## Pre-flight Checks

Branch: !`git branch --show-current`
Status: !`git status --short`

**Checking conditions:**

1. Branch status:
   - If main/master: Require approval
   - If feature branch: Warning about target
   - If hotfix: Fast-track process

2. Tests:
   !`npm test`
   - If tests fail: STOP - fix tests first
   - If tests pass: Continue

3. Environment:
   - If $1 = 'production': Extra validation
   - If $1 = 'staging': Standard process
   - If $1 = 'dev': Minimal checks

**Workflow decision:**
Based on above, proceeding with: [determined workflow]

[Conditional steps based on environment and status]

Ready to deploy? (yes/no)
```

## Command Composition Patterns

### Command Chaining

Commands designed to work together:

```markdown
---
description: Prepare for code review
---

# Prepare Code Review

Running preparation sequence:

1. Format code: /format-code
2. Run linter: /lint-code
3. Run tests: /test-all
4. Generate coverage: /coverage-report
5. Create review summary: /review-summary

This is a meta-command. After completing each step above,
I'll compile results and prepare comprehensive review materials.

Starting sequence...
```

*

*(content truncated)*

## See Also

- [[context-folder-patterns]]
- [[metrics-workflow-health-continuous-improvement]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]
- [[context-folder-patterns]]
- [[context-folder-patterns]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/references/advanced-workflows.md`
- **Indexed:** 2026-04-17T06:42:09.799782+00:00
