---
concept: copilot-sonnet-orchestration-brief
source: plugin-code
source_file: exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/design-artifacts/superpowers-copilot-sonnet-orchestration.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-17T06:42:09.574550+00:00
cluster: file
content_hash: c81186b5db34669f
---

# Copilot Sonnet Orchestration Brief

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

# Copilot Sonnet Orchestration Brief
**For:** Fresh Antigravity session (Claude Sonnet 4.6 Thinking)
**Date written:** 2026-04-06
**Cost model:** Copilot charges per REQUEST not per token.
**Strategy:** ONE single Copilot request generates ALL file content. Antigravity writes files, cleans up, and commits.

---

## Your Mission

You are a **Meta-Harness Orchestrator**. You dispatch ONE comprehensive Copilot CLI request
that generates all missing file content in a single shot. You then use your own file tools
to write every file, do the cleanup, and commit. You document learnings for the
`superpowers-analysis.md`.

**Copilot is used exactly ONCE.** All file writes, deletes, and git operations are done by
you (Antigravity) using your native tools. Do NOT make follow-up Copilot requests unless
the first one is critically incomplete (missing a whole file, not just minor edits).

---

## Repositories & Key Paths

| Item | Path |
|---|---|
| Plugin working dir | `/Users/richardfremmerlid/Projects/agent-plugins-skills/plugins/exploration-cycle-plugin/` |
| Full execution plan | `[plugin dir]/docs/superpowers/plans/2026-04-06-gap-fill-cleanup-attribution.md` |
| Copilot CLI skill | `/Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/SKILL.md` |
| superpowers analysis | `/Users/richardfremmerlid/Projects/AI-Research/01-Research/harnesses/superpowers/superpowers-analysis.md` |
| Opp 3 design plan | `/Users/richardfremmerlid/Projects/AI-Research/07-Opportunities/03-Exploration-and-Design/exploration-cycle-plugin-design-plan.md` |

---

## Step 0: Mandatory Pre-Flight (Before Any Copilot Call)

Read these files using your file tools (NOT shell commands):
1. Read the full plan: `[plugin dir]/docs/superpowers/plans/2026-04-06-gap-fill-cleanup-attribution.md`
2. Read the Copilot CLI skill: `/Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/SKILL.md`
3. Verify what files currently exist in `[plugin dir]/skills/` using `list_dir` tool

Then run the heartbeat check:
```bash
python /Users/richardfremmerlid/Projects/AI-Research/.agents/skills/copilot-cli-agent/scripts/run_agent.py \
  /dev/null /dev/null /tmp/heartbeat.md \
  "HEARTBEAT CHECK: Respond with 'HEARTBEAT_OK' only."
```
Verify `/tmp/heartbeat.md` contains `HEARTBEAT_OK` before proceeding.

---

## Step 1: THE ONE COPILOT REQUEST

Build a single prompt that generates ALL missing file content at once.
Write the prompt to a temp file first (avoids shell escaping issues):

```bash
cat > /tmp/copilot_prompt.md << 'PROMPT_EOF'
You are a senior agent skill author. Your task is to generate the complete file content
for 4 new/updated agent skill files. Output ALL files in one response, separated by
clearly marked headers so they can be parsed and written individually.

Use this exact output format for each file:

===FILE: [relative path from plugin root]===
[complete file content]
===ENDFILE===

---

## Context: What these skills are for

This is the `exploration-cycle-plugin` — an agentic plugin that guides non-technical
Subject Matter Experts (SMEs) through a structured discovery and prototyping workflow.
The plugin follows the GenAI Double Diamond framework. SME = business person, not a developer.

The plugin uses a HARD-GATE pattern from obra/superpowers (MIT license):
no prototype can be built until the SME approves a Discovery Plan.

Key persona rules for ALL skill content:
- Never use developer jargon: scaffold, repo, branch, commit, worktree, invoke, dispatch,
  iterate, initialize, spin up, phase, gate, spec, schema, subagent, context, tokens
- Use business language: "let me save that", "I'll take a note", "we'll build this together",
  "here's what I heard — does this look right?"
- Always confirm back to the SME in plain language before moving forward
- Ask ONE question at a time

---

## File 1: skills/discovery-planning/SKILL.md

YAML frontmatter (exactly):
```yaml
---
# Architectural patterns adapted from obra/superpowers 

*(content truncated)*

## See Also

- [[copilot-cli-plugin]]
- [[acceptance-criteria-copilot-cli-agent]]
- [[procedural-fallback-tree-copilot-cli-agent]]
- [[optimization-program-copilot-cli-agent]]
- [[option-15-sme-orchestrator-implementation---copilot-prompt]]
- [[copilot-proposer-prompt-exploration-cycle-plugin]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `exploration-cycle-plugin/assets/resources/design-thinking/03-Exploration-and-Design/design-artifacts/superpowers-copilot-sonnet-orchestration.md`
- **Indexed:** 2026-04-17T06:42:09.574550+00:00
