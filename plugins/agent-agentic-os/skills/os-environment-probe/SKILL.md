---
name: os-environment-probe
plugin: agent-agentic-os
description: >
  Discovers and persists the user's available AI environments (Claude, Copilot CLI,
  Agy CLI, Cursor, etc.) to context/memory/environment.md. Run once after OS setup
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
> C. Claude Code + Agy CLI (Antigravity — gemini-3.5-flash backend)
> D. Cursor (Claude or GPT backend)
> E. Other (describe)

Wait for their answer before probing.

---

## Probe Commands

For each claimed environment, verify it is actually callable:

| Environment | Probe command | Pass condition |
|-------------|---------------|----------------|
| Copilot CLI | `gh copilot explain "test" 2>&1 \| head -3` | No "not authenticated" or "command not found" |
| Agy CLI | `agy --version 2>&1 \| head -1` | Outputs a version string |
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

| Environment | Status | Cheapest model | Premium model |
|-------------|--------|----------------|---------------|
| Claude Code | active | claude-haiku-4-5 | claude-sonnet-4-6 |
| Copilot CLI | active | gpt-5-mini | claude-sonnet-4.6 (via --model) |
| Agy CLI     | active | gemini-3.5-flash | — |

> Consult `references/cheapest_models.md` for current model names and costs — do not hardcode here.

## Delegation Strategy

**Cheapest brainstorm model**: <first available in priority order below>
1. Copilot CLI — gpt-5-mini (per-token, low cost)
2. Agy CLI — gemini-3.5-flash (per-token, low cost)
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
- If Copilot CLI available → brainstorm options using `run_agent.py --cli copilot` (gpt-5-mini, low cost)
- If Agy CLI available → brainstorm using `run_agent.py --cli agy` (gemini-3.5-flash, low cost)
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

1. After interview + probes, `context/memory/environment.md` exists and contains a
   populated `## Delegation Strategy` section with at least one "Cheapest brainstorm model" line.
2. Running the skill a second time overwrites the file (no duplicate rows).
3. If only Claude Code is confirmed, the file lists only Claude Code as active and sets
   "Cheapest brainstorm model: claude-haiku-4-5 (see references/cheapest_models.md)".

## Gotchas

- **Probe commands must be non-interactive**: use `--version`, `explain "test"`, or
  similar read-only flags — never trigger billing or start sessions.
- **User may not know model names**: ask about products (GitHub Copilot, Gemini), not
  model IDs. Map to model IDs internally.
- **Copilot CLI vs GitHub Copilot in IDE**: these are separate. Copilot CLI requires
  `gh extension install github/gh-copilot`. Confirm CLI specifically, not just Copilot.
- **No free tier**: Copilot and Agy bill per token as of June 2026. Only self-hosted `llama` (Gemma 4) is free. See `references/cheapest_models.md` for current costs.

---

## Support files

This skill now includes two convenience support files to make repro and re-probing easier. Inspect or run them from the skill directory (the agent may invoke them when safe):

- scripts/probe_environments.sh — a small, non-interactive shell probe that runs the same read-only commands listed above (agy --version, cursor --version, gh copilot explain "test") and prints a short summary. It is safe (non-billing) and tolerant of missing commands.

- references/gemini-detection-example.md — a short session-specific note showing an observed gemini probe result (example output captured during an interactive session). Use this as an example snippet when building or testing environment.md content.

Write any additional probe outputs to the references/ directory so downstream skills (os-architect, os-evolution-planner) can read concrete examples when deciding delegation.

