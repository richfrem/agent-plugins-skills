---
concept: ai-environment-profile
source: plugin-code
source_file: agent-agentic-os/skills/os-environment-probe/SKILL.md
wiki_root: /Users/richardfremmerlid/Projects/agent-plugins-skills/.wiki
generated_at: 2026-04-27T05:21:03.706541+00:00
cluster: probe
content_hash: d9297360f7020210
---

# AI Environment Profile

> *Summary pending — run /wiki-distill*

## Key Ideas

- *(Bullets pending — run /wiki-distill)*

## Details

---
name: os-environment-probe
description: >
  Discovers and persists the user's available AI environments (Claude, Copilot CLI,
  Gemini CLI, Cursor, etc.) to context/memory/environment.md. Run once after OS setup
  or whenever the environment changes. os-architect and os-evolution-planner read this
  file to select the right delegation backend and cheapest brainstorm model automatically.
  Invoked by os-architect on first run if environment.md is absent.
model: inherit
color: cyan
tools: ["Bash", "Read", "Write"]
---

## Role

os-environment-probe asks the user which AI environments they have access to, then
verifies each claimed environment by running a lightweight probe command. Results are
written to `context/memory/environment.md` — a single source of truth that downstream
skills read to make delegation decisions without asking the user again.

---

## Environment Interview

Ask the user these questions (one prompt, multiple-choice, keep it brief):

> Which of these AI tools do you currently have active on this machine?
> (Select all that apply)
>
> A. Claude Code only
> B. Claude Code + GitHub Copilot CLI (Pro or Business plan)
> C. Claude Code + Gemini CLI (Google One AI or Workspace)
> D. Cursor (Claude or GPT backend)
> E. Other (describe)

Wait for their answer before probing.

---

## Probe Commands

For each claimed environment, verify it is actually callable:

| Environment | Probe command | Pass condition |
|-------------|---------------|----------------|
| Copilot CLI | `gh copilot explain "test" 2>&1 \| head -3` | No "not authenticated" or "command not found" |
| Gemini CLI | `gemini --version 2>&1 \| head -1` | Outputs a version string |
| Cursor | `cursor --version 2>&1 \| head -1` | Outputs a version string |
| Claude Code | always present | — |

Report each probe result to the user:
- Pass: "✓ Copilot CLI — confirmed"
- Fail: "✗ Copilot CLI — not found or not authenticated (skipping)"

Only write environments that pass to the profile.

---

## Output Format

Write `context/memory/environment.md`:

```markdown
# AI Environment Profile
_Last updated: YYYY-MM-DD_

## Available Environments

| Environment | Status | Free model | Premium model |
|-------------|--------|-----------|---------------|
| Claude Code | active | claude-haiku-4-5-20251001 | claude-sonnet-4-6 |
| Copilot CLI | active | gpt-4o-mini (free tier) | claude-sonnet-4.6 (via --model) |
| Gemini CLI  | active | gemini-flash-2.0 (free) | gemini-pro (paid) |

## Delegation Strategy

**Cheapest brainstorm model**: <first available in priority order below>
1. Copilot CLI free tier (gpt-4o-mini) — zero token cost
2. Gemini CLI free tier (gemini-flash-2.0) — zero token cost  
3. Claude Haiku subagent — low cost, in-session

**Primary dispatch model**: claude-sonnet-4-6 (via Copilot CLI if available, else Claude subagent)

## Capability Matrix

| Task | Best tool | Fallback |
|------|-----------|---------|
| Brainstorm options (cheap) | <cheapest model> | claude-haiku-4-5-20251001 |
| Single-file delegation | Copilot CLI | Claude subagent |
| Multi-workstream delegation | Copilot CLI claude-sonnet-4-6 | Claude subagent (sonnet) |
| Overnight unattended loop | os-improvement-loop | — |
```

---

## How Downstream Skills Use This

**os-evolution-planner** reads `environment.md` at the start of every run:
- If Copilot free tier available → brainstorm options using `gh copilot` (zero cost)
- If Gemini free tier available → brainstorm using `gemini --model flash`
- Otherwise → spawn Claude Haiku subagent for brainstorming

**os-architect** reads `environment.md` to choose the dispatch backend for Path B/C executions.

If `environment.md` is missing, both skills default to Claude-only mode and offer to run
os-environment-probe before proceeding.

---

## Re-probe

If the user adds a new environment later, they can run this skill again. It overwrites
`context/memory/environment.md` with fresh probe results.

---

## Smoke Test

1. After interview + probes, `

*(content truncated)*

## See Also

- [[1-configuration-setup-dynamic-from-profile]]

## Raw Source

- **Source:** `plugin-code`
- **File:** `agent-agentic-os/skills/os-environment-probe/SKILL.md`
- **Indexed:** 2026-04-27T05:21:03.706541+00:00
