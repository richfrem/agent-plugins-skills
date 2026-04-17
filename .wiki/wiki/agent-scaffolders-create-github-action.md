---
concept: agent-scaffolders-create-github-action
source: plugin-code
source_file: spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-github-action.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.317985+00:00
cluster: workflow
content_hash: 53c6cd7c232ae85e
---

# Agent Scaffolders Create Github Action

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: create-github-action
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


## See Also

- [[procedural-fallback-tree-create-github-action]]
- [[procedural-fallback-tree-create-github-action]]
- [[procedural-fallback-tree-create-github-action]]
- [[agent-scaffolders-create-agentic-workflow]]
- [[agent-scaffolders-create-azure-agent]]
- [[agent-scaffolders-create-docker-skill]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/workflows/agent-scaffolders_create-github-action.md`
- **Indexed:** 2026-04-17T06:42:10.317985+00:00
