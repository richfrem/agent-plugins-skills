---
name: create-github-action
plugin: agent-scaffolders
description: Scaffold a deterministic GitHub Actions CI/CD workflow
argument-hint: "[workflow-type: test|build|deploy|lint|release|security]"
allowed-tools: Bash, Read, Write
---

Follow the `create-github-action` skill workflow to scaffold a traditional deterministic
GitHub Actions CI/CD workflow (no AI at runtime).

## Inputs

- `$ARGUMENTS` — optional workflow type or purpose (e.g. `test`, `build`, `deploy`,
  `lint`, `release`, `security`). Omit to start with discovery.

## Steps

1. If `$ARGUMENTS` specifies a workflow type, use it to seed Phase 1 discovery
2. Follow the create-github-action phased workflow: confirm trigger events, runner OS,
   required secrets/environment variables, job steps, and caching strategy
3. Generate the `.github/workflows/<name>.yml` file
4. Report the workflow path and setup instructions (secrets to configure, badges, etc.)

## Output

`.github/workflows/<name>.yml` with complete job definitions, trigger events, permissions,
and inline comments explaining each step.

## Edge Cases

- If `$ARGUMENTS` is empty: begin with workflow type discovery
- If the use case involves AI agents at runtime: redirect to `create-agentic-workflow`
- If secrets or environment variables are required: list them explicitly without values
