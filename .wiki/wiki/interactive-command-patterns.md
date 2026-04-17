---
concept: interactive-command-patterns
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-command/references/interactive-commands.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.804755+00:00
cluster: questions
content_hash: 09ab1f18bfa3ff5f
---

# Interactive Command Patterns

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Interactive Command Patterns

Comprehensive guide to creating commands that gather user feedback and make decisions through the AskUserQuestion tool.

## Overview

Some commands need user input that doesn't work well with simple arguments. For example:
- Choosing between multiple complex options with trade-offs
- Selecting multiple items from a list
- Making decisions that require explanation
- Gathering preferences or configuration interactively

For these cases, use the **AskUserQuestion tool** within command execution rather than relying on command arguments.

## When to Use AskUserQuestion

### Use AskUserQuestion When:

1. **Multiple choice decisions** with explanations needed
2. **Complex options** that require context to choose
3. **Multi-select scenarios** (choosing multiple items)
4. **Preference gathering** for configuration
5. **Interactive workflows** that adapt based on answers

### Use Command Arguments When:

1. **Simple values** (file paths, numbers, names)
2. **Known inputs** user already has
3. **Scriptable workflows** that should be automatable
4. **Fast invocations** where prompting would slow down

## AskUserQuestion Basics

### Tool Parameters

```typescript
{
  questions: [
    {
      question: "Which authentication method should we use?",
      header: "Auth method",  // Short label (max 12 chars)
      multiSelect: false,     // true for multiple selection
      options: [
        {
          label: "OAuth 2.0",
          description: "Industry standard, supports multiple providers"
        },
        {
          label: "JWT",
          description: "Stateless, good for APIs"
        },
        {
          label: "Session",
          description: "Traditional, server-side state"
        }
      ]
    }
  ]
}
```

**Key points:**
- Users can always choose "Other" to provide custom input (automatic)
- `multiSelect: true` allows selecting multiple options
- Options should be 2-4 choices (not more)
- Can ask 1-4 questions per tool call

## Command Pattern for User Interaction

### Basic Interactive Command

```markdown
---
description: Interactive setup command
allowed-tools: AskUserQuestion, Write
---

# Interactive Plugin Setup

This command will guide you through configuring the plugin with a series of questions.

## Step 1: Gather Configuration

Use the AskUserQuestion tool to ask:

**Question 1 - Deployment target:**
- header: "Deploy to"
- question: "Which deployment platform will you use?"
- options:
  - AWS (Amazon Web Services with ECS/EKS)
  - GCP (Google Cloud with GKE)
  - Azure (Microsoft Azure with AKS)
  - Local (Docker on local machine)

**Question 2 - Environment strategy:**
- header: "Environments"
- question: "How many environments do you need?"
- options:
  - Single (Just production)
  - Standard (Dev, Staging, Production)
  - Complete (Dev, QA, Staging, Production)

**Question 3 - Features to enable:**
- header: "Features"
- question: "Which features do you want to enable?"
- multiSelect: true
- options:
  - Auto-scaling (Automatic resource scaling)
  - Monitoring (Health checks and metrics)
  - CI/CD (Automated deployment pipeline)
  - Backups (Automated database backups)

## Step 2: Process Answers

Based on the answers received from AskUserQuestion:

1. Parse the deployment target choice
2. Set up environment-specific configuration
3. Enable selected features
4. Generate configuration files

## Step 3: Generate Configuration

Create `.claude/plugin-name.local.md` with:

\`\`\`yaml
---
deployment_target: [answer from Q1]
environments: [answer from Q2]
features:
  auto_scaling: [true if selected in Q3]
  monitoring: [true if selected in Q3]
  ci_cd: [true if selected in Q3]
  backups: [true if selected in Q3]
---

# Plugin Configuration

Generated: [timestamp]
Target: [deployment_target]
Environments: [environments]
\`\`\`

## Step 4: Confirm and Next Steps

Confirm configuration created and guide user on next steps.
```

### Multi-Stage Interactive Workflow

```markdown
---
descri

*(content truncated)*

## See Also

- [[os-init-command]]
- [[os-loop-command]]
- [[os-memory-command]]
- [[context-folder-patterns]]
- [[optimizer-engine-patterns-reference-design]]
- [[optimizer-engine-patterns-reference-design]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-command/references/interactive-commands.md`
- **Indexed:** 2026-04-17T06:42:09.804755+00:00
