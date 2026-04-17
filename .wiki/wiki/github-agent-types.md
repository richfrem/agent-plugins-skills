---
concept: github-agent-types
source: plugin-code
source_file: spec-kitty-plugin/.agents/skills/create-agentic-workflow/references/agent-types.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.756690+00:00
cluster: plugin-code
content_hash: 8a7bd7d60d2aa024
---

# GitHub Agent Types

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# GitHub Agent Types

## Understanding the Two GitHub Agent Types

| | Type 1: IDE / UI Agent | Type 2: CI/CD — Smart Failure | Type 3: CI/CD — Official Format |
|---|---|---|---|
| **Triggered by** | Human via Copilot Chat | GitHub Actions event | GitHub Actions event |
| **Files generated** | `.agent.md` + `.prompt.md` | `.agent.md` + `.yml` runner | `.md` (intent) + `.lock.yml` (compiled) |
| **Failure signal** | N/A | Kill Switch phrase + grep | Native `safe-outputs` guardrails |
| **Coding engines** | Any Copilot model | Copilot CLI | Copilot CLI, Claude Code, Codex |
| **Compile step?** | No | No | Yes — `gh aw compile` |
| **Status** | GA | Works today | Technical preview (Feb 2026) |

## Implementation Notes

- **IDE agents**: The `.agent.md` body is a starting skeleton. For rich workflows (like multi-agent orchestrators), the full instruction set from the source SKILL.md should be manually ported into the `.agent.md` body, and `handoffs:` frontmatter added for chaining to other agents.
- **CI/CD Smart Failure agents**: The `.github/workflows/*.yml` requires a `COPILOT_GITHUB_TOKEN` secret in the repository settings. The Kill Switch phrase must appear verbatim in the `.agent.md` body instructions for the quality gate to work. Furthermore, you MUST explicitly define an **Escalation Trigger Taxonomy** in the `.agent.md` so the agent knows precisely when to halt and trigger the Kill Switch vs when to auto-approve.
- **CI/CD Official format agents**: After generation, run `gh aw compile` to generate the `.lock.yml` file. Commit **both** the `.md` and the `.lock.yml`. Requires the `gh-aw` extension: `gh extension install github/gh-aw`. Technical preview — may require preview access.
- **Both**: The shared `.agent.md` must satisfy both use cases — include the full instruction set AND (if Smart Failure) the Kill Switch phrase.


## See Also

- [[agent-scaffolders-create-github-action]]
- [[agent-scaffolders-create-github-action]]
- [[agent-harness-learning-layer-formerly-agentic-os]]
- [[agent-harness-summary]]
- [[os-health-check-sub-agent]]
- [[global-agent-kernel]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `spec-kitty-plugin/.agents/skills/create-agentic-workflow/references/agent-types.md`
- **Indexed:** 2026-04-17T06:42:09.756690+00:00
