---
concept: acceptance-criteria-dependency-agent
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/dependency-management/references/acceptance-criteria.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:10.028113+00:00
cluster: dockerfile
content_hash: 61db3c3008693b14
---

# Acceptance Criteria: dependency-agent

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Acceptance Criteria: dependency-agent

**Purpose**: Ensure the agent strictly adheres to the progressive disclosure architecture and properly parses dependencies without polluting production dockerfiles.

## 1. Context Isolation
- **[PASSED]**: When directed to manage dependencies, the agent searches for the required `.in` and `.txt` files rather than blindly running `pip install` on the command line.
- **[FAILED]**: The agent uses `pip install x` when asked to add a dependency without updating the `.txt` and `.in` files.

## 2. Dockerfile Protections
- **[PASSED]**: When updating a Dockerfile for a new Python app, the agent refuses to use `RUN pip install x` and instead creates/modifies a `../../../requirements.txt` file structure.
- **[FAILED]**: The agent adds `RUN pip install boto3` to the Dockerfile.


## See Also

- [[acceptance-criteria-agent-swarm]]
- [[agent-orchestrator-acceptance-criteria]]
- [[acceptance-criteria-create-sub-agent]]
- [[acceptance-criteria-claude-cli-agent]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[acceptance-criteria-gemini-cli-agent]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/dependency-management/references/acceptance-criteria.md`
- **Indexed:** 2026-04-17T06:42:10.028113+00:00
