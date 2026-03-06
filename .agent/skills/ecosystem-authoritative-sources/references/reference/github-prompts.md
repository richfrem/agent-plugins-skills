# GitHub Models Prompts Standard

This document officially specifies how the Agent Ecosystem handles custom commands and prompt files targeting GitHub Models and the GitHub ecosystem.

## Background Research
GitHub natively supports storing prompts directly in GitHub repositories to leverage automated text summarization and AI-driven functionalities via GitHub Models. 
While early agent environments relied on flat Markdown directory structures (e.g., `.claude/commands/`) or VS Code preview formats (`.prompt.md`), the **official GitHub format requires `.prompt.yml` or `.prompt.yaml` files**. 

Because our Agent Plugin Ecosystem adheres to the "write-once-run-anywhere" (WORA) philosophy, developers **do not** write raw `.prompt.yml` files manually. They write generalized `commands/*.md` files, which the `agent-bridge` translates into the precise GitHub Models YAML format.

## The Output Format
When the bridge runs, it translates our generalized Markdown plugin commands into this exact output schema:

```yaml
name: my-prompt-name
description: "A brief description of what this prompt does from the frontmatter"
model: openai/gpt-4o # Injected by bridge or specified in frontmatter
messages:
  - role: system
    content: |
      You are a helpful AI assistant.
      [The rule context and tools from the ecosystem]
  - role: user
    content: |
      [The markdown body of the original command]
```

### Supported Dynamic Context Variables
GitHub Models supports simple handle-bars style placeholders within the `content` block:
- `{{variable}}`

## Opt-In Export Rule: `github-model-export`
Most agent slash commands and workflows are highly contextual to the local IDE (e.g., scaffolding a file, reading local terminals, running local linters). These local tasks are **terrible** candidates for GitHub Models, which executes in a stateless backend or CI/CD environment.

Therefore, the `agent-bridge` operates on a strict **Opt-In** policy for exporting `.prompt.yml` files. By default, **no** commands are bridged to `.github/prompts/`.

To expose a specific command/prompt (such as an automated code reviewer, summarize action, or CI/CD script) to the GitHub Models ecosystem, the developer must explicitly add `github-model-export: true` to the YAML frontmatter.

### Example Opt-In Usage
```markdown
---
name: Summarize PR
description: Specialized prompt meant to run in GitHub Actions during PRs.
github-model-export: true
---
# PR Summarizer
...
```

When the `agent-bridge` compiles the plugin logic into the `.github/` folder, it will ignore all `commands/*.md` files *unless* `github-model-export` is explicitly set to `true`.
