# Workflows vs. Commands vs. Skills

This document traces the historical evolution of custom slash commands into the current open standard for Agent Skills, and specifically calls out how different agent ecosystems refer to specific task-runner routines (like *Workflows* in Antigravity or Roo Code).

## The Evolution of 
`/commands`

In early versions of Agentic environments (such as older versions of Claude Code), users extended capability using a simple directory approach (e.g. `.claude/commands/`).
- Putting a file at `.claude/commands/review.md` would automatically create the `/review` slash command for the user to invoke.
  
**The Merge into Agent Skills:**
Custom slash commands have since been merged into the [Agent Skills standard](https://agentskills.io). 
- Legacy `.claude/commands/` files continue to execute seamlessly.
- **Location Nuance:** Skills can actually be deployed in both the `skills/` and `commands/` directories. 
  - If a skill is placed in `commands/`, it explicitly allows you to invoke it manually via a `/` slash-command in the agent UI as a shortcut.
  - If placed in `skills/`, it relies more on autonomous discovery via the LLM reading the `description` frontmatter.

### Why Skills Replace Legacy Commands
While legacy commands are just flat Markdown files, turning a command into a **Skill** adds powerful features:
- **A Dedicated Directory**: You can store supporting files (`scripts/`, `references/`) instead of cramming everything into one markdown file.
- **Trigger Control via Frontmatter**: Frontmatter allows you to toggle `user-invocable: true` or `disable-model-invocation: true`. 
- **Autonomous Discovery**: Skills contain a `description` field that allows Claude to discover and "run" the command automatically when a relevant context arises, whereas legacy `/commands` require the user to manually trigger them.

## Antigravity Rules and Workflows
For platforms like **Antigravity** (Google Deepmind's agent framework), these repeatable systems are officially documented as **Rules** and **Workflows**.

### Rules
Rules provide models with persistent, reusable constraints and context at the prompt level. They are manually defined constraints to help the agent follow behaviors specific to your stack and style.
- **Global Rules:** Saved to `~/.gemini/GEMINI.md` (applied across all workspaces).
- **Workspace Rules:** Saved to `.agent/rules/` within your workspace/git root.
- **Size Limit:** Each Rule file is strictly limited to **12,000 characters maximum**.

**Activation Triggers:**
Rules can be defined to activate in four ways:
1. **Manual:** Activated manually via `@` mention.
2. **Always On:** Unconditionally applied to prompt context.
3. **Model Decision:** Provide a natural language description, and the model autonomously decides if it applies.
4. **Glob:** A glob pattern (e.g., `.js`, `src/**/*.ts`) causes the rule to automatically apply to matched files.

**File Includes:**
Rules support `@filename` includes. Relative paths are resolved relative to the Rules file. Absolute paths are resolved as true absolutes; otherwise, they resolve relative to the repository root.

### Workflows
While *Rules* provide context, **Workflows** provide a structured sequence of steps or prompts at the *trajectory level*. They guide the model through interconnected actions (like deploying a service or closing PRs).
- **Format:** Workflows are Markdown files containing a title, a description, and a series of steps (often leveraging `// turbo` tags to auto-run CLI actions).
- **Storage:** Saved locally to `.agents/workflows/` or globally as specified.
- **Size Limit:** Each Workflow file is strictly limited to **12,000 characters maximum**.
- **Execution:** Invoked directly as slash commands (e.g., `/workflow-name`). Workflows can also recursively call *other* workflows by including instructions like "Call /workflow-2".

## Convergence
Whether checking `.agent/workflows/[name].md` for Antigravity, or parsing `.claude/skills/[name]/SKILL.md` for Claude Code, the end goal is identical: **providing agents with reusable, deterministically structured procedural knowledge so they don't have to guess how your environment operates.**
